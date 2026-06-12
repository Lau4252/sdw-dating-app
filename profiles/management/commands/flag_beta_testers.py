import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stipconnect.settings')
sys.path.insert(0, '/app')
django.setup()

from profiles.models import Profile

def run():
    """Markiert die ersten 20 freigeschalteten (pending=False), einwilligenden Profile als Beta-Tester."""
    candidates = Profile.objects.filter(
        pending=False,
        consent_given=True,
        is_beta_tester=False
    ).select_related('user').order_by('created_at')[:20]

    count = 0
    for profile in candidates:
        profile.is_beta_tester = True
        profile.save()
        count += 1
        print(f"  ✅ {profile.user.email} -> Beta-Tester")

    print(f"\nDone: {count} User als Beta-Tester markiert.")

if __name__ == '__main__':
    run()
