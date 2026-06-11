from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, UpdateView, DeleteView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q, Prefetch
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from .models import Profile, Swipe, FeedbackEntry
from .forms import ProfileForm, FeedbackForm
from .decorators import RequireApprovedMixin

class ConsentRequiredMixin:
    """Redirect to consent page if user hasn't given consent yet."""
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if not hasattr(request.user, 'profile') or not request.user.profile.consent_given:
                return redirect('consent')
        return super().dispatch(request, *args, **kwargs)

class WarteschlangeView(LoginRequiredMixin, TemplateView):
    """Zeigt Warteschlange-Seite für noch nicht freigeschaltete User."""
    template_name = 'profiles/warteschlange.html'

class BetaWaitlistView(LoginRequiredMixin, TemplateView):
    """Zeigt Beta-Waitlist-Seite für User die nicht im Beta sind."""
    template_name = 'profiles/beta_waitlist.html'

class SwipePageView(LoginRequiredMixin, ConsentRequiredMixin, RequireApprovedMixin, TemplateView):
    template_name = 'profiles/swipe.html'

class ProfileListView(LoginRequiredMixin, ConsentRequiredMixin, RequireApprovedMixin, ListView):
    model = Profile
    template_name = 'profiles/list.html'
    context_object_name = 'profiles'
    paginate_by = 20

    def get_queryset(self):
        qs = Profile.objects.select_related('user').filter(consent_given=True, visible=True, pending=False)
        q = self.request.GET.get('q')
        studie = self.request.GET.get('studie')
        hochschule = self.request.GET.get('hochschule')
        if q:
            qs = qs.filter(
                Q(user__first_name__icontains=q) |
                Q(user__last_name__icontains=q) |
                Q(studienfach__icontains=q) |
                Q(hochschule__icontains=q) |
                Q(quote__icontains=q)
            )
        if studie:
            qs = qs.filter(studienfach__icontains=studie)
        if hochschule:
            qs = qs.filter(hochschule__icontains=hochschule)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['studienfaecher'] = Profile.objects.exclude(studienfach='').values_list('studienfach', flat=True).distinct().order_by('studienfach')
        ctx['hochschulen'] = Profile.objects.exclude(hochschule='').values_list('hochschule', flat=True).distinct().order_by('hochschule')
        return ctx

import json

class BrowseView(LoginRequiredMixin, ConsentRequiredMixin, RequireApprovedMixin, ListView):
    """Grid-Übersicht aller sichtbaren Profile mit Filter (Hochschule, Studienfach, Region)."""
    model = Profile
    template_name = 'profiles/browse.html'
    context_object_name = 'profiles'
    paginate_by = 24

    def get_queryset(self):
        qs = Profile.objects.select_related('user').filter(
            consent_given=True, visible=True, pending=False
        ).exclude(user=self.request.user)

        hochschule = self.request.GET.get('hochschule')
        studienfach = self.request.GET.get('studienfach')
        region = self.request.GET.get('region')
        q = self.request.GET.get('q')

        if hochschule:
            qs = qs.filter(hochschule=hochschule)
        if studienfach:
            qs = qs.filter(studienfach=studienfach)
        if region:
            qs = qs.filter(regionen__icontains=region)
        if q:
            qs = qs.filter(
                Q(user__first_name__icontains=q) |
                Q(user__last_name__icontains=q) |
                Q(quote__icontains=q) |
                Q(about__icontains=q)
            )
        return qs.order_by('-created_at')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        visible_qs = Profile.objects.filter(visible=True, pending=False, consent_given=True)
        ctx['hochschulen'] = visible_qs.exclude(hochschule='').values_list('hochschule', flat=True).distinct().order_by('hochschule')
        ctx['studienfaecher'] = visible_qs.exclude(studienfach='').values_list('studienfach', flat=True).distinct().order_by('studienfach')
        # Regionen aus JSON-Arrays flatten
        all_regions = set()
        for r in visible_qs.exclude(regionen=[]).values_list('regionen', flat=True):
            if r:
                try:
                    if isinstance(r, str):
                        arr = json.loads(r)
                    else:
                        arr = r
                    all_regions.update(arr)
                except Exception:
                    pass
        ctx['regionen'] = sorted(all_regions)
        ctx['filter_count'] = sum([
            bool(self.request.GET.get('hochschule')),
            bool(self.request.GET.get('studienfach')),
            bool(self.request.GET.get('region')),
            bool(self.request.GET.get('q')),
        ])
        return ctx


class ProfileDetailView(LoginRequiredMixin, ConsentRequiredMixin, RequireApprovedMixin, DetailView):
    model = Profile
    template_name = 'profiles/detail.html'
    context_object_name = 'profile'

    def get_queryset(self):
        return Profile.objects.select_related('user').filter(consent_given=True)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        profile = self.object
        user = self.request.user
        is_match = Swipe.is_match(user, profile.user)
        under_200 = User.objects.count() < 200
        ctx['can_see_phone'] = is_match or (user == profile.user) or under_200
        ctx['is_match'] = is_match
        ctx['is_own_profile'] = (user == profile.user)
        ctx['has_sent_like'] = Swipe.objects.filter(
            from_user=user, to_user=profile.user, decision='like'
        ).exists()
        return ctx

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
        user.delete()
        return redirect(self.success_url)

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


from django.contrib.auth import logout as django_logout
from django.http import HttpResponseRedirect
from django.conf import settings

