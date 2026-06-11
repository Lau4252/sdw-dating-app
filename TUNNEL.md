# 🔗 Tunnel-Konfiguration

## Aktiver Quick-Tunnel (Temporär)
- **URL**: https://treasurer-represent-tone-cad.trycloudflare.com
- **Container**: `quick-tunnel` (Docker)
- **Ziel**: `http://stipconnect_caddy:80` (Caddy Reverse Proxy)
- **Gültig**: Bis Container-Restart (neue URL danach)

## Permanenter Tunnel (Vorbereitet)
- **Name**: `stipconnect-v2`
- **ID**: `1fdbdbcc-52b0-40ee-9622-17bd21edea2d`
- **Status**: Erstellt, wartet auf Domain (Task 7)
- **Cred-Datei**: `~/.cloudflared/1fdbdbcc-52b0-40ee-9622-17bd21edea2d.json`

## Umstellung auf Permanenter Tunnel
Sobald Domain geklärt ist (Task 7):
```bash
cloudflared tunnel route dns stipconnect-v2 DEINE-DOMAIN.de
# Dann .env TUNNEL_TOKEN aktualisieren
# docker compose restart cloudflared
```
