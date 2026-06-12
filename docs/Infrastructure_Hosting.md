# StipConnect — Infrastructure Map: Was läuft wo?

Stand: 2026-06-12
Autor: Hermes Agent (autonom)

---

## 1. Übersicht

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              BENUTZER                                        │
│                         (SDW-Stipendiaten)                                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CLOFLARE EDGE (Global)                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                        │
│  │   DNS        │  │   Access     │  │   SSL/TLS    │                        │
│  │  (kostenlos) │  │  (Free Plan) │  │  (kostenlos) │                        │
│  └──────────────┘  └──────────────┘  └──────────────┘                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      CLOUDFLARE TUNNEL (cloudflared)                        │
│                    sdw-connect.kochlab.net → localhost:8081                 │
│                         (Docker Container, network_mode: host)              │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    LAURENS SERVER (Zuhause, Braunschweig)                   │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │  Ubuntu 22.04 LTS | Linux 6.8.0-110-generic | Intel i5 | 16 GB RAM     │  │
│  │  Festplatte: SSD | GPU: GTX 1060 (für lokales Whisper)                 │  │
│  │  Netzwerk: DSL/Kabel → Tailscale (VPN) → Cloudflare Tunnel            │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
              ┌───────────────────────┼───────────────────────┐
              ▼                       ▼                       ▼
┌─────────────────────────┐ ┌─────────────────────────┐ ┌─────────────────────────┐
│      DOCKER COMPOSE      │ │      DOCKER COMPOSE      │ │      DOCKER COMPOSE      │
│   ┌─────────────────┐   │ │   ┌─────────────────┐   │ │   ┌─────────────────┐   │
│   │  Caddy          │   │ │   │  Django (Gunicorn)│   │ │   │  cloudflared    │   │
│   │  Port: 8081→80  │   │ │   │  Port: 8000     │   │ │   │  network_mode:  │   │
│   │  Reverse Proxy  │   │ │   │  App-Logik      │   │ │   │  host             │   │
│   │  Static/Media   │   │ │   │  DB (SQLite)    │   │ │   │  CF Tunnel      │   │
│   └─────────────────┘   │ │   └─────────────────┘   │ │   └─────────────────┘   │
└─────────────────────────┘ └─────────────────────────┘ └─────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          DATEISYSTEM (Host)                                  │
│  /home/laurensmain/stip-dating/                                              │
│  ├── db.sqlite3          ← SQLite-Datenbank                                │
│  ├── media/              ← Profilfotos (Docker-Volume gemountet)            │
│  ├── staticfiles/        ← Static Assets (CSS, JS)                           │
│  └── templates/          ← HTML-Templates                                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Detaillierte Komponenten

### 2.1 Domain & DNS

| Attribut | Wert |
|----------|------|
| **Domain** | `sdw-connect.kochlab.net` |
| **Registrar** | Cloudflare (kostenlos, inkl. DNS) |
| **DNS-Record** | CNAME → Cloudflare Tunnel |
| **SSL/TLS** | Cloudflare Origin CA (Full Strict) |
| **Kosten** | €0 |

**Wichtig:** Die Domain ist eine Subdomain von `kochlab.net` (dein persönliches Domain-Portfolio). Der DNS-Record zeigt nicht auf eine IP, sondern auf den Cloudflare Tunnel.

---

### 2.2 Cloudflare Access (Authentifizierung)

| Attribut | Wert |
|----------|------|
| **Service** | Cloudflare Access (Zero Trust) |
| **Plan** | Free (0-50 Benutzer) |
| **Login-Methode** | Magic Link (E-Mail), Google, GitHub |
| **Session** | JWT-Token im Header `Cf-Access-Jwt-Assertion` |
| **Kosten** | €0 |

**Flow:**
1. User ruft `sdw-connect.kochlab.net` auf
2. Kein gültiges CF-Access-Cookie → Redirect zu Cloudflare-Login-Seite
3. Login via E-Mail-Link → JWT-Token wird gesetzt
4. Bei jedem Request: Django Middleware prüft `Cf-Access-Jwt-Assertion`
5. Ungültig/kein Token → Sofortiger Logout + Session-Flush

**Wichtig:** Kein lokaler Django-Login mehr. `/accounts/login/` liefert 404.

---

### 2.3 Cloudflare Tunnel (cloudflared)