class CloudflareLogoutView(View):
    """
    Loescht Django-Session und leitet zu Cloudflare Access Logout-URL.
    CF Access loescht damit auch das CF-Access-Cookie,
    sodass ein vollstaendiger Logout erfolgt.
    """
    def get(self, request, *args, **kwargs):
        django_logout(request)
        cf_logout_url = getattr(settings, 'CF_ACCESS_LOGOUT_URL', None)
        if cf_logout_url:
            return HttpResponseRedirect(cf_logout_url)
        return redirect('home')

# ── Meine Matches ───────────────────────────────────────────────────

class MyMatchesView(LoginRequiredMixin, ConsentRequiredMixin, RequireApprovedMixin, ListView):
    """Liste aller gegenseitigen Matches mit Telefonnummer."""
    template_name = 'profiles/matches.html'
    context_object_name = 'matches'

    def get_queryset(self):
        # Swipe.get_matches gibt User-Objekte zurueck
        return Swipe.get_matches(self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Fuer jeden Match das zugehoerige Profil anreichern
        matches_with_profile = []
        for u in ctx['matches']:
            p = getattr(u, 'profile', None)
            if p:
                matches_with_profile.append({'user': u, 'profile': p})
        ctx['matches_with_profile'] = matches_with_profile
        return ctx


class BrowseProfilesView(BrowseView):
    """Einfache Browse-View fuer StipConnect (Task 3.1).
    Zeigt sichtbare Profile im Tailwind-Grid ohne Filter-Overhead.
    """
    template_name = 'browse.html'
    paginate_by = 12

    def get_context_data(self, **kwargs):
        # Nur Standard-Pagination-Context, kein Filter-Bar-Zeugs
        ctx = super(ListView, self).get_context_data(**kwargs)
        ctx['profiles'] = ctx.get('object_list', [])
        return ctx

class IsAdminMixin(UserPassesTestMixin):
    """Nur Staff-User (SDW-Admins) dürfen zugreifen."""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff

class AdminPendingProfilesView(LoginRequiredMixin, IsAdminMixin, ListView):
    """Admin-Dashboard: Liste aller pending Profiles mit Freigabe/Ablehnen-Actions."""
    model = Profile
    template_name = 'profiles/admin_dashboard.html'
    context_object_name = 'pending_profiles'
    paginate_by = 20

    def get_queryset(self):
        return Profile.objects.select_related('user').filter(pending=True).order_by('created_at')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['total_pending'] = Profile.objects.filter(pending=True).count()
        ctx['total_approved'] = Profile.objects.filter(pending=False, visible=True).count()
        ctx['total_rejected'] = Profile.objects.filter(pending=False, visible=False).count()
        ctx['total_beta'] = Profile.objects.filter(is_beta_tester=True).count()
        return ctx

class AdminApproveView(LoginRequiredMixin, IsAdminMixin, View):
    """Profil freigeben: pending=False, visible=True"""
    def post(self, request, pk, *args, **kwargs):
        profile = get_object_or_404(Profile, pk=pk, pending=True)
        profile.pending = False
        profile.visible = True
        profile.save()
        messages.success(request, f"Profil von {profile} freigegeben.")
        return redirect('admin_dashboard')

class AdminRejectView(LoginRequiredMixin, IsAdminMixin, View):
    """Profil ablehnen: pending=False, visible=False"""
    def post(self, request, pk, *args, **kwargs):
        profile = get_object_or_404(Profile, pk=pk, pending=True)
        profile.pending = False
        profile.visible = False
        profile.save()
        messages.success(request, f"Profil von {profile} abgelehnt.")
        return redirect('admin_dashboard')

# ── Beta-Tester Toggle + Feedback ─────────────────────────────────────

class AdminToggleBetaView(LoginRequiredMixin, IsAdminMixin, View):
    """Beta-Status eines Users toggeln (POST)."""
    def post(self, request, pk, *args, **kwargs):
        profile = get_object_or_404(Profile, pk=pk)
        profile.is_beta_tester = not profile.is_beta_tester
        profile.save()
        status = 'aktiviert' if profile.is_beta_tester else 'deaktiviert'
        messages.success(request, f"Beta-Status von {profile} {status}.")
        return redirect('admin_dashboard')

class AdminFeedbackListView(LoginRequiredMixin, IsAdminMixin, ListView):
    """Admin-Übersicht aller Feedback-Einträge."""
    model = FeedbackEntry
    template_name = 'profiles/admin_feedback.html'
    context_object_name = 'feedbacks'
    paginate_by = 25

    def get_queryset(self):
        qs = FeedbackEntry.objects.select_related('user').order_by('-created_at')
        typ_filter = self.request.GET.get('typ')
        if typ_filter:
            qs = qs.filter(typ=typ_filter)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['typ_filter'] = self.request.GET.get('typ', '')
        ctx['type_choices'] = FeedbackEntry.FEEDBACK_TYPES
        ctx['total_count'] = FeedbackEntry.objects.count()
        return ctx

class FeedbackFormView(LoginRequiredMixin, ConsentRequiredMixin, RequireApprovedMixin, View):
    """Beta-Tester: Feedback-Formular anzeigen + speichern."""
    def get(self, request, *args, **kwargs):
        form = FeedbackForm()
        return render(request, 'profiles/feedback_form.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = FeedbackForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            entry.save()
            messages.success(request, "Danke für dein Feedback! 🎉")
            return redirect('browse')
        return render(request, 'profiles/feedback_form.html', {'form': form})
