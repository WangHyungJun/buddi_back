import json
import logging
import pdb
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import hashers, login, logout
from django.contrib.auth.decorators import login_required
from django.core.serializers import serialize
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, HttpResponse, redirect
from django.views.generic import ListView
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView
from django.utils.decorators import method_decorator
from django.template import RequestContext
from . import models
from .forms import CreateUserForm, UploadForm, QuestionForm, CategoryForm, ContentForm, FriendSearchForm
from .models import Category, MyUser, Question, Answers
from haystack.generic_views import SearchView
from haystack.query import SearchQuerySet, EmptySearchQuerySet
from .mixins import Question_AjaxableResponseMixin, JSONResponseMixin
from rest_framework.generics import ListAPIView, CreateAPIView
from .serializers import QuestionSerializer, MyUserSerializer, AnswersSerializer, ShareQnASerializer, ShareAnswersSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView
from rest_framework.response import Response


logger = logging.getLogger(__name__)

# Create your views here.
def ip_address_processor(request):
  return {'ip_address': request.META['REMOTE_ADDR']}

def get_model_byurl(request, *args, **kwargs):
    return models.Question.objects.get(id=request.kwargs['question_text'])

def renewal_stars(request, *args, **kwargs):
    try:
        stars=models.stars.objects.filter(answers=request.POST['answer_id']).filter(owner=request.user.pk)[0]
    except:
        stars=models.stars()
        stars.owner=request.user
        stars.answers=models.Answers.objects.get(id=request.POST['answer_id'])
        stars.stars=1
        stars.save()
    else:
        if stars.stars<=20:
            stars.stars+=1
            stars.save()

def counting_stars(answer_pk):
    star_sum = 0
    for star_object in models.stars.objects.filter(answers=answer_pk):
        star_sum += star_object.stars
    return star_sum

def counting_metoo(question_pk):
    try:
        metoo_num=models.MeToo.objects.filter(Uncompli_question=question_pk)
    except:
        return 0
    else:
        return len(metoo_num)

@method_decorator(login_required(login_url='login'), name="dispatch")
class IndexView(Question_AjaxableResponseMixin):
    template_name = "cebula/alpha_ver2.html"
    form_class = QuestionForm

    def get_context_data(self, **kwargs):
        user = get_object_or_404(MyUser, username=self.request.user)
        interestCategory_list = models.Category.objects.filter(category_owner=user.pk).exclude(category_name='')

        question_list = Question.objects.all().order_by('-pub_date')  # question list
        question_list_user = []  # question owner list

        answer_list = []  # answer list
        answer_list_user = []  # answer owner list

        n = 0 # Start to make 'question_answer & owner' list

        while n < len(question_list):
            question_list_user.append(models.MyUser.objects.filter(id=question_list[n].owner_id)[0].username)
            answer_list.append(models.Answers.objects.filter(question_id=question_list[n].id).order_by('-pub_date'))
            answer_list_user.append(models.MyUser.objects.filter(id=answer_list[n][0].owner_id)[0].username)
            n += 1

        question_answer_list_user = zip(question_list, answer_list, question_list_user, answer_list_user)
        context = {'user': user, 'question_answer_list_user': question_answer_list_user,
                   'interestCategory_list': interestCategory_list, 'media_url': settings.MEDIA_URL}
        return context

# @receiver(user_signed_up)
# def populate_usermodel(sociallogin, user, **kwargs):
#     if sociallogin.account.provider=="google":
#         user_data = user.socialaccount_set.filter(provider='google')[0].extra_data
#         email = user_data['email']
#         username=user_data['name']
#
#         user.email = email
#         user.username = username
#         user.save()
#
#     if sociallogin.account.provider=="facebook":
#         user_data = user.socialaccount_set.filter(provider='facebook')[0].extra_data
#         email=user_data['email']
#         username=user_data['name']

class CreateUserView(CreateView):
    form_class = CreateUserForm
    template_name = "registration/signup.html"
    success_url = "login"

    def form_invalid(self, form):
        if form.errors['password2'][0]=="비밀번호가 일치하지 않습니다.":
            context={'message': form.errors['password2'][0]}
            return render(self.request, "registration/signup.html", context)

        elif form.errors['password2'][0]=='비밀번호가 너무 짧습니다. 최소 8 문자를 포함해야 합니다.':
            context = {'message': form.errors['password2'][0]}
            return render(self.request, "registration/signup.html", context)

        elif form.errors['username']:
            username=form.data['username']
            context = {'message': "Username %s is already exists" % username}
            return render(self.request, "registration/signup.html", context)

        else:
            context = {'message': "Please fill in all informations"}
            return render(self.request, 'registration/signup.html', context)

    def form_valid(self, form):
        email = form.cleaned_data['email']
        try:
            MyUser.objects.filter(email__exact=email)[0]
        except IndexError:
            form.save()
            return self.success_url
        else:
            messages.error(self.request, "Email %s is already exists" % email)
            return render(self.request, "registration/signup.html")