| Attribut | Wert |
|----------|------|
| **Service** | `cloudflared` (Cloudflare Tunnel) |
| **Container** | `stipconnect_tunnel` |
| **Netzwerk** | `network_mode: host` (direkter Host-Zugriff) |
| **Config** | `/home/laurensmain/.cloudflared/stipconnect.yml` |
| **Credentials** | `/home/laurensmain/.cloudflared/08d783d9-*.json` |
| **Kosten** | €0 |

**Funktion:** Verbindet den lokalen Server (Port 8081) sicher mit Cloudflare Edge — keine öffentliche IP nötig, keine Firewall-Regeln.

**Wichtig:** Container läuft im `host`-Netzwerk-Modus. Tunnel erreicht Caddy via `localhost:8081`.

---

### 2.4 Reverse Proxy: Caddy

| Attribut | Wert |
|----------|------|
| **Service** | Caddy 2 (Alpine Linux) |
| **Container** | `stipconnect_caddy` |
| **Port** | `:80` (intern) → `:8081` (extern via Docker) |
| **Image** | `caddy:2-alpine` |
| **Config** | `Caddyfile` (Host-gemountet) |
| **Kosten** | €0 |

**Routing-Logik:**
```
/media/*     → /srv/           (Host: ./media/ → Container: /srv/)
/static/*    → /srv/           (Host: ./staticfiles/ → Container: /srv/)
/*           → reverse_proxy web:8000  (Django-App)
```

**Wichtig:** `/srv` ist der Container-Pfad. Via Docker-Volume wird `./media` auf `/srv/media` und `./staticfiles` auf `/srv/static` gemountet. Der `root * /srv` + `file_server` serviert dann die Dateien.

---

### 2.5 App-Server: Django + Gunicorn

| Attribut | Wert |
|----------|------|
| **Framework** | Django 5.2.15 |
| **WSGI-Server** | Gunicorn 26.0.0 |
| **Python** | 3.11 |
| **Container** | `stipconnect_web` |
| **Port** | `0.0.0.0:8000` (intern) |
| **Workers** | 3 (sync) |
| **Build** | Custom Dockerfile |
| **Kosten** | €0 |

**Django-Apps:**
- `profiles` — Haupt-App (Profile, Swipe, Feedback)
- `stipconnect` — Projekt-Settings, Middleware, URLs

**Wichtig:** Kein `runserver` im Production — Gunicorn mit sync-Workern.

---

### 2.6 Datenbank: SQLite

| Attribut | Wert |
|----------|------|
| **Engine** | SQLite 3 |
| **Datei** | `db.sqlite3` |
| **Ort** | Host: `/home/laurensmain/stip-dating/db.sqlite3` |
| **Mount** | Container: `/app/db.sqlite3` (read-write) |
| **Backup** | 12+ Snapshots (`db.sqlite3.backup-*`) |
| **Kosten** | €0 |

**Wichtig:** SQLite ist für bis zu ~1000 gleichzeitige User OK. Bei Skalierung → PostgreSQL.

**Reserved Words:** `alter` ist SQLite reserved word → in raw SQL immer `"alter"` quoten.

---

### 2.7 File Storage: Profilfotos

| Attribut | Wert |
|----------|------|
| **Ort (Host)** | `/home/laurensmain/stip-dating/media/` |
| **Ort (Container)** | `/app/media/` |
| **Struktur** | `photos/%Y/%m/` (Jahr/Monat) |
| **Mount** | Docker-Volume: `./media:/app/media` |
| **Kosten** | €0 (lokale SSD) |

**Wichtig:** Dateien werden in den Container geschrieben, persistieren aber auf dem Host-Volume.

---

### 2.8 Static Assets

| Attribut | Wert |
|----------|------|
| **Ort (Host)** | `/home/laurensmain/stip-dating/staticfiles/` |
| **Ort (Container)** | `/app/staticfiles/` + `/srv/static` (Caddy) |
| **Generierung** | `python manage.py collectstatic` (im Container) |
| **Kosten** | €0 |

---

### 2.9 Entwicklungs-Umgebung

| Attribut | Wert |
|----------|------|
| **Orchestrator** | Hermes Agent (KI-Agent) |
| **Coding-Agent** | Claude Code (Anthropic CLI) |
| **Autonomer Job** | Cronjob alle 15 Minuten (`e4d2f24e9761`) |
| **Task-Tracking** | Kanban-Board `sdw-dating` |
| **Dokumentation** | Nextcloud Sync |

