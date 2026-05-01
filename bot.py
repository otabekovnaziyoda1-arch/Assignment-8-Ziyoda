import asyncio
import os
import re
import threading
from datetime import datetime, timedelta
from datetime import datetime, timezone

from aiogram import Bot, Dispatcher, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, Update
from dotenv import load_dotenv
from flask import Flask, request


load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = https://assignment-8-ziyoda.onrender.com
PORT = int(os.getenv("PORT", "5000"))

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is missing. Add it to your .env file.")

if not WEBHOOK_URL:
    raise ValueError("WEBHOOK_URL is missing. Add it to your .env file.")

# In-memory reminder storage (for learning purposes).
reminders = []

app = Flask(__name__)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

# Background event loop for aiogram and reminder tasks.
bot_loop = asyncio.new_event_loop()


def start_background_loop() -> None:
    asyncio.set_event_loop(bot_loop)
    bot_loop.run_forever()


threading.Thread(target=start_background_loop, daemon=True).start()


def run_async(coro):
    return asyncio.run_coroutine_threadsafe(coro, bot_loop)


async def reminder_task(chat_id: int, reminder_text: str, target_time: datetime) -> None:
    delay = (target_time - datetime.now(timezone.utc)).total_seconds()
    if delay > 0:
        await asyncio.sleep(delay)

    await bot.send_message(chat_id, f"Reminder: {reminder_text}")


@router.message(CommandStart())
async def start_command(message: Message) -> None:
    await message.answer(
        "Hello! Send reminders like this:\n"
        "18:30 Do homework\n\n"
        "Time format must be HH:MM."
    )


@router.message()
async def set_reminder(message: Message) -> None:
    text = (message.text or "").strip()
    match = re.match(r"^(\d{2}):(\d{2})\s+(.+)$", text)

    if not match:
        await message.answer("Please use format: HH:MM message\nExample: 18:30 Do homework")
        return

    hour = int(match.group(1))
    minute = int(match.group(2))
    reminder_text = match.group(3).strip()

    if hour > 23 or minute > 59:
        await message.answer("Invalid time. Use a valid 24-hour time like 09:45.")
        return

    now = datetime.now(timezone.utc)
    target_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

    # If time already passed today, schedule for tomorrow.
    if target_time <= now:
        target_time += timedelta(days=1)

    reminder_data = {
        "chat_id": message.chat.id,
        "time": target_time.isoformat(),
        "text": reminder_text,
    }
    reminders.append(reminder_data)

    run_async(reminder_task(message.chat.id, reminder_text, target_time))
    await message.answer(
        f"Reminder set for {target_time.strftime('%Y-%m-%d %H:%M')}:\n{reminder_text}"
    )


async def process_update(update_data: dict) -> None:
    update = Update.model_validate(update_data, context={"bot": bot})
    await dp.feed_update(bot, update)


async def set_webhook() -> None:
    await bot.set_webhook(url=f"{WEBHOOK_URL}{WEBHOOK_PATH}")


@app.route("/", methods=["GET"])
def index():
    return "Bot is running", 200


@app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    update_data = request.get_json(silent=True)
    if not update_data:
        return {"ok": False, "error": "No JSON body"}, 400

    future = run_async(process_update(update_data))
    try:
        future.result(timeout=20)
    except Exception as e:
        print("Error:", e)
    return {"ok": True}, 200


def startup() -> None:
    run_async(set_webhook()).result(timeout=20)


if __name__ == "__main__":
    startup()
    app.run(host="0.0.0.0", port=PORT)
