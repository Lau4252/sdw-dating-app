from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Prefetch
from django.contrib.auth.models import User
from .models import Profile
from .forms import ProfileForm

class ConsentRequiredMixin:
    """Redirect to consent page if user hasn't given consent yet."""
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if not hasattr(request.user, 'profile') or not request.user.profile.consent_given:
                return redirect('consent')
        return super().dispatch(request, *args, **kwargs)

class ProfileListView(LoginRequiredMixin, ConsentRequiredMixin, ListView):
    model = Profile
    template_name = 'profiles/list.html'
    context_object_name = 'profiles'
    paginate_by = 20

    def get_queryset(self):
        qs = Profile.objects.select_related('user').filter(consent_given=True)
        q = self.request.GET.get('q')
        study = self.request.GET.get('study')
        city = self.request.GET.get('city')
        if q:
            qs = qs.filter(
                Q(user__first_name__icontains=q) |
                Q(user__last_name__icontains=q) |
                Q(study_program__icontains=q) |
                Q(city__icontains=q)
            )
        if study:
            qs = qs.filter(study_program__icontains=study)
        if city:
            qs = qs.filter(city__icontains=city)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['study_programs'] = Profile.objects.exclude(study_program='').values_list('study_program', flat=True).distinct().order_by('study_program')
        ctx['cities'] = Profile.objects.exclude(city='').values_list('city', flat=True).distinct().order_by('city')
        return ctx

class ProfileDetailView(LoginRequiredMixin, ConsentRequiredMixin, DetailView):
    model = Profile
    template_name = 'profiles/detail.html'
    context_object_name = 'profile'

    def get_queryset(self):
        return Profile.objects.select_related('user').filter(consent_given=True)

class ProfileUpdateView(LoginRequiredMixin, ConsentRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'profiles/edit.html'

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_success_url(self):
        return self.request.user.profile.get_absolute_url()

class ProfileDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'profiles/delete_confirm.html'
    success_url = reverse_lazy('login')

    def get_object(self, queryset=None):
        return self.request.user

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        # Remove photo file if exists
        if hasattr(user, 'profile') and user.profile.photo:
            user.profile.photo.delete(save=False)
        user.delete()
        return redirect(self.success_url)

from django.views import View
from django.utils import timezone
from django.contrib import messages

class ConsentSubmitView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        consent = request.POST.get('consent') == 'on'
        if consent:
            profile = request.user.profile
            profile.consent_given = True
            profile.consent_date = timezone.now()
            profile.save()
            messages.success(request, "Einwilligung erfolgreich erteilt. Willkommen bei StipConnect!")
            return redirect('profile_list')
        messages.error(request, "Bitte setze den Haken, um fortzufahren.")
        return redirect('consent')
