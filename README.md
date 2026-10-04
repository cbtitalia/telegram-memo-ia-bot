# Telegram Memo IA Bot

Telegram bot pour capturer automatiquement les mémos IA dans Obsidian.

## Architecture

```
Telegram (@cbtitalia_memo_ia_bot)
  ↓ polling via API
Docker Container (Synology 192.168.1.15)
  ├─ main.py (Python 3.12)
  ├─ python-telegram-bot v20
  ↓
Synology NAS
  ├─ Filesystem: /volume1/015_Obsidian/90_Memo_IA/
  ↓
Obsidian Vault (Brain_Stan)
  ├─ Sync automatique
```

## Installation

1. **Créer le bot Telegram** via `@BotFather`
2. **Configurer `.env`** avec les credentials
3. **Lancer le container Docker**:
   ```bash
   docker-compose up -d
   ```

## Configuration

Voir `.env` pour:
- `TELEGRAM_BOT_TOKEN`: Token du bot Telegram
- `CHAT_ID`: ID du canal Telegram
- `OUTPUT_DIR`: Chemin de sortie des fichiers (Obsidian)

## Utilisation

Envoie un message au bot `@cbtitalia_memo_ia_bot` depuis Telegram:
- Le bot reçoit le message
- Crée un fichier `.md` avec:
  - Frontmatter REF auto-généré
  - Timestamp: `YYYY-MM-DD_HHMMSS - <première_ligne>.md`
  - Tags: `ia`, `claude`, `mobile`
- Répond "✅ Mémo sauvegardé"

## Fichiers

- `main.py`: Code Python principal (polling + write)
- `docker-compose.yml`: Orchestration Docker
- `Dockerfile`: Image Python + dependencies
- `requirements.txt`: Dépendances Python
- `.env`: Configuration credentials (NOT in git)

## Status

- **Phase 1**: ✅ Bot Telegram setup
- **Phase 2**: ✅ Docker deployment + write direct
- **Phase 3**: ⏳ Templates & auto-routing

## Logs

```bash
docker-compose logs --tail=50
```

## Auteur

Stan (2026-10-04)

## License

Personal use only