---

## 3. Netzwerk-Topologie

### Ports & Weiterleitungen

| Extern | Intern | Service | Beschreibung |
|--------|--------|---------|--------------|
| `443` (Cloudflare) | — | Cloudflare Edge | HTTPS-Terminierung |
| — | `8081` | Caddy | Docker-Port-Mapping (Host) |
| `8081` → `80` | — | Caddy | Docker-Compose mapping |
| — | `8000` | Gunicorn | Django-App (intern) |
| — | `8000` | Caddy | `reverse_proxy web:8000` |

### Container-Netzwerk

```
┌────────────────────────────────────────────────────────┐
│              Docker-Netzwerk: stipconnect               │
│                                                         │
│  ┌──────────────┐     ┌──────────────┐                │
│  │   caddy      │────▶│    web       │                │
│  │  :80         │     │   :8000      │                │
│  └──────────────┘     └──────────────┘                │
│        │                                               │
│        │ (Volume: ./media → /srv)                     │
│        ▼                                               │
│   ┌─────────┐                                          │
│   │  Host   │                                          │
│   │  Dateisystem                                      │
│   │  (media, staticfiles, db.sqlite3)                 │
│   └─────────┘                                          │
└────────────────────────────────────────────────────────┘

cloudflared (network_mode: host)
│
└──→ localhost:8081 (Caddy auf Host)
```

---

## 4. Hardware-Spezifikationen

### Host-Server

| Komponente | Spezifikation |
|------------|---------------|
| **Betriebssystem** | Ubuntu 22.04 LTS (Kernel 6.8.0-110-generic) |
| **CPU** | Intel i5 (Dualer Student Setup) |
| **RAM** | 16 GB |
| **Speicher** | SSD (ausreichend für App + Fotos) |
| **GPU** | NVIDIA GTX 1060 (für lokales Whisper, nicht für App) |
| **Standort** | Zuhause, Braunschweig |
| **Netzwerk** | DSL/Kabel → Tailscale VPN → Cloudflare Tunnel |
| **Uptime-Ziel** | 24/7 (Desktop-PC als Server) |

### Stromverbrauch

| Komponente | Geschätzter Verbrauch |
|------------|----------------------|
| Server (Idle) | ~50-80W |
| Server (Load) | ~100-150W |
| Jährliche Kosten | ~€50-80 |

---

## 5. Externe Dienste (SaaS)

| Dienst | Anbieter | Kosten | Nutzung |
|--------|----------|--------|---------|
| DNS | Cloudflare | €0 | Domain-Management, DNS-Records |
| SSL/TLS | Cloudflare Origin CA | €0 | HTTPS-Zertifikate |
| CDN | Cloudflare (implizit) | €0 | Edge-Caching |
| Auth | Cloudflare Access | €0 | JWT-basierte Authentifizierung |
| Tunnel | Cloudflare Tunnel | €0 | Sichere Verbindung ohne öffentliche IP |
| Registrar | Cloudflare | ~€12/Jahr | Domain-Registrierung |

**Keine externen Dienste für:**
- ❌ Datenbank-Hosting (lokale SQLite)
- ❌ File-Storage (lokale SSD)
- ❌ E-Mail-Service (kein SMTP konfiguriert)
- ❌ Monitoring (kein Datadog/New Relic)
- ❌ Logging-Backend (kein ELK/Loki)

---

## 6. Sicherheits-Architektur

### Layer 1: Cloudflare Edge
- DDoS-Schutz
- Bot-Management
- SSL/TLS-Terminierung
- Firewall-Regeln (wenn konfiguriert)

### Layer 2: Cloudflare Access
- Identity-Aware Proxy
- JWT-Validierung
- Session-Management
- Kein Zugriff ohne Authentifizierung

### Layer 3: Caddy Reverse Proxy
- Keine direkte Internet-Verbindung
- Nur internes Docker-Netzwerk
- Static/Media-File-Serving

### Layer 4: Django Application
- CSRF-Protection
- Session-Management (SQLite-backed)
- Middleware: CloudflareAccessMiddleware (JWT-Validierung)
- Kein lokaler Login-Bypass

### Layer 5: Host-System
- Ubuntu mit automatischen Updates
- Docker-Container-Isolation
- Tailscale VPN für Remote-Zugriff
- Keine SSH von außen (nur Tailscale)

