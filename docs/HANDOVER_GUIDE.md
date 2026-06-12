# StipConnect — VOLLSTÄNDIGER HANDOVER-GUIDE

**Für:** Claude Code / Plot Cowork / Jeder andere Entwickler  
**Stand:** 2026-06-12 06:40 UTC  
**Autor:** Hermes Agent (autonom)  
**Zweck:** Alles was gemacht wurde, alle Bugs, alle Datei-Ziele — damit jemand anderes alles perfektionieren und zurückgeben kann

---

## INHALTSVERZEICHNIS

1. [Projekt-Übersicht](#1-projekt-übersicht)
2. [Alle Dateien: Was wurde gemacht, wo sie hinkommen](#2-alle-dateien-was-wurde-gemacht-wo-sie-hinkommen)
3. [Aktuelle Bugs (bekannt)](#3-aktuelle-bugs-bekannt)
4. [Deployment-Prozess](#4-deployment-prozess)
5. [Tests](#5-tests)
6. [Wichtige Constraints](#6-wichtige-constraints)
7. [Claude-Code-Arbeitsanweisung](#7-claude-code-arbeitsanweisung)

---

## 1. PROJEKT-ÜBERSICHT

**App:** StipConnect — Dating-App für SDW-Stipendiaten (Studienstiftung des Deutschen Volkes)  
**Stack:** Django 5.2.15 + SQLite + Docker + Cloudflare Access  
**Domain:** sdw-connect.kochlab.net  
**Host:** Dein Ubuntu-Server zuhause (Braunschweig)  
**Arbeitsverzeichnis:** `/home/laurensmain/stip-dating`  
**Nextcloud-Sync:** `Nextcloud/Startup/SDW Datingapp Projekt/`

**Primärer Code-Flow:** Browse → Like → Mutual Match → Telefonnummer sichtbar. Kein Chat, kein Algorithmus, kein manuelles Approval.

---

## 2. ALLE DATEIEN: WAS WURDE GEMACHT, WO SIE HINKOMMEN

### LEGENDE
- **🆕 NEU** = Datei existierte vorher NICHT im Git
- **✏️ GEÄNDERT** = Datei wurde modifiziert (ggf. mehrfach)
- **📍 ZIEL** = Wohin die Datei gehört (immer `/home/laurensmain/stip-dating/`)
- **BESCHREIBUNG** = Was diese Datei tut

---

### 🆕 NEUE DATEIEN (untracked — müssen hinzugefügt werden)

| # | Datei | Ziel-Pfad | Beschreibung |
|---|-------|-----------|--------------|
| 1 | `profiles/decorators.py` | `profiles/decorators.py` | `@RequireApprovedMixin` — Dekorator für Views die nur approved/sichtbare Profile erlauben |
| 2 | `profiles/management/__init__.py` | `profiles/management/__init__.py` | Django Management-Command Package |
| 3 | `profiles/management/commands/__init__.py` | `profiles/management/commands/__init__.py` | Django Management-Command Package |
| 4 | `profiles/management/commands/flag_beta_testers.py` | `profiles/management/commands/flag_beta_testers.py` | Management-Command: Setzt `is_beta_tester=True` auf Usern |
| 5 | `profiles/migrations/0002_full_profile.py` | `profiles/migrations/0002_full_profile.py` | Migration: Erweitert Profile-Modell (Sprachen, Regionen, Prompts, Lifestyle, etc.) |
| 6 | `profiles/migrations/0003_matchview_swipe.py` | `profiles/migrations/0003_matchview_swipe.py` | Migration: Erstellt `Swipe`-Modell und `MatchView` |
| 7 | `profiles/migrations/0004_profile_is_beta_tester_feedbackentry_message.py` | `profiles/migrations/0004_profile_is_beta_tester_feedbackentry_message.py` | Migration: Fügt `is_beta_tester`, `FeedbackEntry`, `Message` hinzu |
| 8 | `profiles/migrations/0005_profile_photo.py` | `profiles/migrations/0005_profile_photo.py` | Migration: Fügt `photo = ImageField` zum Profile-Modell hinzu. **WICHTIG:** Diese Migration wurde mit `--fake` applied wegen SQLite-Table-Lock. Bei Neuaufsetzung der DB muss sie echt oder neu migriert werden. |
| 9 | `profiles/signals.py` | `profiles/signals.py` | Django-Signals: Automatisches Erstellen eines Profile-Objekts bei User-Erstellung |
| 10 | `profiles/swipe_models.py` | `profiles/swipe_models.py` | Zusätzliche Modelle für Swipe-Logik (ggf. redundant mit models.py) — **PRÜFEN** |
| 11 | `profiles/swipe_views.py` | `profiles/swipe_views.py` | API-Views für Swipe-Feed (JSON): `SwipeFeedView`, `SwipeActionView`, `SwipeBatchView`, `MatchListView`, `ProfileMeView` |
| 12 | `profiles/tests_matches.py` | `profiles/tests_matches.py` | Tests für Match-Funktionalität |
| 13 | `profiles/tests_swipe.py` | `profiles/tests_swipe.py` | Tests für Swipe-Funktionalität |
| 14 | `profiles/tests_tasks31_33.py` | `profiles/tests_tasks31_33.py` | Tests für spezifische Aufgaben |
| 15 | `scripts/fix_db_and_demos.py` | `scripts/fix_db_and_demos.py` | Script zur Datenbank-Reparatur und Demo-Daten-Erstellung |
| 16 | `stipconnect/cloudflare_middleware.py` | `stipconnect/cloudflare_middleware.py` | **KERN-COMPONENTE:** Validiert `Cf-Access-Jwt-Assertion` Header. Erzwingt `logout(request)` + `session.flush()` bei ungültigem/fehlendem Token. Erstellt User automatisch aus JWT-Payload. |
| 17 | `stipconnect/tests_middleware_logout.py` | `stipconnect/tests_middleware_logout.py` | Tests für Middleware-Logout-Verhalten |
| 18 | `templates/browse.html` | `templates/browse.html` | Browse-Grid-Seite: Zeigt alle Profile als Karten mit Foto + Name + Alter + Hochschule + Studienfach |
| 19 | `templates/landing.html` | `templates/landing.html` | Landing-Page für nicht eingeloggte User: Zeigt Mock-Demo-Profile (Hardcoded) |
| 20 | `templates/mockup.html` | `templates/mockup.html` | Design-Mockup / Template-Preview |
| 21 | `templates/profiles/admin_dashboard.html` | `templates/profiles/admin_dashboard.html` | Admin-Dashboard: Zeigt Pending-Profile, Statistiken, Quick-Actions |
| 22 | `templates/profiles/admin_feedback.html` | `templates/profiles/admin_feedback.html` | Admin-Feedback-Übersicht: Liste aller Feedback-Einträge mit Resolve-Button |
| 23 | `templates/profiles/beta_waitlist.html` | `templates/profiles/beta_waitlist.html` | Beta-Waitlist-Seite für nicht-freigeschaltete User |
| 24 | `templates/profiles/browse.html` | `templates/profiles/browse.html` | **DUPLIKAT?** — Prüfen ob browse.html in `templates/` ODER `templates/profiles/` genutzt wird. Aktuell wird `templates/browse.html` gerendert. |
| 25 | `templates/profiles/feedback_form.html` | `templates/profiles/feedback_form.html` | Feedback-Formular für Beta-Tester (Bug, Feature, Feedback, Andreaskritik) |
| 26 | `templates/profiles/matches.html` | `templates/profiles/matches.html` | Match-Liste: Zeigt Mutual-Likes mit Telefonnummer |
| 27 | `templates/profiles/swipe.html` | `templates/profiles/swipe.html` | Swipe-Interface (Tinder-Style) mit Like/Dislike |
| 28 | `templates/profiles/warteschlange.html` | `templates/profiles/warteschlange.html` | Warteschlangen-Seite für nicht-freigeschaltete Profile |
| 29 | `static/images/icon-maskable-192.png` | `static/images/icon-maskable-192.png` | PWA-Icon (maskable, 192px) |
| 30 | `static/images/icon-maskable-512.png` | `static/images/icon-maskable-512.png` | PWA-Icon (maskable, 512px) |
| 31 | `static/images/screenshot-narrow.png` | `static/images/screenshot-narrow.png` | PWA-Screenshot (narrow) |
| 32 | `static/images/splash-*.png` (9 Dateien) | `static/images/splash-*.png` | iOS/Android Splash Screens in verschiedenen Größen |

**Nicht relevanter Müll (NICHT committen):**
- `db.sqlite3.backup-*` (12+ Dateien) — Datenbank-Backups, gehören NICHT ins Git
- `1` — Leere Datei (Fehler)
- `.pytest_cache/` — Cache-Verzeichnis

---

### ✏️ GEÄNDERTE DATEIEN (modified — müssen geprüft/committet werden)

| # | Datei | Ziel-Pfad | Was wurde geändert | Status |
|---|-------|-----------|-------------------|--------|
| 1 | `Caddyfile` | `Caddyfile` | `/media/*` und `/static/*` auf `/srv` geroutet (statt `/srv/media` und `/srv/static`). Docker-Volume mountet `./media` → `/srv/media` und `./staticfiles` → `/srv/static`. Der `root * /srv` + `file_server` muss dann `/srv/media` und `/srv/static` erreichen. **ACHTUNG:** Wir haben das hin- und hergepatcht. Aktueller Stand: `root * /srv` für beide. | ⚠️ PRÜFEN |
| 2 | `docker-compose.yml` | `docker-compose.yml` | Port-Mapping `8081:80` für Caddy. Container `web`, `caddy`, `cloudflared`. **WICHTIG:** `cloudflared` hat `network_mode: host`, alle anderen `networks: stipconnect` (bridge). Tunnel erreicht Caddy via `localhost:8081`. | ✅ OK |
| 3 | `profiles/admin.py` | `profiles/admin.py` | Admin-Konfiguration für Profile, FeedbackEntry. Custom Admin-Dashboard-Views. | ✅ OK |
| 4 | `profiles/apps.py` | `profiles/apps.py` | App-Config, vermutlich Signals registriert. | ✅ OK |
| 5 | `profiles/forms.py` | `profiles/forms.py` | `ProfileForm` — enthält jetzt `photo` Feld (ImageField mit ClearableFileInput). `FeedbackForm` für Beta-Feedback. **WICHTIG:** `photo` Feld nutzt `ClearableFileInput` als Widget. | ✅ OK |
| 6 | `profiles/models.py` | `profiles/models.py` | **MASSIVE ÄNDERUNGEN:**<br>- `Profile`-Modell erweitert: `regionen`, `sprachen`, `quote`, `about`, `looking_for`, `trinken`, `rauchen`, `interests`, `prompts`, `consent_given`, `consent_date`, etc.<br>- `photo = ImageField(upload_to='photos/%Y/%m/', blank=True, null=True)` **NEU**<br>- `photos = JSONField(default=list)` **ALT/DEPRECATED** — JSON-Array mit URLs<br>- `Swipe`-Modell hinzugefügt<br>- `FeedbackEntry`-Modell hinzugefügt<br>- `Message`-Modell hinzugefügt (Chat? — **PRÜFEN** ob genutzt) | ⚠️ PRÜFEN |
| 7 | `profiles/tests.py` | `profiles/tests.py` | Tests für Profile, Swipe, Feedback. Erweitert. | ✅ OK |
| 8 | `profiles/urls.py` | `profiles/urls.py` | URL-Patterns für Swipe-API (`/api/swipe/*`), Matches, Feedback, Admin-Dashboard, Beta-Waitlist. | ✅ OK |
| 9 | `profiles/views.py` | `profiles/views.py` | `ProfileListView`, `ProfileDetailView`, `ProfileUpdateView`, `ProfileDeleteView`, `ConsentSubmitView`, `MockupView`, `AdminDashboardView`, `AdminFeedbackView`, `BetaWaitlistView`. **WICHTIG:** `ProfileUpdateView` nutzt `ProfileForm` — Upload via `request.FILES` sollte via Django-Generic-View automatisch funktionieren (kein expliziter Handler nötig). | ✅ OK |
| 10 | `static/css/custom.css` | `static/css/custom.css` | Custom CSS für Swipe-Interface, Browse-Grid, Profile-Cards, Animations. | ✅ OK |
| 11 | `static/js/sw.js` | `static/js/sw.js` | Service Worker für PWA (Progressive Web App). Caching-Strategie, Offline-Support. | ✅ OK |
| 12 | `static/manifest.json` | `static/manifest.json` | PWA-Manifest: Name, Icons, Theme, Display-Mode. | ✅ OK |
| 13 | `stipconnect/middleware.py` | `stipconnect/middleware.py` | Alte Middleware (wahrscheinlich). **PRÜFEN:** Ob noch in `settings.py` eingetragen oder nur `cloudflare_middleware.py` genutzt wird. | ⚠️ PRÜFEN |
| 14 | `stipconnect/settings.py` | `stipconnect/settings.py` | **WICHTIGE ÄNDERUNGEN:**<br>- `LOGIN_URL = '/'` (kein Django-Login mehr)<br>- `LOGIN_REDIRECT_URL = '/profiles/'`<br>- `LOGOUT_REDIRECT_URL = '/'`<br>- `CF_ACCESS_LOGOUT_URL` für Cloudflare Access Logout<br>- Security Headers (`SECURE_BROWSER_XSS_FILTER`, etc.)<br>- `MEDIA_URL = '/media/'`, `MEDIA_ROOT = BASE_DIR / 'media'` | ✅ OK |
| 15 | `stipconnect/tests.py` | `stipconnect/tests.py` | Tests für Settings, URLs, Middleware. | ✅ OK |
| 16 | `stipconnect/urls.py` | `stipconnect/urls.py` | **KRITISCHE ÄNDERUNG:** `path('accounts/', include('django.contrib.auth.urls'))` wurde **ENTFERNT**. Lokaler Django-Login liefert jetzt 404. Nur Cloudflare Access möglich. | ✅ OK |
| 17 | `templates/base.html` | `templates/base.html` | Basis-Template mit Navigation, PWA-Meta-Tags, Service-Worker-Registrierung. | ✅ OK |
| 18 | `templates/profiles/detail.html` | `templates/profiles/detail.html` | Profil-Detail-Seite: Hero-Foto, About, Lifestyle, Prompts, Like-Button, Telefonnummer (nur bei Mutual Match). **WICHTIG:** Nutzt `profile.photo.url` als Primary, `profile.photos.0` als Fallback. | ✅ OK |
| 19 | `templates/profiles/list.html` | `templates/profiles/list.html` | Profil-Liste (für Admin/Browse). Nutzt `profile.photo.url` als Primary, `profile.photos.0` als Fallback. | ✅ OK |

---

## 3. AKTUELLE BUGS (BEKANNT)

### 🔴 KRITISCHE BUGS

| # | Bug | Wo | Beschreibung | Fix-Status |
|---|-----|-----|--------------|------------|
| 1 | **Profilfoto-Upload** | `profiles/models.py`, `profiles/forms.py`, Templates | `photo` ImageField existiert seit Migration 0005. Upload landet physisch in `/app/media/photos/%Y/%m/` (Container) und persistiert auf Host. **ABER:** Es gibt keine Bildvorschau im `edit.html` Template. User sieht nicht welches Bild aktuell gesetzt ist. | ⚠️ TEIL-FIX |
| 2 | **Migration 0005 ist `--fake`** | `profiles/migrations/0005_profile_photo.py` | SQLite erlaubte kein `ALTER TABLE ADD COLUMN` bei laufendem Container. Migration wurde `--fake` applied. **RISIKO:** Wenn DB neu aufgebaut wird, fehlt die `photo`-Spalte physisch. | ⚠️ WORKAROUND |
| 3 | **Template-Duplikate** | `templates/browse.html` vs `templates/profiles/browse.html` | Zwei Browse-Templates existieren. `templates/browse.html` wird von `ProfileListView` gerendert. `templates/profiles/browse.html` ist ungenutzt. **EINES LÖSCHEN.** | 🔴 OFFEN |
| 4 | **`swipe_models.py` vs `models.py`** | `profiles/swipe_models.py` | Swipe-Modelle sind wahrscheinlich DUPLIKAT in `models.py` UND `swipe_models.py`. **PRÜFEN:** Welche Datei wird genutzt? Einheitlich machen. | 🔴 OFFEN |

### 🟡 MEDIUM BUGS

| # | Bug | Wo | Beschreibung | Fix-Status |
|---|-----|-----|--------------|------------|
| 5 | **PWA offline** | `static/js/sw.js` | Service Worker hat Caching-Logik, aber nicht getestet ob Offline-Modus funktioniert. | 🔴 OFFEN |
| 6 | **Splash Screens** | `static/images/splash-*.png` | 9 Splash-Screens für iOS erstellt, aber nicht verifiziert ob sie korrekt im Manifest referenziert sind. | 🔴 OFFEN |
| 7 | **`Message` Modell ungenutzt?** | `profiles/models.py` | `Message`-Modell existiert (für Chat?), aber es gibt keine Chat-Views oder Templates. **PRÜFEN:** Entweder entfernen oder Chat-Feature implementieren. | 🔴 OFFEN |
| 8 | **`middleware.py` vs `cloudflare_middleware.py`** | `stipconnect/middleware.py` | Beide existieren. Prüfen welche in `settings.py` eingetragen ist. Vermutlich nur `cloudflare_middleware.py` aktiv. | 🔴 OFFEN |
| 9 | **Foto-Vorschau in edit.html** | `templates/profiles/edit.html` | Keine Bildvorschau wenn `profile.photo` existiert. User sieht nur ClearableFileInput-Widget ohne Vorschau. | 🔴 OFFEN |

### 🟢 NIEDRIG / COSMETIC

| # | Bug | Wo | Beschreibung | Fix-Status |
|---|-----|-----|--------------|------------|
| 10 | **`.claude/settings.json`** | `.claude/settings.json` | Claude-Code-Einstellungen. Sollte nicht ins Git. In `.gitignore` aufnehmen. | 🔴 OFFEN |
| 11 | **Leere Datei `1`** | `1` | Wahrscheinlich Fehler bei einem Command. Löschen. | 🔴 OFFEN |
| 12 | **DB-Backups im Git** | `db.sqlite3.backup-*` | 12+ Backup-Dateien im Projekt-Root. Sollten ins `.gitignore` oder in `backups/`-Ordner. | 🔴 OFFEN |

---

## 4. DEPLOYMENT-PROZESS

### 4.1 Voraussetzungen

```bash
# Am Server (SSH oder lokal)
ssh laurensmain@<server-ip>
cd /home/laurensmain/stip-dating
```

### 4.2 Standard-Deployment

```bash
# 1. Code aktualisieren (oder Dateien kopieren)
cd /home/laurensmain/stip-dating

# 2. Docker Image neu bauen
docker compose build web

# 3. Container neu starten (ohne Datenverlust)
docker compose up -d --force-recreate web

# 4. Caddy neu starten (Config-Änderungen)
docker compose restart caddy

# 5. Logs prüfen
docker logs --tail 20 stipconnect_web
```

### 4.3 Mit Migrationen (VORSICHT)

```bash
# Nur wenn neue Migrationen existieren:
docker compose run --rm web python manage.py migrate

# DANN neu bauen:
docker compose up -d --force-recreate web
```

### 4.4 Static Files neu sammeln

```bash
# Wenn CSS/JS/Images geändert wurden:
docker compose run --rm web python manage.py collectstatic --noinput
```

### 4.5 Vollständiges Rebuild (nur bei Problemen)

```bash
# ALLES neu bauen:
docker compose down
docker compose build --no-cache web caddy
docker compose up -d
```

### 4.6 Wichtige Docker-Constraints

- **Tunnel:** `cloudflared` nutzt `network_mode: host` → erreicht Caddy via `localhost:8081`
- **Web:** `stipconnect_web` läuft im `bridge`-Netzwerk → für Hermes/Tunnel: `http://172.17.0.1:8081` (nicht `localhost`)
- **Volumes:** `db.sqlite3`, `media/`, `staticfiles/` sind auf Host gemountet → Container-Neustart = kein Datenverlust
- **SQLite:** `alter` ist reserved word → in raw SQL immer `"alter"` quoten

---

## 5. TESTS

### 5.1 Test-Command

```bash
# Im Container:
docker compose run --rm web python manage.py test

# Oder lokal (mit venv):
python manage.py test
```

### 5.2 Vorhandene Test-Dateien

| Datei | Was wird getestet |
|-------|-------------------|
| `profiles/tests.py` | Profile-Model, Form, Views |
| `profiles/tests_swipe.py` | Swipe-API (Like, Dislike, Match) |
| `profiles/tests_matches.py` | Match-Liste, Telefonnummer-Sichtbarkeit |
| `profiles/tests_tasks31_33.py` | Spezifische Aufgaben-Tests |
| `stipconnect/tests.py` | Settings, URLs |
| `stipconnect/tests_middleware_logout.py` | Middleware-Logout bei ungültigem JWT |

### 5.3 Manuelle Tests (nach jedem Deploy)

```bash
# 1. Site erreichbar?
curl -s -o /dev/null -w "%{http_code}" https://sdw-connect.kochlab.net/
# Erwartet: 302 (Cloudflare Access Redirect) oder 200 (wenn eingeloggt)

# 2. Lokaler Login blockiert?
curl -s -o /dev/null -w "%{http_code}" http://localhost:8081/accounts/login/
# Erwartet: 404

# 3. Admin blockiert?
curl -s -o /dev/null -w "%{http_code}" http://localhost:8081/admin/
# Erwartet: 302 (redirect zu CF Access)

# 4. Container läuft?
docker ps | grep stipconnect

# 5. Media-Verzeichnis beschreibbar?
docker exec stipconnect_web python -c "import os; print(os.access('/app/media', os.W_OK))"
# Erwartet: True
```

---

## 6. WICHTIGE CONSTRAINTS

### 6.1 Technische Constraints

| Constraint | Bedeutung |
|------------|-----------|
| **Kein lokaler Django-Login** | `/accounts/login/` muss 404 liefern. Nur CF Access. |
| **Cloudflare Access JWT** | Jeder Request braucht `Cf-Access-Jwt-Assertion` Header. Middleware prüft dies. |
| **SQLite nur** | Kein PostgreSQL. `ALTER TABLE` in SQLite ist begrenzt. |
| **Docker Bridge** | Für Tunnel/externe Zugriffe: `http://172.17.0.1:8081`, nie `localhost` |
| **Privacy-First** | Keine Tier-1-Daten (Vivi, Coaching, Finanzen) via OpenRouter. Nur Ollama Cloud. |
| **Autonom** | Hermes Agent darf autonom deployen. Keine manuellen Approvals nötig. |

### 6.2 Business Constraints

| Constraint | Bedeutung |
|------------|-----------|
| **Ultra-minimal** | Kein Chat, kein Algorithmus, kein manuelles Approval |
| **Browse → Like → Mutual → Phone** | Das ist der ENTIRE Flow. Nichts mehr. |
| **SDW-only** | Nur Stipendiaten. Keine externen Nutzer. |
| **Kostenlos** | Aktuell kein Premium-Tier aktiv. |

---

## 7. CLAUDE-CODE-ARBEITSANWEISUNG

### 7.1 Setup für Claude Code

```bash
# 1. In Projekt-Ordner wechseln
cd /home/laurensmain/stip-dating

# 2. Claude Code starten
claude

# 3. Im Prompt:
# "Siehe CLAUDE.md im Projekt-Root für Kontext.
#  Siehe Dokumentation.md für Architektur.
#  Siehe Handover-Guide.md für aktuelle Bugs und Datei-Ziele."
```

### 7.2 Was Claude Code machen soll

1. **Fix #1:** Template-Duplikate (`browse.html` vs `profiles/browse.html`) auflösen
2. **Fix #2:** `swipe_models.py` vs `models.py` — Swipe-Modelle deduplizieren
3. **Fix #3:** `middleware.py` vs `cloudflare_middleware.py` — cleanup
4. **Fix #4:** Bildvorschau in `templates/profiles/edit.html` hinzufügen
5. **Fix #5:** `Message`-Modell entweder nutzen oder entfernen
6. **Fix #6:** PWA-Splash-Screens im Manifest verifizieren
7. **Fix #7:** `.gitignore` aufräumen (Backups, `.claude/`, `1`)

### 7.3 Was Claude Code NICHT machen soll

- ❌ KEINEN Chat implementieren (gegen Ultra-minimal-Constraint)
- ❌ KEINEN Algorithmus bauen
- ❌ KEINE OAuth-Provider hinzufügen (nur CF Access)
- ❌ KEINE externen APIs für Tier-1-Daten nutzen
- ❌ KEIN `db.sqlite3` löschen oder migrieren ohne Backup

### 7.4 Nach Claude Code: Deployment

```bash
# Nach allen Änderungen:
cd /home/laurensmain/stip-dating
docker compose build web
docker compose up -d --force-recreate web
docker compose restart caddy

# Tests laufen lassen:
docker compose run --rm web python manage.py test

# Nextcloud sync:
rsync -av --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' --exclude='node_modules' \
  /home/laurensmain/stip-dating/ "/home/laurensmain/Nextcloud/Startup/SDW Datingapp Projekt/"
```

---

## 8. DATEI-LISTE FÜR PLOT COWORK / GIT COMMIT

### Was committet werden muss (neu + geändert):

```bash
# NEUE DATEIEN (untracked):
git add profiles/decorators.py
git add profiles/management/
git add profiles/migrations/0002_full_profile.py
git add profiles/migrations/0003_matchview_swipe.py
git add profiles/migrations/0004_profile_is_beta_tester_feedbackentry_message.py
git add profiles/migrations/0005_profile_photo.py
git add profiles/signals.py
git add profiles/swipe_models.py
git add profiles/swipe_views.py
git add profiles/tests_matches.py
git add profiles/tests_swipe.py
git add profiles/tests_tasks31_33.py
git add scripts/fix_db_and_demos.py
git add stipconnect/cloudflare_middleware.py
git add stipconnect/tests_middleware_logout.py
git add templates/browse.html
git add templates/landing.html
git add templates/mockup.html
git add templates/profiles/admin_dashboard.html
git add templates/profiles/admin_feedback.html
git add templates/profiles/beta_waitlist.html
git add templates/profiles/browse.html
git add templates/profiles/feedback_form.html
git add templates/profiles/matches.html
git add templates/profiles/swipe.html
git add templates/profiles/warteschlange.html
git add static/images/icon-maskable-*.png
git add static/images/screenshot-narrow.png
git add static/images/splash-*.png

# GEÄNDERTE DATEIEN:
git add Caddyfile
git add docker-compose.yml
git add profiles/admin.py
git add profiles/apps.py
git add profiles/forms.py
git add profiles/models.py
git add profiles/tests.py
git add profiles/urls.py
git add profiles/views.py
git add static/css/custom.css
git add static/js/sw.js
git add static/manifest.json
git add stipconnect/middleware.py
git add stipconnect/settings.py
git add stipconnect/tests.py
git add stipconnect/urls.py
git add templates/base.html
git add templates/profiles/detail.html
git add templates/profiles/list.html

# NICHT committen (in .gitignore aufnehmen):
# db.sqlite3.backup-*
# .pytest_cache/
# .claude/
# 1
# __pycache__/
# *.pyc
```

---

## 9. SCHNELL-REFERENZ: WOHIN JEDE DATEI GEHÖRT

### Django-Projekt (`stipconnect/`)

```
stipconnect/
├── __init__.py              # (original, unverändert)
├── settings.py              # ✅ GEÄNDERT — Auth, Security, MEDIA
├── urls.py                  # ✅ GEÄNDERT — auth-URLs ENTFERNT
├── wsgi.py                  # (original, unverändert)
├── asgi.py                  # (original, unverändert)
├── middleware.py            # ⚠️ PRÜFEN — ob noch aktiv oder deprecated
└── cloudflare_middleware.py # 🆕 NEU — CF Access JWT-Validierung
```

### Haupt-App (`profiles/`)

```
profiles/
├── __init__.py              # (original)
├── models.py                # ✅ GEÄNDERT — Profile, Swipe, FeedbackEntry, Message
├── views.py                 # ✅ GEÄNDERT — Profile CRUD, Admin, Beta-Waitlist
├── swipe_views.py           # 🆕 NEU — Swipe-API (JSON)
├── forms.py                 # ✅ GEÄNDERT — ProfileForm (mit photo), FeedbackForm
├── urls.py                  # ✅ GEÄNDERT — Swipe-API-URLs, Feedback, Admin
├── admin.py                 # ✅ GEÄNDERT — Custom Admin
├── tests.py                 # ✅ GEÄNDERT — Erweiterte Tests
├── tests_swipe.py           # 🆕 NEU — Swipe-Tests
├── tests_matches.py         # 🆕 NEU — Match-Tests
├── tests_tasks31_33.py     # 🆕 NEU — Task-Tests
├── decorators.py            # 🆕 NEU — @RequireApprovedMixin
├── signals.py               # 🆕 NEU — Auto-Profile bei User-Erstellung
├── swipe_models.py          # 🆕 NEU — Swipe-Modelle (DUP?)
├── apps.py                  # ✅ GEÄNDERT — Signals registriert
└── migrations/
    ├── __init__.py          # (original)
    ├── 0001_initial.py      # (original)
    ├── 0002_full_profile.py # 🆕 NEU — Full Profile Migration
    ├── 0003_matchview_swipe.py # 🆕 NEU — Swipe-Modelle
    ├── 0004_profile_is_beta_tester_feedbackentry_message.py # 🆕 NEU — Beta, Feedback, Message
    └── 0005_profile_photo.py # 🆕 NEU — ImageField (⚠️ --fake applied)
```

### Templates (`templates/`)

```
templates/
├── base.html                # ✅ GEÄNDERT — PWA-Meta, Navigation
├── landing.html             # 🆕 NEU — Landing-Page mit Mock-Daten
├── mockup.html              # 🆕 NEU — Design-Mockup
├── browse.html              # 🆕 NEU — Browse-Grid (genutzt von ProfileListView)
└── profiles/
    ├── detail.html          # ✅ GEÄNDERT — Profil-Detail mit photo+photos Fallback
    ├── edit.html            # ✅ GEÄNDERT — Profil-Edit mit photo Upload
    ├── list.html            # ✅ GEÄNDERT — Profil-Liste mit photo+photos Fallback
    ├── swipe.html           # 🆕 NEU — Swipe-Interface
    ├── matches.html         # 🆕 NEU — Match-Liste
    ├── admin_dashboard.html # 🆕 NEU — Admin-Übersicht
    ├── admin_feedback.html  # 🆕 NEU — Feedback-Übersicht
    ├── feedback_form.html   # 🆕 NEU — Feedback-Formular
    ├── beta_waitlist.html   # 🆕 NEU — Beta-Waitlist
    ├── browse.html          # 🆕 NEU — DUPLIKAT? (ungünstig)
    └── warteschlange.html   # 🆕 NEU — Warteschlange
```

### Static Assets (`static/`)

```
static/
├── css/
│   └── custom.css           # ✅ GEÄNDERT — Swipe, Browse Styles
├── js/
│   └── sw.js                # ✅ GEÄNDERT — Service Worker
├── images/
│   ├── icon-maskable-192.png # 🆕 NEU — PWA Icon
│   ├── icon-maskable-512.png # 🆕 NEU — PWA Icon
│   ├── screenshot-narrow.png # 🆕 NEU — PWA Screenshot
│   └── splash-*.png (9)     # 🆕 NEU — iOS Splash Screens
└── manifest.json            # ✅ GEÄNDERT — PWA Manifest
```

### Docker & Config

```
├── Dockerfile               # (original, unverändert)
├── docker-compose.yml       # ✅ GEÄNDERT — 8081:80, Volumes, Networks
├── Caddyfile                # ✅ GEÄNDERT — /media/* und /static/* auf /srv
├── .env                     # (original, NICHT ins Git!)
├── .env.template            # (original)
├── .gitignore               # (original — muss erweitert werden)
└── requirements.txt         # (original, unverändert)
```

### Dokumentation (Nextcloud)

```
Nextcloud/Startup/SDW Datingapp Projekt/
├── Dokumentation.md                   # ✅ GEÄNDERT — Technische Doku
├── CLAUDE.md                          # ✅ GEÄNDERT — Claude Code Kontext
├── Business_Kosten_Lohnenswert.md     # 🆕 NEU — Kosten, ROI
├── Infrastructure_Hosting.md          # 🆕 NEU — Was läuft wo
├── README.md                          # (vorhanden)
├── DATENSCHUTZ.md                     # (vorhanden)
├── BETA_EINLADUNG.md                  # (vorhanden)
├── LAUNCH_ANNOUNCEMENT.md             # (vorhanden)
├── TUNNEL.md                          # (vorhanden)
├── DOMAIN_OPTIONS.md                  # (vorhanden)
├── PWA_STATUS.md                      # (vorhanden)
├── MASTER_PROMPT.md                   # (vorhanden)
├── MVP_Status_Backend.md              # (vorhanden)
├── FINAL_Status_2026-06-11.md         # (vorhanden)
├── 502_Analyse_und_Routing_Doku.md    # (vorhanden)
└── Statusbericht_Nacht_2026-06-11.md  # (vorhanden)
```

---

## 10. CHECKLISTE: VOR DEM NÄCHSTEN DEPLOY

- [ ] Alle Tests laufen durch: `docker compose run --rm web python manage.py test`
- [ ] Keine Template-Duplikate mehr
- [ ] Keine Modell-Duplikate mehr
- [ ] `middleware.py` aufgeräumt (nur eine Middleware aktiv)
- [ ] Bildvorschau in `edit.html` vorhanden
- [ ] PWA-Manifest validiert (alle Icons/Screenshots referenziert)
- [ ] `.gitignore` aktualisiert (Backups, `.claude/`, `1`)
- [ ] Keine `db.sqlite3.backup-*` im Git
- [ ] Migration 0005 ist echt (nicht `--fake`) ODER DB-Schema manuell verifiziert
- [ ] Caddyfile: `/media/*` und `/static/*` korrekt geroutet
- [ ] `cloudflared` läuft und erreicht Caddy auf `localhost:8081`
- [ ] Site erreichbar: `curl https://sdw-connect.kochlab.net/`
- [ ] Lokaler Login blockiert: `curl http://localhost:8081/accounts/login/` → 404
- [ ] Nextcloud-Sync durchgeführt

---

*Letzte Aktualisierung: 2026-06-12 06:40 UTC*  
*Autor: Hermes Agent (autonom)*  
*Quellcode: `/home/laurensmain/stip-dating/`*  
*Nextcloud: `Startup/SDW Datingapp Projekt/`*
