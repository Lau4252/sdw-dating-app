# Generated manually — Full Profile Model with all Mockup fields

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
import json


def migrate_interests(apps, schema_editor):
    """Convert old comma-separated CharField interests to JSON array."""
    Profile = apps.get_model('profiles', 'Profile')
    for profile in Profile.objects.all():
        old_interests = getattr(profile, '_old_interests', '') or ''
        if old_interests.strip():
            # Split by comma and clean up
            interests_list = [i.strip() for i in old_interests.split(',') if i.strip()]
            profile.interests = interests_list
        else:
            profile.interests = []
        profile.save(update_fields=['interests'])


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0001_initial'),
    ]

    operations = [
        # Step 1: Rename old fields so we can add new ones
        migrations.RenameField(
            model_name='profile',
            old_name='interests',
            new_name='_old_interests',
        ),

        # Step 2: Add all new fields from the mockup
        # Sichtbarkeit & Status
        migrations.AddField(
            model_name='profile',
            name='visible',
            field=models.BooleanField(default=False, verbose_name='Sichtbar'),
        ),
        migrations.AddField(
            model_name='profile',
            name='pending',
            field=models.BooleanField(default=True, verbose_name='Freigabe ausstehend'),
        ),

        # Basis-Info
        migrations.AddField(
            model_name='profile',
            name='gender',
            field=models.CharField(max_length=1, choices=[('M', 'Mann'), ('F', 'Frau'), ('D', 'Divers')], blank=True, verbose_name='Geschlecht'),
        ),
        migrations.AddField(
            model_name='profile',
            name='seeking',
            field=models.CharField(max_length=1, choices=[('M', 'Männer'), ('F', 'Frauen'), ('A', 'Alle')], blank=True, verbose_name='Suche nach'),
        ),

        # Studium & Region
        migrations.AddField(
            model_name='profile',
            name='studienfach',
            field=models.CharField(max_length=100, blank=True, verbose_name='Studienfach'),
        ),
        migrations.AddField(
            model_name='profile',
            name='hochschule',
            field=models.CharField(max_length=100, blank=True, verbose_name='Hochschule'),
        ),
        migrations.AddField(
            model_name='profile',
            name='regionen',
            field=models.JSONField(default=list, blank=True, verbose_name='Regionen'),
        ),
        migrations.AddField(
            model_name='profile',
            name='sprachen',
            field=models.CharField(max_length=100, blank=True, verbose_name='Sprachen'),
        ),

        # Profil-Inhalt
        migrations.AddField(
            model_name='profile',
            name='quote',
            field=models.CharField(max_length=200, blank=True, verbose_name='Mein Spruch'),
        ),
        migrations.AddField(
            model_name='profile',
            name='about',
            field=models.TextField(blank=True, verbose_name='Über mich'),
        ),
        migrations.AddField(
            model_name='profile',
            name='looking_for',
            field=models.CharField(max_length=20, choices=[('serious', '💛 Etwas Ernstes'), ('open', '🥂 Offen — Freunde & mehr'), ('casual', '✨ Mal schauen')], blank=True, verbose_name='Suche nach'),
        ),

        # Lifestyle
        migrations.AddField(
            model_name='profile',
            name='trinken',
            field=models.CharField(max_length=20, choices=[('nie', 'Nie'), ('selten', 'Selten'), ('gesellig', 'Gesellig am Wochenende'), ('regelmaessig', 'Regelmäßig')], blank=True, verbose_name='Trinken'),
        ),
        migrations.AddField(
            model_name='profile',
            name='rauchen',
            field=models.CharField(max_length=20, choices=[('nie', 'Nichtraucher(in)'), ('gelegentlich', 'Gelegentlich'), ('regelmaessig', 'Regelmäßig')], blank=True, verbose_name='Rauchen'),
        ),

        # Fotos
        migrations.AddField(
            model_name='profile',
            name='photos',
            field=models.JSONField(default=list, blank=True, verbose_name='Fotos'),
        ),

        # Prompts
        migrations.AddField(
            model_name='profile',
            name='prompts',
            field=models.JSONField(default=list, blank=True, verbose_name='Prompts'),
        ),

        # Step 3: Add the new JSON interests field
        migrations.AddField(
            model_name='profile',
            name='interests',
            field=models.JSONField(default=list, blank=True, verbose_name='Interessen'),
        ),

        # Step 4: Run data migration for interests
        migrations.RunPython(migrate_interests, migrations.RunPython.noop),

        # Step 5: Remove old fields
        migrations.RemoveField(
            model_name='profile',
            name='_old_interests',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='bio',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='city',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='photo',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='study_program',
        ),
    ]
