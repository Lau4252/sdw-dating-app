# 🤖 STIPCONNECT MASTER-PROMPT (Telegram-Steuerung)

**Gültig ab:** 11.06.2026  
**Version:** 1.0  
**Status:** Mockup live → Backend-Phase startet

---

## 📋 AKTUELLER STAND

| Komponente | Status | URL/Path |
|---|---|---|
| Mockup (Frontend) | ✅ LIVE | https://sdw-connect.kochlab.net/mockup/ |
| Django-Backend | 🔄 BEREIT | /home/laurensmain/stip-dating/ |
| Docker-Container | ✅ LAUFEND | stipconnect_web, stipconnect_caddy |
| Cloudflare Access | ✅ AKTIV | Auth auf sdw-connect.kochlab.net |
| Datenbank | ✅ SQLITE | /home/laurensmain/stip-dating/db.sqlite3 |
| Kanban-Board | ✅ AKTIV | `sdw-dating` (21 done, bereit für neue Tasks) |
| Claude Code | ✅ INSTALLIERT | v2.1.117, Auth: kj.89@web.de |
| Hermes Gateway | ✅ LAUFEND | Telegram-Notifications aktiv |

---

## 🎯 WIE DU TASKS ERSTELLST (Telegram)

Sende mir (Hermes) auf Telegram eine Nachricht im Format:

```
/stipconnect [TASK-BESCHREIBUNG]
```

**Oder einfach:**
```
Neuer Task: [was zu tun ist]
```

### Beispiele:

1. **Django-Model erstellen:**
   ```
   /stipconnect Erstelle ein Django-Model "Profile" mit allen Feldern aus dem Mockup: name, age, gender, seeking, photos (Array), about, studienfach, hochschule, regionen, sprachen, trinken, rauchen, interests, prompts, phone, visible. Migration erstellen und ausführen.
   ```

2. **Swipe-Interface bauen:**
   ```
   /stipconnect Baue das Swipe-Interface (Tinder-like). View + Template mit Card-Design aus dem Mockup. Links/Rechts-Swipe für Like/Reject. Profile-Detail-Sheet beim Hochswipen.
   ```

3. **Matching-Algorithmus:**
   ```
   /stipconnect Implementiere den Matching-Algorithmus: Prüfe gender/seeking-Kompatibilität, speichere Likes in SQLite, zeige "It's a Match" bei gegenseitigem Like.
   ```

4. **Cloudflare Auth:**
   ```
   /stipconnect Setze Cloudflare Access Auth ein: Lese CF-Header, erstelle User automatisch, leite zu Consent weiter wenn neu.
   ```

---

## 🚀 AUTONOMIE-REGELN (Hermes + Claude Code)

### Hermes macht SOFORT (ohne zu fragen):
- ✅ Kanban-Task erstellen mit `--idempotency-key`
- ✅ Claude Code starten mit Print-Mode (`-p`)
- ✅ Status-Updates an Telegram senden
- ✅ Bei Fehlern: Task auf `blocked` setzen + Grund melden
- ✅ Bei Erfolg: Task auf `done` setzen + Meilenstein melden
- ✅ Docker-Container rebuilden (`docker compose up -d`)
- ✅ Django-Management-Commands ausführen

### Claude Code macht SOFORT (ohne zu fragen):
- ✅ Django-Models, Views, Forms schreiben
- ✅ Templates (HTML/CSS/JS) erstellen
- ✅ Migrationen erstellen und ausführen
- ✅ URL-Routes konfigurieren
- ✅ Static-Files collecten
- ✅ Git-Commits auf Feature-Branch
- ✅ Tests schreiben

### MUSS IMMER GEFRAGT WERDEN:
- ❌ Datenbank LÖSCHEN
- ❌ Production-Deployment (Domain/DNS)
- ❌ Neue kostenpflichtige APIs
- ❌ Andere zu Admin machen
- ❌ Secrets/Tokens in öffentlichen Channels
- ❌ Source Code öffentlich machen

---

## 📊 MEILENSTEINE (wenn erreicht → Telegram-Benachrichtigung)

□ **Phase 0:** Mockup live ✅  
□ **Phase 1:** Django-Model "Profile" + SQLite-Migration  
□ **Phase 2:** Cloudflare Access Auth + User-Auto-Create  
□ **Phase 3:** Swipe-Interface (Tinder-like Cards)  
□ **Phase 4:** Matching-Algorithmus  
□ **Phase 5:** Match-Notification + Telefonnummer-Freigabe  
□ **Phase 6:** Admin-Freigabe-Workflow  
□ **Phase 7:** DSGVO-Consent + Löschfunktion  
□ **Phase 8:** Mobile-Optimierung + PWA  
□ **Phase 9:** Beta-Launch

---

## 🛠️ TECH-STACK (fest)

| Layer | Technologie |
|---|---|
| Backend | Django 5 + SQLite |
| Auth | Cloudflare Access (Email-Header) |
| Frontend | Django Templates + Tailwind CDN |
| CSS | Custom (Mockup-Design-System) |
| Hosting | Docker Compose (Web + Caddy + Cloudflared) |
| Domain | sdw-connect.kochlab.net |
| Worker | Claude Code v2.1.117 |
| Orchestrator | Hermes Agent |

---

## 📁 WICHTIGE Pfade

- **Projekt:** `/home/laurensmain/stip-dating/`
- **Django-App:** `/home/laurensmain/stip-dating/profiles/`
- **Templates:** `/home/laurensmain/stip-dating/templates/`
- **Static:** `/home/laurensmain/stip-dating/static/`
- **DB:** `/home/laurensmain/stip-dating/db.sqlite3`
- **Docker:** `docker compose -f /home/laurensmain/stip-dating/docker-compose.yml`
- **CLAUDE.md:** `/home/laurensmain/stip-dating/CLAUDE.md`
- **Mockup:** https://sdw-connect.kochlab.net/mockup/

---

## 🔐 SICHERHEIT

- Telefonnummer erst bei **gegenseitigem Match** sichtbar
- Profil nur für **freigeschaltete SDW-Mitglieder**
- Löschfunktion: User + Profile + Fotos komplett entfernen
- Consent-Checkbox: **NICHT pre-selected**
- Cloudflare DPA: Akzeptiert

---

## 📲 TELEGRAM-NOTIFICATION-FORMAT

Wenn ein Task erledigt ist:

```
🚀 StipConnect Update
Task: [Titel] → ✅ DONE
Meilenstein: [Phase X]
Nächster Schritt: [Was kommt danach]
URL: [Falls relevant]
Zeitstempel: [Jetzt]
```

---

## ⚡ SCHNELLSTART

**Sende mir jetzt deinen ersten Backend-Task auf Telegram!**

Empfohlene Reihenfolge:
1. Django-Model "Profile" erstellen
2. Cloudflare Auth + User-Auto-Create
3. Swipe-Interface
4. Matching-Algorithmus
5. Match-Seite mit Telefonnummer

---

**Viel Erfolg! 🚀**
