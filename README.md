# StipConnect

Interne Stipendiaten-Vernetzungsplattform. Max. 200 Nutzer, geschützt durch Cloudflare Access, gehostet auf eigener Hardware.

## Tech-Stack

- **Backend**: Django 5 + SQLite
- **Frontend**: Django Templates + Tailwind CSS (CDN)
- **Auth**: Cloudflare Access (kein eigenes Passwort-Login)
- **PWA**: Offline-fähig, installierbar auf Homescreen
- **Hosting**: Docker Compose + Caddy + Cloudflare Tunnel (self-hosted)

## Schnellstart

```bash
# 1. Repo clonen
git clone <repo-url> && cd stip-dating

# 2. Virtuelle Umgebung
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. DB initialisieren
python manage.py migrate

# 4. lokal starten (nur für Entwicklung)
DEV_AUTH_EMAIL=dev@example.com DJANGO_DEBUG=True python manage.py runserver
```

## Deployment (Docker + Cloudflare)

Siehe [README_DEPLOY.md](README_DEPLOY.md) für die vollständige Schritt-für-Schritt-Anleitung.

Kurzversion:
1. `.env` aus `.env.template` kopieren und Werte eintragen
2. `cloudflared tunnel create stipconnect` → Token in `.env`
3. Cloudflare Zero Trust → Access → Application einrichten
4. `docker compose up -d`

## DSGVO-Compliance (Minimal-Viable)

- ☑️ Einwilligungs-Modal beim ersten Login (`consent.html`)
- ☑️ Datenschutzerklärung (`datenschutz.html`)
- ☑️ Lösch-Button im eigenen Profil (`profile_delete` View)
- ☑️ Cloudflare DPA im Account akzeptiert

## Ordnerstruktur

```
stip-dating/
├── stipconnect/          # Django-Projekt (Settings, URLs, WSGI)
├── profiles/             # App: Models, Views, Forms, Admin
├── templates/            # Django Templates (HTML + Tailwind)
├── static/               # PWA-Assets (Manifest, SW, Icons, CSS)
├── media/                # Nutzer-Uploads (Fotos)
├── scripts/              # entrypoint.sh
├── infra/                # Cloudflare-Referenz-Config
├── docker-compose.yml
├── Caddyfile
├── Dockerfile
└── requirements.txt
```

## Wichtige URLs

| Pfad | Zweck |
|------|-------|
| `/profiles/` | Alle Profile (mit Filter) |
| `/profiles/<pk>/` | Detail-Ansicht |
| `/profiles/edit/` | Eigenes Profil bearbeiten |
| `/profiles/delete/` | Eigenes Profil löschen |
| `/consent/` | Erst-Login Einwilligung |
| `/datenschutz/` | Datenschutzerklärung |
| `/admin/` | Django Admin |

## Lizenz

Interne Nutzung für Studienstiftung. Keine öffentliche Verbreitung.
