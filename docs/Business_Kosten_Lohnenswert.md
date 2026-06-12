# StipConnect — Kosten, Business-Modell & Lohnenswertigkeit

Stand: 2026-06-12
Autor: Hermes Agent (autonom)

---

## 1. Einmalige Kosten (Setup)

| Posten | Betrag | Anmerkung |
|--------|--------|-----------|
| Domain `kochlab.net` | ~€12/Jahr | Cloudflare Registrar |
| Server (bestehend) | €0 | Ubuntu-Server bei dir zuhause |
| Cloudflare Access (Free Plan) | €0 | Bis 50 Nutzer kostenlos |
| SSL-Zertifikat | €0 | Cloudflare Origin CA (kostenlos) |
| **Setup-Gesamt** | **~€12** | Primär Domain |

**Wichtig:** Der Server läuft auf deiner bestehenden Hardware (Ubuntu, GTX 1060 als Host). Keine zusätzliche Hardware nötig.

---

## 2. Laufende Kosten (monatlich / jährlich)

### 2.1 Infrastructure (aktuell)

| Posten | Kosten/Jahr | Kosten/Monat | Anmerkung |
|--------|-------------|--------------|-----------|
| Domain `kochlab.net` | ~€12 | ~€1 | Cloudflare Registrar |
| Cloudflare Access (Free) | €0 | €0 | 0-50 Benutzer = kostenlos |
| Cloudflare Tunnel (`cloudflared`) | €0 | €0 | Kostenlos |
| Server-Strom | ~€50-80 | ~€4-7 | Desktop-PC als Server 24/7 |
| **Infrastructure-Total** | **~€62-92/Jahr** | **~€5-8/Monat** | |

### 2.2 Entwicklung & Betrieb (Time-Cost)

| Posten | Zeit/Monat | Bewertung |
|--------|------------|-----------|
| Hermes Agent (autonom) | ~2-4h manuelles Monitoring | Reduzierbar via Cronjobs |
| Claude Code (on demand) | ~$0-1/API-Call | Nur bei komplexen Features |
| Manuelle Bugfixes | ~1-2h/Monat | Ziel: autonom |
| **Time-Cost (geschätzt)** | **~5-10h/Monat** | Deine Zeit als Opportunity Cost |

### 2.3 Skalierungs-Kosten (ab 50+ Nutzern)

| Posten | Schwellwert | Kosten |
|--------|-------------|--------|
| Cloudflare Access Pro | Ab 50 Benutzern | ~$3/Benutzer/Monat |
| SQLite → PostgreSQL | Ab 500+ Profilen | €0 (Open Source), aber Setup-Zeit |
| Gunicorn → mehr Worker | Ab 100+ gleichzeitigen Usern | €0 (mehr RAM nötig) |
| CDN (Cloudflare Pro) | Ab hohem Bild-Traffic | ~$20/Monat |

**Szenario bei 100 SDW-Stipendiaten:**
- Cloudflare Access Pro: 100 × $3 = $300/Monat ≈ **€275/Monat**
- Plus evtl. Server-Upgrade (mehr RAM)
- **Gesamt: ~€3.300/Jahr + Strom**

---

## 3. Monetarisierung — Wie verdient StipConnect Geld?

### 3.1 Aktuelles Modell: Kostenlos

**Kein Revenue-Stream aktiv.** Die App ist kostenlos für alle SDW-Stipendiaten.

### 3.2 Mögliche Monetarisierungs-Optionen

| Modell | Umsetzung | Revenue-Potenzial | Komplexität |
|--------|-----------|-------------------|-------------|
| **Freemium** | Basis-App kostenlos, Premium-Features (z.B. mehr Fotos, Swipe-Undo, Standort-Filter) | Niedrig-Mittel | Gering |
| **Sponsoring / Werbung** | Lokalisierte Anzeigen (Studenten-Rabatte, Events) | Niedrig | Mittel |
| **Event-Ticketing** | SDW-Events über App promoten + Ticketing-Gebühr | Mittel | Hoch |
| **Stipendiaten-Netzwerk** | Premium-Networking-Features für Alumni | Hoch | Hoch |
| **White-Label** | App für andere Stiftungen/Stipendiaten-Verbände lizenzieren | Sehr hoch | Sehr hoch |
| **Daten-Analyse (anonymisiert)** | Aggregate Daten über Studienfächer/Regionen (für SDW-Strategie) | Niedrig | Mittel |

