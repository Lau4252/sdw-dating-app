from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Profile

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profil'
    fields = ('photo', 'bio', 'phone', 'study_program', 'city', 'birth_date', 'interests', 'consent_given', 'consent_date')
    readonly_fields = ('consent_date',)

class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'profile__study_program', 'profile__city', 'profile__phone')

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
