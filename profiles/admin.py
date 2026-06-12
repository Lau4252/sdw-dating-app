from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Profile, Message

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'text_preview', 'created_at', 'is_read')
    list_filter = ('created_at',)
    search_fields = ('sender__email', 'recipient__email', 'text')
    readonly_fields = ('created_at', 'read_at')

    def text_preview(self, obj):
        return obj.text[:50] + ('...' if len(obj.text) > 50 else '')
    text_preview.short_description = 'Nachricht'


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profil'
    fields = ('visible', 'pending', 'gender', 'seeking', 'birth_date', 'studienfach', 'hochschule', 'regionen', 'sprachen', 'quote', 'about', 'looking_for', 'trinken', 'rauchen', 'interests', 'photos', 'phone', 'consent_given', 'consent_date', 'prompts', 'created_at', 'updated_at')
    readonly_fields = ('consent_date', 'created_at', 'updated_at')

class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'profile__studienfach', 'profile__hochschule', 'profile__phone')

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
