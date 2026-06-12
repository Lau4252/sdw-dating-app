"""Decorator und Mixins für Freigabe-Status (pending)."""
from django.shortcuts import redirect
from functools import wraps


class RequireApprovedMixin:
    """Redirect zur Warteschlange wenn Profile.pending=True oder nicht Beta-Tester.
    Staff-User (Admins) werden nie geblockt — sie müssen Beta-Verwaltung machen können.
    """

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            # Staff/Admin immer erlauben
            if request.user.is_staff:
                return super().dispatch(request, *args, **kwargs)
            profile = getattr(request.user, 'profile', None)
            if profile:
                if profile.pending:
                    return redirect('warteschlange')
                if not profile.is_beta_tester:
                    return redirect('beta_waitlist')
        return super().dispatch(request, *args, **kwargs)


def require_approved(view_func):
    """Function-based-View Decorator: redirect zur Warteschlange oder Beta-Waitlist.
    Staff-User (Admins) werden nie geblockt.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_staff:
                return view_func(request, *args, **kwargs)
            profile = getattr(request.user, 'profile', None)
            if profile:
                if profile.pending:
                    return redirect('warteschlange')
                if not profile.is_beta_tester:
                    return redirect('beta_waitlist')
        return view_func(request, *args, **kwargs)
    return wrapper
