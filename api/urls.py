from django.contrib import admin
from django.urls import path, re_path
from django.conf.urls import url, include
from cebula import views

app_name='api'

urlpatterns = [
    re_path('waiting/(?P<pk>\d*)', views.WaitingAPIView.as_view(), name='waiting_api'),
    path('<slug:username>/setting', views.SettingAPIView.as_view(), name="setting_api"),
    path('<slug:username>/userpage', views.UserPageAPIView.as_view(), name="user_api"),
    re_path('myuser/(?P<pk>\d+)', views.Custom_MyUserAPIView.as_view(), name="myuser_custom_api"),
    re_path('question/(?P<pk>\d+)', views.Custom_QuestionAPIView.as_view(), name="question_custom_api"),
    path('question', views.All_QuestionAPIView.as_view(), name="question_all_api"),
    path('answers', views.All_AnswersAPIView.as_view(), name="answers_all_api"),
    path('main', views.MainPageAPIView.as_view(), name="main_api"),
    re_path('ShareQnA/(?P<pk>\d+)/', views.ShareQnAAPIView.as_view(), name="Share_QnA_api"),
    re_path('ShareAnswers/(?P<pk>\d+)/', views.ShareAnswersAPIView.as_view(), name="Share_Answers_api"),
    re_path('Buddi', views.BuddiAPIView.as_view(), name="Buddi_api"),
]
