#!/usr/bin/env python3
"""Telegram Memo IA Bot — Phase 3: respects Claude frontmatter"""
import os, logging, asyncio, re, mimetypes
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from telegram import Bot
from telegram.error import TelegramError

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "/volume1/015_Obsidian/90_Memo_IA"))

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
bot = Bot(token=TOKEN)
last_update_id = 0

def sanitize_filename(text):
    filename = re.sub(r'[^\w\s_-]', '', text)
    return (filename.strip()[:50]) or "memo"

def extract_title_from_frontmatter(content):
    """Extract title from YAML frontmatter if present"""
    if content.startswith("---"):
        lines = content.split('\n')
        for i, line in enumerate(lines[1:], 1):
            if line.startswith("---"):
                break
            if line.startswith("titre:") or line.startswith("title:"):
                title = line.split(':', 1)[1].strip().strip('"\'')
                return sanitize_filename(title) if title else None
    return None

def get_unique_filepath(path):
    """Handle filename collisions by appending -2, -3, etc."""
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    counter = 2
    while True:
        new_path = path.parent / f"{stem}-{counter}{suffix}"
        if not new_path.exists():
            return new_path
        counter += 1

def save_memo(text, date):
    try:
        # Check if content starts with frontmatter
        if text.startswith("---"):
            content = text
            # Extract title from frontmatter
            title = extract_title_from_frontmatter(text)
            if not title:
                # Fallback: use first line after frontmatter
                lines = text.split('\n')
                for line in lines:
                    if line and not line.startswith("---") and not line.startswith(("1=", "2=", "3=", "4=", "5=", "source:", "date:", "tags:", "projet:", "urgence:", "liens:")):
                        title = sanitize_filename(line[:50])
                        break
                title = title or "memo"
        else:
            # Add default frontmatter REF
            default_frontmatter = f"""---
1= IA
2= Claude
3= wiki IA
4= conversation
5= Depuis téléphone
source: telegram
date: {date.isoformat()}
auteur: Claude Mobile
tags:
  - ia
  - claude
  - mobile
projet: undefined
urgence: normal
liens: []
---

"""
            content = default_frontmatter + text
            title = sanitize_filename(text.split('\n')[0][:50])

        timestamp = date.strftime("%Y-%m-%d_%H%M%S")
        filename = f"{timestamp} - {title}.md"
        filepath = OUTPUT_DIR / filename
        filepath = get_unique_filepath(filepath)

        filepath.write_text(content, encoding='utf-8')
        logger.info(f"✅ Memo saved: {filepath.name}")
        return filepath.name
    except Exception as e:
        logger.error(f"❌ Error saving memo: {e}")
        return None

async def main():
    global last_update_id
    logger.info(f"Bot initialized: {OUTPUT_DIR}")
    logger.info("Starting polling...")

    while True:
        try:
            updates = await bot.get_updates(offset=last_update_id, timeout=10)

            if updates:
                for update in updates:
                    last_update_id = update.update_id + 1

                    if update.message:
                        date = update.message.date

                        # Handle text messages
                        if update.message.text:
                            text = update.message.text
                            filename = save_memo(text, date)
                            if filename:
                                await bot.send_message(chat_id=update.message.chat_id, text=f"✅ Mémo sauvegardé : {filename}")
                            else:
                                await bot.send_message(chat_id=update.message.chat_id, text="❌ Erreur lors de la sauvegarde")

                        # Handle document attachments (.md, .txt)
                        elif update.message.document:
                            doc = update.message.document
                            mime_type = doc.mime_type or ""

                            # Only accept .md and .txt files
                            if mime_type in ("text/plain", "text/markdown") or doc.file_name.endswith((".md", ".txt")):
                                try:
                                    file = await bot.get_file(doc.file_id)
                                    content = await file.download_as_bytearray()
                                    text = content.decode('utf-8')
                                    filename = save_memo(text, date)
                                    if filename:
                                        await bot.send_message(chat_id=update.message.chat_id, text=f"✅ Document sauvegardé : {filename}")
                                    else:
                                        await bot.send_message(chat_id=update.message.chat_id, text="❌ Erreur lors de la sauvegarde")
                                except Exception as e:
                                    logger.error(f"Error processing document: {e}")
                                    await bot.send_message(chat_id=update.message.chat_id, text="❌ Erreur lors du traitement du document")
                            else:
                                await bot.send_message(chat_id=update.message.chat_id, text="⚠️ Seuls les fichiers .md et .txt sont acceptés")

            await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Bot stopped")
            break
        except TelegramError as e:
            logger.error(f"Telegram error: {e}")
            await asyncio.sleep(5)
        except Exception as e:
            logger.error(f"Error: {e}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