---

## 7. Backup & Disaster Recovery

### Was wird gebackupt?

| Daten | Frequenz | Ort | Methode |
|-------|----------|-----|---------|
| `db.sqlite3` | Bei jedem Deployment | Host + Nextcloud | Manuelle Snapshots |
| `media/` (Fotos) | Bei Upload | Host + Nextcloud | rsync |
| Source Code | Bei jeder Änderung | GitHub + Nextcloud | git push + rsync |
| Configs | Bei Änderung | Nextcloud | Manuelle Kopie |

### Snapshot-Strategie

```bash
# Vor jedem großen Deployment:
cp db.sqlite3 db.sqlite3.backup-$(date +%Y%m%d-%H%M%S)
```

**Aktuell:** 12+ Backups im Projekt-Ordner.

### Recovery-Zeiten (RTO/RPO)

| Szenario | RTO | RPO |
|----------|-----|-----|
| Container-Crash | ~2 Min | Kein Datenverlust (Volumes) |
| Host-Crash | ~1 Stunde (Neuaufsetzung) | ~24h (letzter Backup) |
| Datenbank-Korruption | ~5 Min | Letzter Snapshot |
| Komplettverlust | ~2 Stunden | Letzter Snapshot + Git |

---

## 8. Monitoring (aktuell minimal)

| Was | Wie | Status |
|-----|-----|--------|
| Container-Status | `docker ps` | Manuell |
| Logs | `docker logs stipconnect_web` | Manuell |
| Uptime | Cloudflare Dashboard | Cloudflare |
| Fehler | Django-Logs im Container | Manuell |
| Ressourcen | `htop` auf Host | Manuell |

**Empfohlene Verbesserung:**
- Uptime-Kuma oder Healthchecks.io für Monitoring
- `docker-compose logs -f` für Live-Logs

---

## 9. Skalierungs-Pfade

### Aktuell (0-50 Nutzer)
- ✅ SQLite + Gunicorn (3 Worker) + Caddy
- ✅ Einzelner Docker-Host
- ✅ Cloudflare Access Free Plan

### Phase 2 (50-500 Nutzer)
- 🔄 SQLite → PostgreSQL (Docker-Container)
- 🔄 Gunicorn Worker erhöhen (5-10)
- 🔄 Cloudflare Access Pro ($3/User/Monat)

### Phase 3 (500+ Nutzer)
- 🔄 PostgreSQL auf dediziertem Host
- 🔄 Redis für Caching/Sessions
- 🔄 Load Balancer (Caddy oder Cloudflare LB)
- 🔄 Mehrere App-Server (Docker Swarm oder K8s)
- 🔄 S3-kompatibler Storage für Fotos (MinIO oder AWS S3)

---

## 10. Zusammenfassung: Was läuft wo?

| Komponente | Ort | Container/Service | Kosten |
|------------|-----|-------------------|--------|
| **Domain/DNS** | Cloudflare Edge | Cloudflare DNS | €12/Jahr |
| **Auth** | Cloudflare Edge | Cloudflare Access | €0 (Free) |
| **SSL/TLS** | Cloudflare Edge | Cloudflare Origin CA | €0 |
| **Reverse Proxy** | Laur. Server | `stipconnect_caddy` (Docker) | €0 |
| **App-Server** | Laur. Server | `stipconnect_web` (Docker) | €0 |
| **Datenbank** | Laur. Server | SQLite (im `web`-Container, Volume) | €0 |
| **Fotos** | Laur. Server | Host-FS `/home/laurensmain/stip-dating/media/` | €0 |
| **Static Assets** | Laur. Server | Host-FS `/home/laurensmain/stip-dating/staticfiles/` | €0 |
| **Tunnel** | Laur. Server | `stipconnect_tunnel` (Docker, host-net) | €0 |
| **Entwicklung** | Laur. Server | Hermes + Claude Code (lokal) | €0 |

**Gesamtkosten: ~€12/Jahr (Domain) + ~€50-80/Jahr (Strom)**

---

*Letzte Aktualisierung: 2026-06-12 06:35 UTC*  
*Autor: Hermes Agent (autonom)*  
*Quellcode: `/home/laurensmain/stip-dating/` | Sync: `Nextcloud/Startup/SDW Datingapp Projekt/`*
