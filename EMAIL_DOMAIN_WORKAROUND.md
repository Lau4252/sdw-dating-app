# Stiftungs-E-Mail-Domain — Workarounds

## Problem
Stipendiaten haben **keine zentrale @studienstiftung.de** E-Mail.
Jeder nutzt seine private Universität/Einrichtungs-Mail.

## Optionen für Cloudflare Access

### A. Manuelle E-Mail-Whitelist (Empfohlen für Beta)
- Alle 200 E-Mail-Adressen in Cloudflare Access eintragen
- Aufwand: ~30 Minuten (Copy-Paste aus Liste)
- Vorteil: Präzise Kontrolle

### B. Einladungs-Link mit Token
- App bleibt offen (kein Access)
- Registrierung nur mit gültigem Einladungs-Token
- Token per E-Mail/Signal/WhatsApp an Stipendiaten

### C. Self-Service mit Verifikation
- Nutzer registrieren sich mit beliebiger E-Mail
- Verifikation via Stiftungs-ID / Referenz-Code
- Manuelle Freigabe durch Admin

### D. Kombination (Empfohlen für Launch)
1. **Beta:** Manuelle Whitelist (Option A)
2. **Growth:** Einladungs-Token (Option B)
3. **Scale:** Self-Service (Option C)

---

*Stand: 2026-06-11 — Entscheidung nötig*
