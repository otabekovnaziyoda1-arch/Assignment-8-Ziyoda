# Telegram Reminder Bot (aiogram + Flask)

Simple beginner-friendly Telegram bot with reminder functionality using:
- `aiogram` for bot logic
- `Flask` for webhook endpoint
- `asyncio` for reminder scheduling

## Features

- `/start` command with welcome text
- Reminder input format: `HH:MM message`
  - Example: `18:30 Do homework`
- Parses time + reminder text
- Stores reminders in memory (Python list)
- Waits until reminder time and sends message
- Webhook support (no polling)

## Project Files

- `bot.py` - main bot + Flask webhook app
- `requirements.txt` - Python dependencies
- `.env.example` - environment variable template

## Local Run

1. Create and activate virtual environment (recommended):
   - Windows PowerShell:
     - `python -m venv .venv`
     - `.venv\Scripts\Activate.ps1`

2. Install dependencies:
   - `pip install -r requirements.txt`

3. Create `.env` file from template:
   - Copy `.env.example` to `.env`
   - Fill:
     - `BOT_TOKEN=...`
     - `WEBHOOK_URL=https://your-public-url`

4. Run:
   - `python bot.py`

## Deploy on Render (Web Service + Webhook)

1. Push this project to a GitHub repository.
2. In Render, click **New +** -> **Web Service**.
3. Connect your GitHub repository.
4. Set:
   - **Runtime**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python bot.py`
5. Add environment variables in Render:
   - `BOT_TOKEN` = your Telegram bot token
   - `WEBHOOK_URL` = your Render service URL  
     Example: `https://my-reminder-bot.onrender.com`
6. Deploy the service.

After deploy, the bot sets webhook to:
- `https://your-service.onrender.com/webhook`

### Optional: Deploy via `render.yaml` (Blueprint)

- This project includes `render.yaml`.
- In Render, choose **New +** -> **Blueprint** and select your repository.
- Render will create the web service using the settings from `render.yaml`.
- Then set secret values for:
  - `BOT_TOKEN`
  - `WEBHOOK_URL` (your Render service URL)

Health check endpoint:
- `GET /` -> `Bot is running`

## Notes

- Time is based on the server clock.
- Reminders are stored in memory only.
  - If service restarts, existing reminders are lost.
