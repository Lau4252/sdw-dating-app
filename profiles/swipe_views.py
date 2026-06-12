import json
import logging
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone
from .models import Profile, Swipe
from .decorators import RequireApprovedMixin

logger = logging.getLogger(__name__)

class SwipeFeedView(LoginRequiredMixin, RequireApprovedMixin, View):
    """Gibt das naechste Profil fuer den Swipe-Feed als JSON zurueck."""
    
    def get(self, request, *args, **kwargs):
        user = request.user
        profile = getattr(user, "profile", None)
        
        if not profile or not profile.consent_given or not profile.visible or profile.pending:
            return JsonResponse({"error": "Profil nicht bereit"}, status=403)
        
        # Sichtbare, freigeschaltete, nicht-eigene Profile
        qs = Profile.objects.select_related("user").filter(
            consent_given=True,
            visible=True,
            pending=False
        ).exclude(user=user)
        
        # Bereits geswipete ausschliessen
        swiped_ids = Swipe.objects.filter(from_user=user).values_list("to_user_id", flat=True)
        qs = qs.exclude(user_id__in=swiped_ids)
        
        # Optional: nach Geschlecht/Seeking filtern
        if profile.seeking and profile.gender:
            seeking_map = {"M": "M", "F": "F", "A": None}
            target_gender = seeking_map.get(profile.seeking)
            if target_gender:
                qs = qs.filter(gender=target_gender)
            my_gender = profile.gender
            qs = qs.filter(
                Q(seeking="A") | Q(seeking=my_gender)
            )
        
        next_profile = qs.order_by("?").first()
        
        if not next_profile:
            return JsonResponse({"empty": True, "message": "Keine neuen Profile mehr -- komm spaeter wieder!"})
        
        photos = next_profile.photos or []
        photo = photos[0] if photos else ""
        
        return JsonResponse({
            "id": next_profile.user_id,
            "profile_id": next_profile.id,
            "name": next_profile.user.get_full_name() or next_profile.user.email.split("@")[0],
            "age": next_profile.age,
            "quote": next_profile.quote or "",
            "about": next_profile.about or "",
            "photo": photo,
            "photos": photos,
            "studienfach": next_profile.studienfach or "",
            "hochschule": next_profile.hochschule or "",
            "interests": next_profile.interests or [],
            "gender": next_profile.get_gender_display() if next_profile.gender else "",
            "looking_for": next_profile.get_looking_for_display() if next_profile.looking_for else "",
            "trinken": next_profile.get_trinken_display() if next_profile.trinken else "",
            "rauchen": next_profile.get_rauchen_display() if next_profile.rauchen else "",
            "regionen": next_profile.regionen or [],
            "sprachen": next_profile.sprachen or "",
            "prompts": next_profile.prompts or [],
        })

class SwipeActionView(LoginRequiredMixin, RequireApprovedMixin, View):
    """Verarbeitet Like/Pass und prueft auf Match."""
    
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        
        to_user_id = data.get("to_user_id")
        decision = data.get("decision")
        
        if not to_user_id or decision not in ("like", "pass"):
            return JsonResponse({"error": "Ungueltige Parameter"}, status=400)
        
        to_user = get_object_or_404(User, pk=to_user_id)
        
        swipe, created = Swipe.objects.get_or_create(
            from_user=request.user,
            to_user=to_user,
            defaults={"decision": decision}
        )
        
        if not created:
            swipe.decision = decision
            swipe.save()
        
        # Match-Check bei Like
        is_match = False
        if decision == "like":
            is_match = Swipe.is_match(request.user, to_user)
        
        response = {"success": True, "match": is_match}
        
        if is_match:
            to_profile = getattr(to_user, "profile", None)
            response["match_data"] = {
                "name": to_user.get_full_name() or to_user.email.split("@")[0],
                "photo": (to_profile.photos or [""])[0] if to_profile else "",
                "phone": to_profile.phone or "" if to_profile else "",
                "about": to_profile.about or "" if to_profile else "",
                "studienfach": to_profile.studienfach or "" if to_profile else "",
                "hochschule": to_profile.hochschule or "" if to_profile else "",
                "age": to_profile.age if to_profile else None,
            }
        
        return JsonResponse(response)

