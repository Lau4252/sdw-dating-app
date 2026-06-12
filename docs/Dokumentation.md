# StipConnect — Dating-App für SDW-Stipendiaten

**Dokumentation** | Stand: 2026-06-12  
**Domain:** [sdw-connect.kochlab.net](https://sdw-connect.kochlab.net)  
**Stack:** Django 5 + SQLite + Docker + Cloudflare Access  
**Orchestrator:** Hermes Agent (autonomer Coding-Agent via Cronjob)

---

## 1. Projekt-Übersicht

StipConnect ist eine ultra-minimale Dating-App für Stiftungswerk-Stipendiaten. Kein Chat, kein Algorithmus, kein manuelles Approval. Flow: **Browse → Like → Mutual → Telefonnummer**.

### Kernphilosophie
- **Privacy-first:** Authentifizierung ausschließlich via Cloudflare Access (kein lokaler Django-Login)
- **Minimalismus:** Nur essenzielle Features — Profile ansehen, liken, Matches sehen, Telefonnummer teilen
- **Autonom:** Hermes Agent + Claude Code arbeiten autonom am Projekt (Kanban `sdw-dating`)

---

## 2. Stack & Architektur

| Komponente | Technologie |
|------------|-------------|
| Backend | Django 5.2.15 (Python 3.11) |
| Datenbank | SQLite |
| Webserver | Gunicorn (Docker-Container) |
| Reverse-Proxy | Caddy |
| Auth | Cloudflare Access (JWT-Header) |
| Container | Docker + Docker Compose |
| Domain-Management | Cloudflare DNS |
| File-Storage | Host-Bind-Mount (`./media/`) |
| Task-Queue | Django-Cronjob via Hermes |

### Netzwerk-Architektur
```
User → Cloudflare Access → Caddy (:80) → Gunicorn (:8000) → Django
                                    ↓
                              Docker Host
                              /srv/media/ (Caddy file_server)
                              /app/ (Django app)
```

### Container-Konfiguration
- **Container:** `stipconnect_web` (Django + Gunicorn)
- **Port:** 8000 (intern) → 8081 (extern via Docker Bridge)
- **Netzwerk:** `bridge` (NICHT `host`) — daher `http://172.17.0.1:8081` für Tunnel
- **Volume-Mounts:**
  - `./media:/app/media` — Profilfotos
  - `./static:/app/staticfiles` — Static Assets
  - `./db.sqlite3:/app/db.sqlite3` — Datenbank

---

## 3. Ordnerstruktur

```
SDW Datingapp Projekt/
├── stipconnect/              # Django-Projekt-Settings
│   ├── __init__.py
│   ├── settings.py           # Django-Konfiguration
│   ├── urls.py               # URL-Routing (keine auth-URLs!)
│   ├── wsgi.py
│   ├── asgi.py
│   └── cloudflare_middleware.py  # CF Access Auth-Middleware
│
├── profiles/                 # Haupt-App
│   ├── __init__.py
│   ├── models.py             # Profile, Swipe, FeedbackEntry
│   ├── views.py              # Browse, Detail, Edit, Delete
│   ├── swipe_views.py        # API für Swipe-Feed, Matches
│   ├── forms.py              # ProfileForm, FeedbackForm
│   ├── urls.py               # App-URLs
│   ├── admin.py              # Django-Admin
│   ├── tests.py
│   └── migrations/           # Datenbank-Migrationen
│
├── templates/                # HTML-Templates
│   ├── base.html             # Base-Layout
│   ├── landing.html          # Landing-Page (mit Mock-Daten)
│   ├── browse.html           # Browse-Grid
│   └── profiles/
│       ├── detail.html       # Profil-Detail
│       ├── edit.html         # Profil-Edit (Foto-Upload!)
│       ├── swipe.html        # Swipe-Interface
│       ├── matches.html      # Match-Liste
│       └── ...
│
├── static/                   # Static Assets (CSS, JS)
│   ├── css/
│   └── js/
│
├── media/                    # Uploads (Profilfotos)
│   └── photos/
│       └── %Y/%m/            # Jahr/Monat-Struktur
│
├── manage.py                 # Django-Management
├── requirements.txt          # Python-Abhängigkeiten
├── Dockerfile                # Container-Definition
├── docker-compose.yml        # Compose-Konfiguration
├── Caddyfile                 # Caddy-Reverse-Proxy
├── db.sqlite3                # SQLite-Datenbank
├── .env*                     # Environment-Variablen (nicht im Git)
└── Dokumentation/            # Diese Datei + weitere Docs
```

---

## 4. Features & Funktionalität

### Aktuell implementiert
| Feature | Status |
|---------|--------|
| Cloudflare Access Auth | ✅ Nur CF Access, kein lokaler Login |
| Profil-Erstellung | ✅ Automatisch bei erstem Login |
| Profil-Bearbeiten | ✅ Inkl. Profilfoto-Upload |
| Browse-Grid | ✅ Filter: Hochschule, Studienfach, Region |
| Swipe-Interface | ✅ Like/Dislike mit Animation |
| Matches | ✅ Mutual-Like = Telefonnummer sichtbar |
| Feedback-System | ✅ Beta-Tester Feedback-Formular |
| Admin-Dashboard | ✅ Intern: Pending-Profiles, Feedback-Übersicht |
| Landing-Page | ✅ Mit Demo-Daten für Nicht-Angemeldete |

### In Entwicklung / Bugs
| Feature | Status | Problem |
|---------|--------|---------|
| Profilfoto-Upload | ⚠️ Fix läuft | Photo-Feld war JSON (URLs), jetzt ImageField |
| Container-Persistenz | ⚠️ Check | db.sqlite3 + media/ auf Host gemountet |

### Nicht geplant (by Design)
- ❌ Chat-System
- ❌ Matching-Algorithmus
- ❌ Manuelles Approval
- ❌ Lokaler Django-Login
- ❌ Registrierung

---

## 5. Datenbank-Schema

### Profile-Modell
```python
class Profile(models.Model):
    user = OneToOneField(User, related_name='profile')
    visible = BooleanField(default=True)
    pending = BooleanField(default=False)  # Für Admin-Approval (nicht aktiv)
    is_beta_tester = BooleanField(default=False)
    
    # Basis
    gender = CharField(choices=[('M','Mann'),('W','Frau'),('D','Divers')])
    seeking = CharField(choices=[('M','Männer'),('W','Frauen'),('A','Alle')])
    birth_date = DateField(blank=True, null=True)
    alter = IntegerField(default=20)  # Berechnet aus birth_date
    
    # Studium
    studienfach = CharField(max_length=100)
    hochschule = CharField(max_length=100)
    
    # Standort & Sprachen
    regionen = JSONField(default=list)  # ["Erfurt", "Berlin"]
    sprachen = CharField(max_length=100)
    
    # Persönlichkeit
    quote = CharField(max_length=200)
    about = TextField()
    looking_for = CharField(choices=[('F','Freunde'),('E','Etwas Ernstes'),('O','Offen'),('S','Mal schauen')])
    
    # Lifestyle
    trinken = CharField(choices=...)
    rauchen = CharField(choices=...)
    
    # Interessen & Fotos
    interests = JSONField(default=list)  # ["Laufen", "Lesen"]
    photos = JSONField(default=list)     # DEPRECATED: JSON-Array mit URLs
    photo = ImageField(upload_to='photos/%Y/%m/')  # NEU: Echter Upload
    
    # Kontakt
    phone = CharField(max_length=50)
    
    # Prompts (Hinge-Style)
    prompts = JSONField(default=list)  # [{"q":"Frage","a":"Antwort"}]
    
    # Einwilligung
    consent_given = BooleanField(default=False)
    consent_date = DateTimeField(blank=True, null=True)
    
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

### Swipe-Modell
```python
class Swipe(models.Model):
    from_user = ForeignKey(User)
    to_user = ForeignKey(User)
    decision = CharField(choices=[('like','Like'),('dislike','Dislike')])
    created_at = DateTimeField(auto_now_add=True)
    
    @classmethod
    def is_match(user_a, user_b) -> bool
```

### FeedbackEntry-Modell
```python
class FeedbackEntry(models.Model):
    typ = CharField(choices=[('bug','Bug'),('feature','Feature-Wunsch'),('feedback','Feedback'),('andreaskritik','Andreaskritik')])
    text = TextField()
    created_at = DateTimeField(auto_now_add=True)
    resolved = BooleanField(default=False)
```

---

## 6. API-Endpunkte (Swipe-API)

| Endpoint | Methode | Beschreibung |
|----------|---------|--------------|
| `/profiles/api/swipe/next/` | GET | Nächstes Profil für Swipe-Feed |
| `/profiles/api/swipe/action/` | POST | Like/Dislike action |
| `/profiles/api/swipe/batch/` | GET | Batch-Profile laden |
| `/profiles/api/me/` | GET | Eigenes Profil (JSON) |
| `/profiles/api/matches/` | GET | Match-Liste (JSON) |

### Swipe Action Payload
```json
POST /profiles/api/swipe/action/
{
  "profile_id": 42,
  "action": "like"  // oder "dislike"
}
```

---

## 7. Authentifizierung

### Cloudflare Access Integration
**Kein lokaler Django-Login mehr!** Alle Auth-Routen (`/accounts/login/`) liefern **404**.

#### Flow
1. User ruft `sdw-connect.kochlab.net` auf
2. Cloudflare Access prüft CF-Authorization-Cookie
3. Bei gültigem Cookie: JWT-Token im Header `Cf-Access-Jwt-Assertion`
4. Django Middleware (`cloudflare_middleware.py`) validiert JWT
5. Bei fehlendem/ungültigem Header: sofortiger Logout + Session-Flush

#### Middleware-Logik
```python
class CloudflareAccessMiddleware:
    def __call__(self, request):
        jwt_token = request.META.get('HTTP_CF_ACCESS_JWT_ASSERTION')
        if not jwt_token:
            logout(request)
            request.session.flush()
            return redirect('/')
        # JWT validieren + User erstellen/aktualisieren
```

#### Settings
```python
LOGIN_URL = '/'              # Kein Django-Login → CF Access
LOGIN_REDIRECT_URL = '/profiles/'
LOGOUT_REDIRECT_URL = '/'
```

#### Admin-Zugriff
- `/admin/` → 302 Redirect (kein lokaler Zugriff)
- Admin nur über Cloudflare Access + Django-Superuser-Status

---

## 8. Deployment

### Docker Compose
```yaml
services:
  web:
    build: .
    container_name: stipconnect_web
    volumes:
      - ./db.sqlite3:/app/db.sqlite3
      - ./media:/app/media
      - ./static:/app/staticfiles
    environment:
      - DJANGO_SETTINGS_MODULE=stipconnect.settings
      - CF_ACCESS_TEAM_DOMAIN=...
      - CF_ACCESS_AUD_TAG=...
    command: gunicorn stipconnect.wsgi:application -b 0.0.0.0:8000
```

### Build & Deploy
```bash
cd /home/laurensmain/stip-dating
docker compose build web
docker compose up -d --force-recreate web
```

### Wichtige Docker-Constraints
- **Tunnel-Service** muss `http://172.17.0.1:8081` nutzen (Docker Bridge IP), NIEMALS `localhost`
- Container läuft im `bridge`-Netzwerk, nicht `host`
- SQLite: `alter` ist reserved word → in raw SQL immer `"alter"` quoten

### Caddy-Konfiguration
```
:80 {
    handle /media/* {
        root * /srv
        file_server
    }
    handle /static/* {
        root * /srv
        file_server
    }
    handle {
        reverse_proxy web:8000
    }
    encode gzip
    header -Server
}
```

### Port-Mapping
| Extern | Intern | Service |
|--------|--------|---------|
| 8081 | 8000 | Django (Docker Bridge) |
| 80 | 80 | Caddy (innerhalb Compose) |

---

## 9. Entwicklungs-Setup

### Lokale Entwicklung
```bash
# Voraussetzungen
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Environment
export DJANGO_SETTINGS_MODULE=stipconnect.settings
export CF_ACCESS_TEAM_DOMAIN=your-team.cloudflareaccess.com
export CF_ACCESS_AUD_TAG=your-aud-tag

# Datenbank
python manage.py migrate
python manage.py runserver
```

### Docker-Entwicklung
```bash
docker compose build web
docker compose up -d web
# Logs
docker logs -f stipconnect_web
```

### Migrationen
```bash
python manage.py makemigrations profiles
python manage.py migrate
```

---

## 10. Autonomer Coding-Agent (Hermes)

### Cronjob
- **ID:** `e4d2f24e9761`
- **Intervall:** Alle 15 Minuten
- **Task:** Implementiert Django-Features autonom basierend auf Kanban-Board `sdw-dating`
- **Script:** `~/.hermes/scripts/stipconnect_autonomous.py`

### Claude Code Delegation
Hermes kann Aufgaben an Claude Code delegieren:
```bash
# Print Mode (One-Shot)
claude -p "Fix den Foto-Upload in profiles/views.py" \
  --allowedTools "Read,Edit" \
  --max-turns 10 \
  --workdir /home/laurensmain/stip-dating

# Interactive Mode (tmux)
tmux new-session -d -s coding -x 140 -y 40
tmux send-keys -t coding 'cd /home/laurensmain/stip-dating && claude' Enter
```

---

## 11. Sicherheit

### Maßnahmen
| Maßnahme | Status |
|----------|--------|
| Cloudflare Access (JWT) | ✅ Alle Requests |
| Kein lokaler Login | ✅ `/accounts/login/` → 404 |
| Session-Flush bei ungültigem JWT | ✅ Middleware |
| Keine Registrierung | ✅ Nur CF-Access-User |
| Admin-Lockdown | ✅ 302 Redirect |
| CSRF-Protection | ✅ Django-Standard |
| Privacy-First | ✅ Keine Daten an OpenRouter |

### Tier-1-Daten (Vivi, Coaching, Finanzen)
- **NIE** via OpenRouter
- **AUSSCHLIESSLICH** Ollama Cloud (no-retention)
- Voice-Input: Lokales Whisper (Port 8085), nie Cloud-STT

---

## 12. Bekannte Bugs & TODOs

### Aktive Bugs
| Bug | Priorität | Status |
|-----|-----------|--------|
| Profilfoto-Upload persistiert nicht | 🔴 Hoch | Fix in Arbeit |
| Caddy static/media Serving | 🟡 Mittel | Prüfen |
| Container-Neustart Datenverlust | 🟡 Mittel | Volume-Mount OK? |

### TODO-Liste
- [ ] Upload-Handler in `profiles/views.py` prüfen
- [ ] `MEDIA_ROOT` + `MEDIA_URL` in `settings.py` verifizieren
- [ ] Docker-Volume-Bindung für `media/` testen
- [ ] Nginx/Caddy Body-Size-Limit prüfen
- [ ] `photo` vs `photos` Feld-Konsistenz (Template + API)
- [ ] E2E-Upload-Test durchführen
- [ ] Doku-Sync automatisieren (dieses File)

---

## 13. Kontakt & Verantwortlich

| Rolle | Kontakt |
|-------|---------|
| Product Owner | Laurens Koch |
| DevOps / Server | Hermes Agent (autonom) |
| Coding-Agent | Claude Code (on demand) |
| Domain | sdw-connect.kochlab.net |

---

## 14. Changelog

### 2026-06-12
- ✅ Cloudflare Access Middleware hart implementiert
- ✅ Lokale Django-auth-URLs entfernt (`/accounts/login/` → 404)
- ✅ `photo` ImageField zu Profile-Modell hinzugefügt
- ✅ `ProfileForm` auf `photo` statt `photos` umgestellt
- ✅ Templates: `photo.url` als Primary, `photos.0` als Fallback (browse.html, detail.html, list.html)
- ✅ Caddyfile: `/media/*` und `/static/*` korrekt auf `/srv` geroutet
- ✅ Upload-Handler verifiziert: Dateien landen in `/app/media/` und persistieren auf Host
- ✅ Docker-Container rebuild + recreate erfolgreich
- 📝 Dokumentation erstellt und in Nextcloud synchronisiert

### 2026-06-11
- Initialer MVP-Launch
- Browse, Swipe, Matches, Feedback
- Cloudflare Access Basis-Integration

---

*Letzte Aktualisierung: 2026-06-12 06:30 UTC*  
*Autor: Hermes Agent (autonom)*  
*Quellcode: `/home/laurensmain/stip-dating/` | Sync: `Nextcloud/Startup/SDW Datingapp Projekt/`*

---

## 15. Weitere Dokumente

| Dokument | Inhalt |
|----------|--------|
| `HANDOVER_GUIDE.md` | **KOMPLETTER GUIDE:** Alle Dateien, Bugs, Fixes, Deployment, Tests, Constraints, Checkliste |
| `Dokumentation.md` | Technische Doku (Stack, API, Auth, Schema) |
| `CLAUDE.md` | Claude Code Kontext (autonomer Coding-Agent) |
| `Business_Kosten_Lohnenswert.md` | Kosten, Monetarisierung, ROI, Risiken, KPIs |
| `Infrastructure_Hosting.md` | Was läuft wo — vollständige Infrastructure Map |
| `README.md` | Projekt-README (kurz) |
| `DATENSCHUTZ.md` | Datenschutzerklärung |
| `BETA_EINLADUNG.md` | Einladungstext für Beta-Tester |
| `LAUNCH_ANNOUNCEMENT.md` | Launch-Ankündigung |
| `TUNNEL.md` | Cloudflare Tunnel Setup |
| `DOMAIN_OPTIONS.md` | Domain-Vergleich |
| `PWA_STATUS.md` | Progressive Web App Status |
| `MASTER_PROMPT.md` | Master-Prompt für Claude Code |
| `MVP_Status_Backend.md` | MVP-Status vom 11.06. |
| `FINAL_Status_2026-06-11.md` | Final-Status vom 11.06. |
| `502_Analyse_und_Routing_Doku.md` | 502-Fehler-Analyse |
| `Statusbericht_Nacht_2026-06-11.md` | Nacht-Statusbericht |
