#!/usr/bin/env python3
"""Telegram Memo IA Bot — async polling version"""
import os, logging, asyncio, re
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from telegram import Bot
from telegram.error import TelegramError

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "/volume2/homes/cbtitalia/90_Memo_IA/Inbox"))

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
bot = Bot(token=TOKEN)
last_update_id = 0

def sanitize_filename(text):
    filename = re.sub(r'[^\w\s_-]', '', text)
    return (filename.strip()[:50]) or "memo"

def save_memo(text, date):
    try:
        filename_base = sanitize_filename(text.split('\n')[0][:50])
        timestamp = date.strftime("%Y-%m-%d_%H%M%S")
        filename = f"{timestamp} - {filename_base}.md"
        
        frontmatter = f"""---
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
        filepath = OUTPUT_DIR / filename
        filepath.write_text(frontmatter + text, encoding='utf-8')
        logger.info(f"✅ Memo saved: {filename}")
        return True
    except Exception as e:
        logger.error(f"❌ Error saving memo: {e}")
        return False

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
                    
                    if update.message and update.message.text:
                        text = update.message.text
                        date = update.message.date
                        
                        if save_memo(text, date):
                            await bot.send_message(chat_id=update.message.chat_id, text="✅ Mémo sauvegardé")
                        else:
                            await bot.send_message(chat_id=update.message.chat_id, text="❌ Erreur")
            
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