class MatchListView(LoginRequiredMixin, RequireApprovedMixin, View):
    """Gibt alle Matches des aktuellen Users als JSON zurueck."""
    
    def get(self, request, *args, **kwargs):
        matches = Swipe.get_matches(request.user)
        data = []
        for u in matches:
            p = getattr(u, "profile", None)
            if not p:
                continue
            photos = p.photos or []
            data.append({
                "id": u.id,
                "name": u.get_full_name() or u.email.split("@")[0],
                "age": p.age,
                "photo": photos[0] if photos else "",
                "phone": p.phone or "",
                "about": p.about or "",
                "studienfach": p.studienfach or "",
                "hochschule": p.hochschule or "",
                "interests": p.interests or [],
                "regionen": p.regionen or [],
                "sprachen": p.sprachen or "",
                "gender": p.get_gender_display() if p.gender else "",
            })
        return JsonResponse({"matches": data})

class ProfileBatchView(LoginRequiredMixin, RequireApprovedMixin, View):
    """Gibt bis zu 10 ungesehene, sichtbare Profile als JSON-Array zurueck."""

    def get(self, request, *args, **kwargs):
        user = request.user
        profile = getattr(user, "profile", None)

        if not profile or not profile.consent_given or not profile.visible or profile.pending:
            return JsonResponse({"error": "Profil nicht bereit"}, status=403)

        # Sichtbare, freigeschaltete, nicht-eigene Profile
        qs = Profile.objects.select_related("user").filter(
            consent_given=True,
            visible=True,
            pending=False
        ).exclude(user=user)

        # Bereits geswipete ausschliessen
        swiped_ids = Swipe.objects.filter(from_user=user).values_list("to_user_id", flat=True)
        qs = qs.exclude(user_id__in=swiped_ids)

        # Optional: nach Geschlecht/Seeking filtern
        if profile.seeking and profile.gender:
            seeking_map = {"M": "M", "F": "F", "A": None}
            target_gender = seeking_map.get(profile.seeking)
            if target_gender:
                qs = qs.filter(gender=target_gender)
            my_gender = profile.gender
            qs = qs.filter(
                Q(seeking="A") | Q(seeking=my_gender)
            )

        # Limit: default 10, max 50
        try:
            limit = int(request.GET.get("limit", 10))
            if limit < 1 or limit > 50:
                limit = 10
        except ValueError:
            limit = 10

        profiles = qs.order_by("?")[:limit]

        data = []
        for p in profiles:
            photos = p.photos or []
            data.append({
                "id": p.user_id,
                "profile_id": p.id,
                "name": p.user.get_full_name() or p.user.email.split("@")[0],
                "age": p.age,
                "quote": p.quote or "",
                "about": p.about or "",
                "photo": photos[0] if photos else "",
                "photos": photos,
                "studienfach": p.studienfach or "",
                "hochschule": p.hochschule or "",
                "interests": p.interests or [],
                "gender": p.get_gender_display() if p.gender else "",
                "looking_for": p.get_looking_for_display() if p.looking_for else "",
                "trinken": p.get_trinken_display() if p.trinken else "",
                "rauchen": p.get_rauchen_display() if p.rauchen else "",
                "regionen": p.regionen or [],
                "sprachen": p.sprachen or "",
                "prompts": p.prompts or [],
            })

        return JsonResponse({"profiles": data, "count": len(data)})

class MeView(LoginRequiredMixin, View):
    """Gibt das eigene Profil als JSON zurueck (fuer Frontend-Me-Photo etc.)."""

    def get(self, request, *args, **kwargs):
        p = getattr(request.user, "profile", None)
        if not p:
            return JsonResponse({"error": "Kein Profil"}, status=404)
        photos = p.photos or []
        return JsonResponse({
            "id": request.user.id,
            "name": request.user.get_full_name() or request.user.email.split("@")[0],
            "age": p.age,
            "photo": photos[0] if photos else "",
            "photos": photos,
            "gender": p.get_gender_display() if p.gender else "",
            "seeking": p.get_seeking_display() if p.seeking else "",
        })
