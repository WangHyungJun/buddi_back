from django.contrib import admin
from django.urls import path, re_path
from django.conf.urls import url, include
from . import views

app_name='cebula'
urlpatterns = [
    path('',views.IndexView.as_view(),name='index'),
    re_path(r'waiting/(?P<question_text>.*)/$', views.Waiting.as_view(), name='waiting'),
    # url(r'^waiting/(?P<pk>.*)/$', views.WaitingView,name='waiting'),
    url(r'^question/$',views.QuestionView.as_view(),name='question'),
    re_path(r'^(?P<username>.*)/category/(?P<category>.*)/$', views.Category.as_view(),name='category'), #<slug:category>[-\w]*
    path('<slug:username>/userpage',views.UserPage,name='userpage'),
    path('<slug:username>/answer',views.UserPage_answer,name='userpage_answer'),
    path('<slug:username>/Question',views.UserPage_MyQuestion.as_view(),name='userpage_question'),
    path('<slug:username>/SharedQuestion',views.UserPage_sharedQuestion,name='userpage_sharedQuestion'),
    path('<slug:username>/Post',views.UserPage_post,name='userpage_post'),
    re_path('(?P<username>.*)/following', views.following.as_view(), name='following'),
    re_path('(?P<username>.*)/follower', views.follower.as_view(), name='follower'),
    #아래의 pk는 subcategory의 pk, 나중에는 꼭 username으로 고유식별을 한 뒤 pk 대신 subcategory를 사용할 것!
    # path('<slug:username>/<slug:category>/(?P<pk>\d+)/$', views.Sub_Category.as_view(), name="sub_category"),
    re_path(r'(?P<username>.*)/(?P<category>.*)/(?P<sub_category>.*)', views.Sub_Category.as_view(), name="sub_category"),
    # path('search/', views.MySearchView.as_view(), name='search_view'),
    # path('friendsearch', views.FriendSearch.as_view(), name="friendsearch"),
    path('test', views.Test.as_view(), name="test"),
    path('<slug:username>/setting', views.Setting.as_view(), name='setting'),
    path('websoket' ,views.websoket.as_view(), name="websoket"),
]
