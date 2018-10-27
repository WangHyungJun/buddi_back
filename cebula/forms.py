from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import Photo, Answers, Profile, Question, Category, MyUser, Content
from haystack.forms import SearchForm

class CreateUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = MyUser
        fields = ("first_name","last_name","username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(CreateUserForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

class QuestionForm(forms.ModelForm):
    class Meta:
        model=Question
        fields={'question_text','question_specific','question_tags'}

class UploadForm(forms.ModelForm):

    class Meta:
        model=Answers
        fields={'answerimage', 'question'}

class ProfileForm(forms.ModelForm):
    class Meta:
        model=Profile
        fields=("nickname","comment","profile_photo")

class CategoryForm(forms.ModelForm):
    class Meta:
        model=Category
        fields=("category_name",)

class ContentForm(forms.ModelForm):
    class Meta:
        model=Content
        fields=('owner', 'content', )


class DateRangeSearchForm(SearchForm):
    startdate=forms.DateTimeField(required=False)
    enddate=forms.DateTimeField(required=False)

    def search(self):
        sqs=super(DateRangeSearchForm, self).search()

        if not self.is_valid():
            return self.no_query_found()

        if self.cleaned_data['startdate']:
            return sqs.filter(pub_data__gte=self.cleaned_data['startdate'])

        if self.cleaned_data['enddate']:
            return sqs.filter(pub_data__lte=self.cleaned_data['enddate'])

        return sqs

class FriendSearchForm(forms.Form):
    search=forms.CharField(max_length=50, required=True)


