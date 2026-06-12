# StipConnect — Dating-App für SDW-Stipendiaten

## Projekt-Übersicht
**Name:** StipConnect ("Such Dir Wen")  
**Zielgruppe:** Stipendiaten der Stiftung der Deutschen Wirtschaft  
**URL:** https://sdw-connect.kochlab.net/  
**Motto:** "Wir stiften Connections!"

## Architektur
- **Backend:** Django 5 + SQLite
- **Auth:** Cloudflare Access (HTTP_CF_ACCESS_AUTHENTICATED_USER_EMAIL Header)
- **Frontend:** Django Templates + Tailwind CDN
- **Hosting:** Docker (Web + Caddy + Cloudflared)
- **Server:** /home/laurensmain/stip-dating/
- **Domain:** sdw-connect.kochlab.net

## Wichtige Dateien & Ordner
- `/home/laurensmain/stip-dating/` — Projekt-Root
- `/home/laurensmain/stip-dating/stipconnect/` — Django-Settings, URLs
- `/home/laurensmain/stip-dating/profiles/` — Django-App (Models, Views, Forms)
- `/home/laurensmain/stip-dating/templates/` — HTML-Templates
- `/home/laurensmain/stip-dating/static/` — CSS, JS, Bilder
- `/home/laurensmain/stip-dating/db.sqlite3` — Datenbank
- `/home/laurensmain/stip-dating/docker-compose.yml` — Docker-Config
- `/home/laurensmain/stip-dating/manage.py` — Django-Management
- `/home/laurensmain/Nextcloud/Startup/Projekte/sdw-dating-app/` — Design-Assets (Nextcloud-Sync)

## Docker-Kommandos (immer verwenden!)
```bash
# Container rebuild nach Code-Änderung
cd /home/laurensmain/stip-dating && docker compose build web && docker compose up -d web

# Logs anschauen
docker compose logs -f web

# Django-Shell
docker compose exec web python manage.py shell

# Migrationen
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate

# Static-Files collecten
docker compose exec web python manage.py collectstatic --noinput
```

## Code-Standards
- Django-Models: Snake_case, docstrings in Deutsch
- Templates: Tailwind-Klassen, responsive Design
- Views: Class-based wo sinnvoll, function-based für einfache Sachen
- URL-Patterns: sprechende Namen (z.B. `profile_detail`, `swipe_feed`)
- Python: PEP 8, 4-space Indentation
- HTML: Semantische Tags, aria-labels für Accessibility

## Sicherheitsregeln
- NIE Secrets in Code committen (.env nutzen)
- NIE `rm -rf /` oder ähnliches ausführen
- NIE die Datenbank löschen ohne explizite Bestätigung
- IMMER Cloudflare Access Header prüfen: `request.META.get('HTTP_CF_ACCESS_AUTHENTICATED_USER_EMAIL')`
- IMMER Django-CSRF-Token in Forms verwenden

## DSGVO-Compliance (MUSS immer beachtet werden)
- Consent-Checkbox NICHT pre-selected
- Datenschutzerklärung als separate Seite
- Löschfunktion für User-Profile
- Telefonnummer erst bei Match sichtbar
- Keine Daten an Dritte weitergeben

## Design-System (aus dem Mockup)
- **Farben:**
  - Primary: `#F9C513` (Gelb)
  - Text: `#575756` (Dunkelgrau)
  - Hintergrund: `#ecebe7` (Hellgrau)
  - Karte: `#ffffff` (Weiß)
  - Ablehnen: `#d35a5a` (Rot)
- **Radius:** 20px für Cards, 12px für Buttons
- **Font:** System-Font-Stack (-apple-system, Segoe UI, Roboto)
- **Schatten:** `0 10px 30px rgba(0,0,0,.25)` für Cards

## App-Struktur (geplant)
1. **Login/Auth** — Cloudflare Access → Django User Auto-Create
2. **Consent** — DSGVO-Einwilligung vor erstem Swipe
3. **Entdecken (Swipe)** — Tinder-like Interface mit Profil-Cards
4. **Profil-Detail** — Vollständiges Profil mit Fotos, Interessen, Kontakt
5. **Matches** — Grid-Übersicht aller Matches mit Telefonnummer
6. **Mein Profil** — Bearbeiten, Fotos hochladen, Einstellungen
7. **Admin-Freigabe** — SDW-Admin prüft neue Accounts

## Mockup-Referenz
Das vollständige HTML-Mockup liegt in:
`/home/laurensmain/stip-dating/static/mockup-karte.html`
Alle Design-Entscheidungen basieren auf diesem Mockup.

## Kanban-Board
- Board: `sdw-dating`
- CLI: `hermes kanban boards switch sdw-dating`
- Neue Tasks immer mit `--idempotency-key` erstellen
- Status: blocked → running → done

## Meilensteine
□ Phase 0: Mockup live auf Website
□ Phase 1: Django-Model "Profile" + SQLite-Migration
□ Phase 2: Cloudflare Access Auth + User-Auto-Create
□ Phase 3: Swipe-Interface (Frontend)
□ Phase 4: Matching-Algorithmus
□ Phase 5: Chat/Match-Notification
□ Phase 6: Admin-Freigabe-Workflow
□ Phase 7: DSGVO-Consent + Löschfunktion
□ Phase 8: Mobile-Optimierung + PWA
□ Phase 9: Beta-Launch

## Notizen
- Server: Ubuntu 22.04, Docker läuft
- Python 3.11 im Container
- Cloudflare Tunnel: `cloudflared` läuft als Docker-Service
- Nextcloud-Sync: `/home/laurensmain/Nextcloud/`
- Voice-Input: whisper.cpp auf Port 8085