class LogIn(TemplateView):
    template_name = "registration/login.html"

    def post(self, request):
        try:
            u=MyUser.objects.filter(username__exact=request.POST['Username'])[0]
        except IndexError:
            messages.error(request, 'Incorrect user id')
            return render(request, "error/error.html")
        if hashers.check_password(request.POST['password'],u.password):
            login(request, u, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('cebula:index')
        else:
            messages.error(request,'Incorrect password')
            return render(request, 'error/error.html')


def LogOut(request):
    logout(request)
    return render(request, 'registration/logged_out.html')


class RegisteredView(TemplateView):
    template_name = 'registration/signup_done.html'


class Waiting(CreateView):
    template_name = "cebula/alpha_waiting.html"
    form_class = UploadForm

    def get_context_data(self, **kwargs):
        user = get_object_or_404(MyUser, pk=self.request.user.pk)
        pk = models.Question.objects.filter(question_text__exact=self.kwargs['question_text'].replace("-", " "))[0].pk
        each_category_list = models.Category.objects.filter(category_owner=user).exclude(category_name='')
        categories = each_category_list.exclude(parentId__isnull=False)
        question = models.Question.objects.filter(id=pk)
        photo_list = models.Answers.objects.filter(question=pk)

        n = 0
        answer_category_list = []
        while n < len(photo_list):
            answer_category_list.append(models.Category.objects.filter(id=photo_list[n].category_id)[0].category_name)
            n += 1
        photo_and_answer = zip(photo_list, answer_category_list)
        context = {'question': question, 'photo_and_answer': photo_and_answer, 'user': user, 'answer_category_list': answer_category_list,
                   'each_category_list': each_category_list,'categories': categories}
        return context

    def form_valid(self, form):
        post=form.save(commit=False)
        post.owner=self.request.user

        if form.data['answerCategory']=='':
            category="Answered Contents"
            try:
                c_previous = models.Category.objects.filter(category_owner=self.request.user.pk).filter(category_name__exact=category)[0]
            except IndexError:
                c_form = CategoryForm({'category_name': category})
                c_post = c_form.save(commit=False)
                c_post.category_owner = self.request.user
                c_post.save()
                post.category = c_post
                post.save()
            else:
                post.category = c_previous
                post.save()

        else:
            category = form.data['answerCategory']
            try:
                c_previous = models.Category.objects.filter(category_owner=self.request.user.pk).filter(category_name__exact=category)[0]
            except IndexError:
                c_form = CategoryForm({'category_name': category})
                c_post = c_form.save(commit=False)
                c_post.category_owner = self.request.user
                c_post.save()
                post.category = c_post
                post.save()
            else:
                post.category = c_previous
                post.save()

        return  JsonResponse({'message': "Submit Success"})

    def form_invalid(self, form):
        return JsonResponse({'message': "Submit Failed"})

    '''
    def ajax_response(self):
        stars 1로 받음
        1이면 Stars pk 꽂은 뒤 원래 데이터에서 +1
        다시 contents 별로 filter 작업 거친 뒤
        for 구문 돌려서 좋아요 개수 더한 뒤
        ajax로 반환
        지금 당장은 그냥 post로 받음. 사실 큰 문제 없음.
    '''

    def post(self, *args, **kwargs):
        if self.request.POST['divider']=="Share_Page":
            question_model=get_model_byurl(self)
            try:
                models.Share_QandA.objects.filter(questions=question_model.pk).filter(owner=self.request.user)
            except:
                share=models.Share_QandA()
                share.owner=self.request.user
                share.questions=question_model
                share.save()
                return HttpResponse({'messages': "Keep!"})
            else:
                return HttpResponse({"messages": "이미함!"})

        if self.request.POST['divider']=="Share_contents":
            try:
                models.Share_Answers.objects.filter(contents=self.request.POST['answer_id']).filter(owner=self.request.user)
            except:
                share = models.Share_Answers()
                share.owner = self.request.user
                share.contents= models.Answers.objects.get(id=self.request.POST['answer_id'])
                share.save()

                return HttpResponse({'messages': "Keep!"})
            else:
                return HttpResponse({"messages": "이미함!"})

        if self.request.POST['divider']=="Likes":
            renewal_stars(self.request)
            sum_stars=counting_stars(self.request.POST['answer_id'])
            return JsonResponse({"stars": sum_stars})


class QuestionApiView(ListAPIView):
    serializer_class = QuestionSerializer
    queryset = Question.objects.order_by('-pub_date')



class QuestionView(ListView):
    template_name = 'cebula/alpha_question.html'
    context_object_name = 'context'

    def get_queryset(self):
        metoo_num=[]
        question_object_list=models.Question.objects.order_by('-pub_date')
        for question_object in question_object_list:
            metoo_num.append(counting_metoo(question_object.pk))
        context=zip(metoo_num, question_object_list)
        return context

    def post(self, *args, **kwargs):
        if self.request.POST['divider']=="MeToo":
            question_pk=self.request.POST['pk']
            try:
                models.MeToo.objects.filter(Uncompli_question=question_pk).filter(owner=self.request.user.pk)[0]
            except:
                metoo=models.MeToo()
                metoo.owner=self.request.user
                metoo.Uncompli_question=models.Question.objects.get(id=question_pk)
                metoo.save()
                return JsonResponse({"message": "Success as it is always", "data": counting_metoo(question_pk)})
            else:
                return JsonResponse({"message": "Already Clicked"})


class Category(TemplateView):
    template_name = "cebula/alpha_category.html"

    def get_context_data(self, **kwargs):
        context=super(Category, self).get_context_data()
        c_rep=kwargs['category'].replace("-", " ")
        user=get_object_or_404(MyUser, username=kwargs['username'])
        category_model = models.Category.objects.filter(category_owner=user.pk).filter(category_name__exact=c_rep)[0]

        sub_category = models.Category.objects.filter(parentId=category_model.pk)
        sub_category_json = json.dumps(serialize("json", sub_category, fields=('category_name')))
        photo_list_answer = models.Answers.objects.filter(category=category_model.pk)
        photo_list_individual=models.Content.objects.filter(category=category_model.pk)

        context.update({'profile_user': user, 'photo_list_answer': photo_list_answer, 'photo_list_individual': photo_list_individual, 'c_rep': c_rep,
                        'category': kwargs['category'],'sub_category': sub_category, 'sub_category_json': sub_category_json, 'username': kwargs['username'],
                        'category_model': category_model, 'owner_id': user.pk})
        return context

    def post(self, request, **kwargs):
        context=self.get_context_data(**kwargs)
        category_model=context['category_model']
        user=context['profile_user']

        if request.POST['sub_category']!='' and request.FILES=={}:
            c=models.Category()
            c.category_name=request.POST['sub_category']
            c.parentId=category_model
            c.category_owner=user
            c.save()

        #sub_category는 만들지 않고 상위 카테고리에 새로운 콘텐츠를 추가하고 싶은 경우
        elif request.POST['sub_category']=='' and request.FILES!={}:
            form=ContentForm({'owner': user.pk}, request.FILES)
            if form.is_valid():
                post=form.save(commit=False)
                post.category=context['category_model']
                post.save()

        #그냥 아무것도 하지 않은 경우
        elif request.POST['sub_category']=='' and request.FILES=={}:
            return HttpResponse('')

        #이미지와 sub_category 모두 새롭게 생성한 경우
        else:
            form=ContentForm({'owner': user.pk},request.FILES)
            if form.is_valid():
                temp=models.Category()
                temp.category_name=request.POST['sub_category']
                temp.parentId=category_model
                temp.category_owner=user
                temp.save()
                post=form.save(commit=False)
                post.category=temp
                post.save()

                return  HttpResponse('')

        return HttpResponse('')


def UserPage(request,username):
    user = get_object_or_404(MyUser, username=username)
    if request.method=="GET":

        following= len(models.Following_Follower.objects.filter(user=user.pk))
        follower= len(models.Following_Follower.objects.filter(following=user.pk))

        is_following = 1
        try :
            models.Following_Follower.objects.filter(user=request.user.pk).filter(following=user.pk)[0]
        except IndexError:
            is_following = 0

        photo_list = models.Answers.objects.filter(owner=user.pk)

        category = models.Category.objects.filter(category_owner=user.pk)#.exclude(category_name__isnull=True).exclude(category_name__exact='')
        category_json = json.dumps(serialize("json", category, fields=('category_name')))

        galaxy_num=models.MyUser.objects.filter(id=user.pk)[0].galaxy_num
        galaxy_num_list = []

        for i in range(0, galaxy_num):
            galaxy_num_list.append(i)

        onoff =models.MyUser.objects.filter(username=username)[0].onoff
        latest_question_list= models.Question.objects.order_by('-pub_date')
        answer_list_for_question = []

        for i in latest_question_list :
            answer_list_for_question.append(models.Answers.objects.filter(question_id=i.id))

        latest_question_and_answer_list = zip(latest_question_list, answer_list_for_question)
        context = {'profile_user': user, 'photo_list': photo_list, 'category': category, 'category_json': category_json,
                   'latest_question_and_answer_list': latest_question_and_answer_list, 'galaxy_num_list': galaxy_num_list,
                   'galaxy_num': galaxy_num, 'onoff': onoff, 'following': following, 'follower': follower, 'is_following': is_following}

        return render(request, "cebula/alpha_userpage_answer.html", context)


    if request.POST['divider']=="click_follower":
        request_user= models.MyUser.objects.filter(username=request.POST['request_user'])[0].pk

        if request.POST.get('add_follower') :
            try:
                temp=models.Following_Follower.objects.filter(user=request.user.pk).filter(following=user.pk)[0]
            except IndexError:
                f=models.Following_Follower()
                f.user_id=request_user
                f.following=user
                f.save()
                return HttpResponse(len(models.Following_Follower.objects.filter(following=user.pk))) #After adding the following +1, response the number of all of following.
            else :
                return HttpResponse('')
        elif request.POST.get('cancle_follower') :
            temp=models.Following_Follower.objects.filter(user_id=request_user).filter(following=user)[0]
            temp.delete()
            return HttpResponse(len(models.Following_Follower.objects.filter(following=user.pk))) #After canceling the following -1, response the number of all of following.
        return HttpResponse('')

    if request.POST['divider']=="add_galaxy":

        on = request.POST['on']
        new_galaxy_num=request.POST['galaxy_num']
        temp=models.MyUser.objects.filter(id=user.pk)[0]
        temp.onoff=on
        temp.galaxy_num=new_galaxy_num
        temp.save()

        context = {'likes': new_galaxy_num}

        return JsonResponse(context)

    if request.POST['divider']=="remove_galaxy":
        new_galaxy_num=request.POST['galaxy_num']
        temp=models.MyUser.objects.filter(id=user.pk)[0]
        temp.galaxy_num=new_galaxy_num
        temp.save()

        context = {'likes': new_galaxy_num}

        return JsonResponse(context)

    if request.POST['divider']=="origin_default_Category":
        originCategoryList_json = request.POST.get('originCategoryList_json')
        originCategoryList = json.loads(originCategoryList_json)

        for i in originCategoryList['0'] :
            g=models.Category()
            g.category_name=i
            g.category_owner=user
            g.save()
        off = request.POST['off']
        temp=models.MyUser.objects.filter(id=user.pk)[0]
        temp.onoff=off
        temp.save()
        return HttpResponse('')

    if request.POST['divider']=="default_Category":
        initCategoryList_json = request.POST.get('initCategoryList_json')
        initCategoryList = json.loads(initCategoryList_json)
        emptyCategoryId_obj = {}
        emptyCategoryId = []
        for i in initCategoryList['0'] :
            g=models.Category()
            g.category_name=i
            g.category_owner=user
            g.save()
            emptyCategoryId.append(g.id)
        emptyCategoryId_obj[0] = emptyCategoryId

        off = request.POST['off']
        temp=models.MyUser.objects.filter(id=user.pk)[0]
        temp.onoff=off
        temp.save()
        return JsonResponse(emptyCategoryId_obj)

    #중복 카테고리 입력시 경고창 혹은 하나로 자동적으로 합치도록 설계
    if request.POST['divider']=="modify_Category":
        category = request.POST['category']
        previousCategory = request.POST['previousCategory']
        order = int(request.POST['order'])

        if previousCategory == '' :
            temp = models.Category.objects.filter(category_owner=user.pk).filter(category_name=previousCategory)[order]
            temp.category_name=category
            temp.save()

        else :
            temp = models.Category.objects.filter(category_owner=user.pk).filter(category_name=previousCategory)[0]
            temp.category_name=category
            temp.save()

        return HttpResponse('')


def UserPage_answer(request,username):
    user = get_object_or_404(MyUser, username=username)
    pk=user.pk
    following= len(models.Following_Follower.objects.filter(user=user.pk))
    follower= len(models.Following_Follower.objects.filter(following=user.pk))

    is_following = 1
    try :
        models.Following_Follower.objects.filter(user=request.user.pk).filter(following=user.pk)[0]
    except IndexError:
        is_following = 0

    photo_list = models.Answers.objects.filter(owner=user.pk)

    category = models.Category.objects.filter(category_owner=user.pk)#.exclude(category_name__isnull=True).exclude(category_name__exact='')
    category_json = json.dumps(serialize("json", category, fields=('category_name')))

    galaxy_num=models.MyUser.objects.filter(id=user.pk)[0].galaxy_num
    galaxy_num_list = []
    for i in range(0, galaxy_num):
        galaxy_num_list.append(i)

    onoff =models.MyUser.objects.filter(username=username)[0].onoff
    latest_question_list= models.Question.objects.order_by('-pub_date')[:20]

    return render(request, "cebula/alpha_userpage_answer.html", {'profile_user': user, 'photo_list': photo_list, 'category': category, 'category_json': category_json, 'latest_question_list': latest_question_list,
            'galaxy_num_list': galaxy_num_list, 'galaxy_num': galaxy_num, 'onoff': onoff, 'pk': pk,
            'following': following, 'follower': follower, 'is_following': is_following})


class UserPage_MyQuestion(TemplateView):
    template_name = "cebula/alpha_userpage_question.html"

    def get_context_data(self, **kwargs):
        user = get_object_or_404(MyUser, username=kwargs['username'])
        pk=user.pk
        following = len(models.Following_Follower.objects.filter(user=user.pk))
        follower = len(models.Following_Follower.objects.filter(following=user.pk))

        is_following = 1
        try:
            models.Following_Follower.objects.filter(user=self.request.user.pk).filter(following=user.pk)[0]
        except IndexError:
            is_following = 0

        myQuestion_list = models.Question.objects.filter(owner_id=user.pk).order_by('-pub_date')
        someone_answer_for_myQuestion = []

        for i in myQuestion_list:
            someone_answer_for_myQuestion.append(models.Answers.objects.filter(question_id=i.id).order_by('-pub_date'))

        myQuestion_and_answer_list = zip(myQuestion_list, someone_answer_for_myQuestion)

        context = {'profile_user': user, 'following': following, 'follower': follower, 'pk': pk, 
        'is_following': is_following, 'myQuestion_and_answer_list': myQuestion_and_answer_list}
        return context


def UserPage_sharedQuestion(request,username):
    user = get_object_or_404(MyUser, username=username)
    following= len(models.Following_Follower.objects.filter(user=user.pk))
    follower= len(models.Following_Follower.objects.filter(following=user.pk))

    is_following = 1
    try :
        models.Following_Follower.objects.filter(user=request.user.pk).filter(following=user.pk)[0]
    except IndexError:
        is_following = 0

    photo_list = models.Answers.objects.filter(owner=user.pk)

    category = models.Category.objects.filter(category_owner=user.pk)#.exclude(category_name__isnull=True).exclude(category_name__exact='')
    category_json = json.dumps(serialize("json", category, fields=('category_name')))

    galaxy_num=models.MyUser.objects.filter(id=user.pk)[0].galaxy_num
    galaxy_num_list = []
    for i in range(0, galaxy_num):
        galaxy_num_list.append(i)

    onoff =models.MyUser.objects.filter(username=username)[0].onoff
    latest_question_list= models.Question.objects.filter(owner_id=user.pk).order_by('-pub_date')

    return render(request, "cebula/alpha_userpage_shared_question.html", {'profile_user': user,
        'photo_list': photo_list, 'category': category, 'category_json': category_json,
        'latest_question_list': latest_question_list, 'galaxy_num_list': galaxy_num_list, 'galaxy_num': galaxy_num,
        'onoff': onoff, 'following': following, 'follower': follower, 'is_following': is_following})


def UserPage_post(request,username):
    user = get_object_or_404(MyUser, username=username)
    following= len(models.Following_Follower.objects.filter(user=user.pk))
    follower= len(models.Following_Follower.objects.filter(following=user.pk))

    is_following = 1
    try :
        models.Following_Follower.objects.filter(user=request.user.pk).filter(following=user.pk)[0]
    except IndexError:
        is_following = 0

    photo_list = models.Answers.objects.filter(owner=user.pk)

    category = models.Category.objects.filter(category_owner=user.pk)#.exclude(category_name__isnull=True).exclude(category_name__exact='')
    category_json = json.dumps(serialize("json", category, fields=('category_name')))

    galaxy_num=models.MyUser.objects.filter(id=user.pk)[0].galaxy_num
    galaxy_num_list = []
    for i in range(0, galaxy_num):
        galaxy_num_list.append(i)

    onoff =models.MyUser.objects.filter(username=username)[0].onoff
    latest_question_list= models.Question.objects.order_by('-pub_date')[:20]

    return render(request, "cebula/alpha_userpage_post.html", {'profile_user': user, 'photo_list': photo_list, 'category': category, 'category_json': category_json, 'latest_question_list': latest_question_list,
            'galaxy_num_list': galaxy_num_list, 'galaxy_num': galaxy_num, 'onoff': onoff, 'following': following, 'follower': follower, 'is_following': is_following})


def UserPage_Previous(request,username):
    user = get_object_or_404(MyUser, username=username)
    request_user=request.user
    if request.method=="GET":
     photo_list = models.Answers.objects.filter(owner=user.pk)
     category = models.Category.objects.filter(category_owner=user.pk).exclude(category_name__isnull=True).\
         exclude(category_name__exact='').exclude(parentId__isnull=False)
     category_json = json.dumps(serialize("json", category, fields=('category_name')))
     following=len(models.Following_Follower.objects.filter(user=user.pk))
     follower = len(models.Following_Follower.objects.filter(following=user.pk))
     galaxy_num=models.MyUser.objects.filter(id=user.pk)[0].galaxy_num
     galaxy_num_list = []

     for i in range(0, galaxy_num):
         galaxy_num_list.append(i)

     context = {'profile_user': user, 'photo_list': photo_list, 'category': category, 'category_json': category_json,
                'galaxy_num_list': galaxy_num_list, 'galayx_num': galaxy_num, 'following': following, 'follower': follower,
                'request_user': request_user}

     return render(request, "cebula/alpha_userpage.html", context)

    #star_cluster//remove_cluster 전부 다 나의 페이지가 아닌 이상 클릭할 수 없도록 설계해라! Category 편집도 마찬가지!

    if request.POST['divider']=="add_galaxy":
        new_galaxy_num=request.POST['galaxy_num']
        temp=models.MyUser.objects.filter(id=user.pk)[0]
        temp.galaxy_num=new_galaxy_num
        temp.save()

        context = {'likes': new_galaxy_num}

        return JsonResponse(context)

    if request.POST['divider']=="remove_galaxy":
        new_galaxy_num=request.POST['galaxy_num']
        temp=models.MyUser.objects.filter(id=user.pk)[0]
        temp.galaxy_num=new_galaxy_num
        temp.save()

        context = {'likes': new_galaxy_num}

        return JsonResponse(context)

    #중복 카테고리 입력시 경고창 혹은 하나로 자동적으로 합치도록 설계
    if request.POST['divider']=="modify_Category":
        category = request.POST['category']
        previousCategory = request.POST['previousCategory'].split('\n')[0]

        if previousCategory=='':
            try:
                overlapcheck=models.Category.objects.filter(category_owner=user.pk).\
                    filter(category_name__exact=category).exclude(parentId__isnull=False)[0]
            except IndexError:
                c=Category()
                c.category_name=category
                c.category_owner=user
                c.save()

                return JsonResponse({'category': category})

            else:
                response = JsonResponse({"error": "이미 존재하는 카테고리입니다."})
                response.status_code = 403  # To announce that the user isn't allowed to publish
                return response

        try:
            overlapcheck=models.Category.objects.filter(category_owner=user.pk).\
                filter(category_name__exact=category).exclude(parentId__isnull=False)[0]
        except IndexError:
            temp = models.Category.objects.filter(category_owner=user.pk).filter(category_name__exact=previousCategory)[0]
            temp.category_name = category
            temp.save()

            return JsonResponse({'category': category})
        else:
            response = JsonResponse({"error": "이미 존재하는 카테고리입니다."})
            response.status_code = 403  # To announce that the user isn't allowed to publish
            return response

    #다른 사람의 페이지가 아닌 마이페이지를 볼 경우에는 follower 버튼이 아예 없도록 설계하는 것이 옳음.
    if request.POST['divider']=="add_follower":
        follower_num=request.POST['add_follower']
        try:
            temp=models.Following_Follower.objects.filter(user=request.user.pk).filter(following=user.pk)[0]
        except IndexError:
            f=models.Following_Follower()
            f.user=request_user
            f.following=user
            f.save()

            follower = len(models.Following_Follower.objects.filter(following=user.pk))
            context={'follower_num': follower}
            return JsonResponse(context)
        else:
            context={'messages': "이미 팔로워 했습니다."}
            return JsonResponse(context)

    if request.POST['divider'] == "modify_Username":
        user.username=request.POST['Username']
        user.save()

        context={'Username': request.POST['Username']}

        return JsonResponse(context)


class following(ListView):
    template_name = "cebula/alpha_followings.html"
    context_object_name = "following_list"

    #지금 당장은 username으로 필터링하고 username을 불러왔지만 나중에는 username이 아닌 아이디나 이메일로 필터링 후, username을 불러와야 한다.
    def get_queryset(self):
        user=get_object_or_404(MyUser, username=self.kwargs['username'])
        return models.Following_Follower.objects.filter(user=user.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['User'] = self.kwargs['username']
        return context


class follower(ListView):
    template_name = "cebula/alpha_followers.html"
    context_object_name = "follower_list"

    #지금 당장은 username으로 필터링하고 username을 불러왔지만 나중에는 username이 아닌 아이디나 이메일로 필터링 후, username을 불러와야 한다.
    #즉, User를 *유일* 식별자가 필요하다. Username은 겹칠 때가 많아 한계가 있음!!
    def get_queryset(self):
        user=get_object_or_404(MyUser, username=self.kwargs['username'])
        return models.Following_Follower.objects.filter(following=user.pk)

    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        context['User']=self.kwargs['username']
        return context

class Sub_Category(ListView):
    template_name='cebula/alpha_sub_category.html'
    context_object_name = "subcategory_contents"

    def get_queryset(self):
        user = get_object_or_404(MyUser, username=self.kwargs['username'])
        category=self.kwargs['category'].replace("-", " ")
        category_model=Category.objects.filter(category_owner=user.pk).filter(category_name__exact=category)[0]
        sub_category=self.kwargs['sub_category'].replace("-"," ")
        try:
            sub_category_model=models.Category.objects.filter(parentId=category_model.pk).filter(category_name=sub_category)[0]
            photo_list = models.Content.objects.filter(category=sub_category_model.pk)
        except IndexError:
            return JsonResponse({'message': "Please Add your galaxy"})
        else:
            return photo_list

# def search_test(request):
#     users=SearchQuerySet().autocomplete(content_auto=)
#
#
#     # if request.method=="GET":
#     #     search_text=''
#     # else:
#     #     search_text=request.POST['search_text']
#     # users=MyUser.objects.filter(username__contains=search_text)
#     context={"users": users}
#     return render(request, 'search/search.html', context)


class FriendSearch(SearchView, JSONResponseMixin):
    # template_name = "search/friend_search.html"
    # form_class = DateRangeSearchForm... search form이 필요할까? request.get에서 얻은 Data로 필터링할 것이니 필요 없을 듯.
    # sqs=SearchQuerySet().models(MyUser).all() #MyUser model로 filtering하겠다.
    query=""
    results = EmptySearchQuerySet()
    load_all = True
    # form_class = FriendSearchForm
    context_object_name = 'context'
    form_name = "form"

    def get_queryset(self):
        # queryset = super().get_queryset()

        if self.request.GET.get('q'):
            keyword=self.request.GET['q']
            sqs=SearchQuerySet().models(MyUser, models.Question).filter(username__contains=keyword)
            return sqs
        else:
            pass
        return ''

    #context data를 FRONT에 보낸다.
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        if self.request.GET.get('q') is None:
            context['users']=MyUser.objects.get(id=self.request.user.pk)
            return context

        #검색어는 입력했으나 그 형식이 유효하지 않은 경우
        elif not FriendSearchForm(self.request.GET.get('q')).is_valid:
            context={'message': "You search has some errors"}
            return context
        #검색어 형식이 유효한 경우
        else:
            query = self.request.GET.get('q')
            sqs = SearchQuerySet().models(MyUser).filter(text__contains=query)
            context['query'] = query
            context['results'] = sqs
            pdb.set_trace()
            return context

    def render_to_response(self, context, **response_kwargs):

        if self.request.is_ajax():
            sqs = SearchQuerySet().autocomplete(content_auto=self.request.GET.get('q', ''))[:5]
            suggestions = [result.username for result in sqs]

            # Make sure you return a JSON object, not a bare list.
            # Otherwise, you could be vulnerable to an XSS attack.

            context={'results': suggestions}

            return JsonResponse(context, safe=False)

        return render(self.request, 'search/friend_search.html')

class Test(TemplateView):
    template_name="cebula/test.html"

    def get_context_data(self):
        context=super(TemplateView, self).get_context_data()
        context['username']="HyungJun"

        return context

    
class Setting(UpdateView):
    template_name = "cebula/alpha_setting.html"
    fields=['username', 'email', 'password']

    def get_object(self):
        return get_object_or_404(MyUser, username=self.kwargs['username'])

    def get_context_data(self):
        context=super(UpdateView,self).get_context_data()
        context['username']=self.kwargs['username']

        return context


class SettingAPIView(APIView):

    renderer_classes = (JSONRenderer, )

    def get(self, request, username):
        user=get_object_or_404(MyUser, username=username)
        content = {'user': user.username, 'greeting': "Hello API WORLD"}
        return Response(content)


class Custom_MyUserAPIView(ListAPIView):
    serializer_class=MyUserSerializer
    
    def get_queryset(self):
        queryset=MyUser.objects.filter(id=self.kwargs['pk'])

        return queryset


class Custom_QuestionAPIView(ListAPIView):
    serializer_class=QuestionSerializer

    def get_queryset(self):
        queryset=Question.objects.filter(owner_id=self.kwargs['pk'])

        return queryset


class All_QuestionAPIView(ListAPIView):
    serializer_class=QuestionSerializer
    queryset=Question.objects.all()


class All_AnswersAPIView(ListAPIView):
    serializer_class=AnswersSerializer
    queryset=Answers.objects.all()


class Userpage_Answer(TemplateView):
    template_name = "cebula/alpha_userpage_answer.html"

    def get_context_data(self, **kwargs):
        context=super(TemplateView, self).get_cotext_data()
        context['pk']=get_object_or_404(MyUser, username=self.kwargs['username']).pk
        return context


class Userpage_Question(TemplateView):
    template_name = "cebula/alpha_userpage_question.html"

    def get_context_data(self, **kwargs):
        context = super(TemplateView, self).get_cotext_data()
        context['pk'] = get_object_or_404(MyUser, username=self.kwargs['username']).pk
        return context


class UserPageAPIView(APIView):
    renderer_classes=(JSONRenderer,)

    #userpage/answer 부분
    def get(self, request, username):
        user=get_object_or_404(MyUser, username=username)
        all_categories_list=[]
        category_object=models.Category.objects.filter(category_owner=user.pk).exclude(parentId__isnull=False)

        for i in range(0,(len(category_object)//6+1)):
            temp_objects=category_object[6*i:6*(i+1)]
            temp_dic={}
            j=0

            for object in temp_objects:   
                if object.category_name=="":
                    temp_dic[j]=""
                else:
                    temp_list=[]
                    for sub_object in models.Category.objects.filter(parentId=object.pk):
                        temp_list.append(sub_object.category_name)
                    temp_dic[object.category_name]=temp_list
                j+=1
                    
            all_categories_list.append(temp_dic)
                
        return Response(all_categories_list)

class MainPageAPIView(APIView, MyUserSerializer):
    renderer_classes = (JSONRenderer,)

    def get(self, request):
        main_lst=[]
        for question_object in models.Question.objects.all():
            try:
                answer_object=models.Answers.objects.filter(question_id=question_object.pk)[0]
            except:
                pass
            else:
                temp={}
                temp['question_text']=question_object.question_text
                temp['question_owner']=question_object.owner.username
                temp['answer_image']="127.0.0.1:8000"+answer_object.answerimage.url
                temp['answer_owner']=answer_object.owner.username
                main_lst.append(temp)

        return Response(main_lst)

    def post(self, request):
        instance=models.Question.objects.get(id=request.data['id'])
        instance.question_text=request.data['question_text']
        pdb.set_trace()
        instance.save()

        return Response('success')


class WaitingAPIView(APIView):
    renderer_classes = (JSONRenderer,)

    def get(self, *args,**kwargs):
        lst=[]
        temp={}
        answers_lst=models.Answers.objects.filter(question=self.kwargs['pk'])
        for answer in answers_lst:
            temp['answer_owner']=answer.owner.username
            temp['answer_image']="127.0.0.1:8000"+answer.answerimage.url
            star_sum=counting_stars(answer.pk)
            temp['stars']=star_sum
            lst.append(temp)
        return Response(temp)


class ShareQnAAPIView(ListAPIView):
    serializer_class = ShareQnASerializer

    def get_queryset(self):
        queryset=models.Share_QandA.objects.filter(owner=self.kwargs['pk'])
        return queryset


class ShareAnswersAPIView(ListAPIView):
    serializer_class = ShareAnswersSerializer

    def get_object  (self):
        queryset = models.Share_Answers.objects.filter(owner=self.kwargs['pk'])
        return queryset





