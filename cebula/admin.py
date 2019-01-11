from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.admin import User
from django.contrib.sites.models import Site

from .models import Photo,Question, Answers, Profile, MyUser, Category, Buddi


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False

class CustomUserAdmin(UserAdmin):
    inlines=(ProfileInline,)

# Register your models here.
admin.site.register(Photo)
admin.site.register(Question)
admin.site.register(Answers)
admin.site.register(MyUser)
admin.site.register(Category)
admin.site.register(Buddi)
