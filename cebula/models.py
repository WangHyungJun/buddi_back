from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.contrib.auth.models import User

def user_path(instance,filename):
    from random import choice
    import string
    arr=[choice(string.ascii_letters) for _ in range(8)]
    pid=''.join(arr)
    extension=filename.split('.')[-1]
    return '%s/%s.%s' % (instance.owner.username,pid,extension)

class Photo(models.Model):
    image=models.ImageField(upload_to=user_path)
    owner=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=None)
    comment=models.CharField(max_length=255)
    pub_date=models.DateTimeField(auto_now_add=True)
    category=models.CharField(blank=True,max_length=255)

# Create your models here.
class Question(models.Model):
    owner=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=None)
    question_text=models.CharField(max_length=400)
    question_specific=models.CharField(blank=True, max_length=1000)
    question_tags=models.CharField(blank=True, max_length=500)
    pub_date=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question_text

class Category(models.Model):
    category_owner=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category_name=models.CharField(max_length=100, blank=True)
    parentId = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)
    # image = models.ImageField(upload_to=user_path, blank=True, null=True)

    def __str__(self):
        return self.category_name

class Content(models.Model):
    owner=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category=models.ForeignKey(Category, on_delete=models.CASCADE)
    content=models.ImageField(upload_to=user_path)


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=None)
    profile_photo = models.ImageField(blank=True)
    nickname = models.CharField(max_length=64)
    comment=models.CharField(max_length=400)


class MyUser(AbstractUser):
    galaxy_num=models.IntegerField(default=1)
    onoff=models.IntegerField(default=1, null=True)

    def __str__(self):
        return self.username


#on_delete는 뭘까? unique의 기능은? symmetrical은?
class Following_Follower(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user")
    following=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=None, related_name="following")


# class Sub_Category(models.Model):
#     upper_category=models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
#     sub_category_name=models.CharField(max_length=100)


# class Individual_Contents(models.Model):
#     owner=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
#     category=models.ForeignKey(Category, on_delete=None)
#     sub_category=models.ForeignKey(Sub_Category, on_delete=None, null=True, blank=True)
#     content=models.ImageField(upload_to=user_path, null=True)


class Answers(models.Model):
    owner=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=None)
    comment=models.CharField(max_length=100, blank=True)
    answerimage=models.ImageField(upload_to=user_path)
    question=models.ForeignKey(Question,on_delete='CASCADE')
    pub_date=models.DateTimeField(auto_now_add=True)
    category=models.ForeignKey(Category, on_delete="CASCADE", related_name="Answer_category_name")
    # sub_category=models.ForeignKey(Sub_Category, on_delete=None, null=True)


class stars(models.Model):
    owner=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stars=models.IntegerField(default=0)
    answers=models.ForeignKey(Answers, on_delete=models.CASCADE)


class Share_QandA(models.Model):
    owner=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    questions=models.ForeignKey(Question, on_delete=models.CASCADE)


class Share_Answers(models.Model):
    owner=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    answers=models.ForeignKey(Answers, on_delete=models.CASCADE)


class MeToo(models.Model):
    owner=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    Uncompli_question=models.ForeignKey(Question, on_delete=models.CASCADE) #공감은 미완성된 질문에 한해서만 허용하겠다.