### 3.3 Empfohlenes Modell: **Freemium + White-Label**

**Phase 1 (Jetzt):** Kostenlos für alle SDW-Stipendiaten. Ziel: User-Base aufbauen.

**Phase 2 (ab 50 aktiven Nutzern):**
- Premium-Tier: €2,99/Monat oder €19,99/Jahr
  - Unbegrenzte Swipes (Basis: 10/Tag)
  - Swipe-Undo
  - Mehr Fotos (Basis: 1, Premium: 5)
  - Erweiterte Filter (Alter, Region, Studienfach)

**Phase 3 (ab 200+ Nutzern):**
- White-Label für andere Stipendiaten-Programme (z.B. Deutschlandstipendium, Hans-Böckler-Stiftung)
- Lizenzgebühr: €500-2.000/Setup + €50-100/Monat Hosting-Support

---

## 4. Lohnenswertigkeit-Analyse

### 4.1 Pro-Stimmen

| Argument | Gewichtung |
|----------|------------|
| **Niedrige Einstiegskosten** | ⭐⭐⭐⭐⭐ | €12/Jahr Domain, Rest ist Open Source |
| **Autonomer Betrieb** | ⭐⭐⭐⭐⭐ | Hermes + Claude Code = minimale Zeit-Investition |
| **Skalierbar** | ⭐⭐⭐⭐ | Von 10 auf 1.000 Nutzer ohne Code-Änderungen |
| **Unique Selling Point** | ⭐⭐⭐⭐ | Keine andere Dating-App für Stipendiaten |
| **Netzwerk-Effekt** | ⭐⭐⭐⭐ | Je mehr Stipendiaten, desto wertvoller |
| **Reputation** | ⭐⭐⭐⭐ | Gut für BCG-Application (Unternehmergeist) |

### 4.2 Kontra-Stimmen

| Argument | Gewichtung |
|----------|------------|
| **Kleine Zielgruppe** | ⭐⭐⭐ | SDW hat ~2.500 Stipendiaten, nur Bruchteil aktiv |
| **Kein Network Effects ohne Dichte** | ⭐⭐⭐ | Bei 20 Nutzern in Deutschland = keine Matches |
| **Privacy-Risiko** | ⭐⭐ | Dating-App = sensible Daten, DS-GVO-Konformität |
| **Wartungsaufwand** | ⭐⭐ | Auch autonomer Betrieb braucht Monitoring |
| **Konkurrenz** | ⭐⭐ | Tinder, Bumble, Hinge — aber nicht für Nischen |

### 4.3 Fazit: **Lohnenswert als Lernprojekt + Portfolio-Stück**

**Primärer Wert:** Nicht monetär, sondern strategisch:
- **BCG/Tier-1 Application:** Beweist Unternehmergeist, technische Kompetenz, Produkt-Mindset
- **Full-Stack-Erfahrung:** Django, Docker, Cloudflare, Auth — alles aus einer Hand
- **Autonomes Development:** Hermes + Claude Code = Cutting-Edge Workflow
- **Community-Building:** Netzwerk innerhalb der SDW stärken

**Monetärer Wert:** Gering bis moderat. Bei 100 Premium-Usern × €20/Jahr = €2.000/Jahr. Deckt Kosten, ist aber kein Business.

---

## 5. Risiken & Mitigation

| Risiko | Wahrscheinlichkeit | Impact | Mitigation |
|--------|-------------------|--------|------------|
| Zu wenige Nutzer | Hoch | Hoch | Beta-Tester einbeziehen, SDW-Newsletter nutzen |
| DS-GVO-Verstoß | Niedrig | Sehr hoch | Datenschutzerklärung, Cloudflare Access, keine Datenweitergabe |
| Server-Ausfall | Mittel | Hoch | Automatisches Backup (db.sqlite3), Monitoring |
| Negatives Feedback | Mittel | Mittel | Beta-Phase, Feedback-System bereits integriert |
| Feature-Creep | Hoch | Mittel | Ultra-minimal: Kein Chat, kein Algorithmus |
| Kosten-Explosion (CF Access) | Niedrig | Hoch | Free-Tier = 50 User; bei 51 Usern: €3/User/Monat |

---

## 6. KPIs & Erfolgsmetriken

| KPI | Ziel (3 Monate) | Ziel (6 Monate) | Messung |
|-----|-----------------|-----------------|---------|
| Registrierte Profile | 50 | 100 | Django-Admin |
| Aktive Nutzer (letzte 7 Tage) | 20 | 50 | Django-Admin |
| Matches (gesamt) | 10 | 30 | Swipe-Modell |
| Feedback-Einträge | 20 | 50 | FeedbackEntry-Modell |
| Bug-Reports | <5 | <3 | FeedbackEntry (Typ=bug) |
| Uptime | 99% | 99.5% | Cloudflare-Dashboard |
| Kosten/Nutzer | €1 | €0.50 | Infrastructure-Total / Nutzer |

---

## 7. Empfohlene Nächste Schritte (Business)

1. **Soft Launch** (Jetzt): 10 Beta-Tester einladen → Feedback sammeln
2. **Hard Launch** (Juli 2026): SDW-Newsletter, Social Media → Ziel: 50 Profile
3. **Feature-Entscheidung** (August 2026): Basierend auf Feedback — Premium-Tier ja/nein?
4. **White-Label-Pitch** (Q4 2026): Andere Stipendiaten-Programme ansprechen
5. **Exit-Option** (2027): An SDW oder Stipendiaten-Plattform verkaufen/abtreten

---

## 8. Alternativen zu StipConnect

| Alternative | Pro | Contra |
|-------------|-----|--------|
| **Projekt beenden** | Keine Zeit-/Kosten-Investition mehr | Verlorene Arbeit, kein Portfolio-Stück |
| **Open Source stellen** | Community-Pflege, Reputation | Kein Revenue, evtl. Forks |
| **SDW spenden** | Gutes Karma, Netzwerk | Kein Revenue, evtl. Übernahme-Probleme |
| **Weiter als Hobby** | Lernen, Spaß, autonom | Zeit-Investition ohne Return |
| **Professionalisieren** | Revenue, Skalierung | Hoher Aufwand, Konkurrenz |

---

## 9. Fazit

**StipConnect ist lohnenswert als Lernprojekt und Portfolio-Stück für BCG/Tier-1**, nicht als primäre Einkommensquelle.

| Aspekt | Bewertung |
|--------|-----------|
| **Technischer Wert** | ⭐⭐⭐⭐⭐ | Voller Stack, autonomer Betrieb |
| **Business-Wert** | ⭐⭐⭐ | Nische zu klein für echtes Revenue |
| **Karriere-Wert** | ⭐⭐⭐⭐⭐ | Exzellentes Gesprächsthema bei Interviews |
| **Kosten-Nutzen** | ⭐⭐⭐⭐⭐ | €12/Jahr für viel Lernen + Reputation |
| **Zeit-Investition** | ⭐⭐⭐⭐ | Autonom → minimale Zeit nötig |

**Empfehlung:** Weiterführen als autonomes Lernprojekt. Monetarisierung erst evaluieren wenn 100+ aktive Nutzer erreicht. Bei Erfolg: White-Label-Option prüfen.

---

*Letzte Aktualisierung: 2026-06-12 06:30 UTC*  
*Autor: Hermes Agent (autonom)*
