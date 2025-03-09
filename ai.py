import requests
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

NGROK_URL = "https://99e9-34-105-36-66.ngrok-free.app/generate"  # Replace with your ngrok URL
BOT_TOKEN = "7765834703:AAE9UEhF-dPAsc-jaJ8VvsiWPNi0iqo9EGU"  # Replace with your token

def generate_response(prompt):
    try:
        response = requests.post(NGROK_URL, json={"prompt": prompt}, timeout=30)
        response.raise_for_status()
        return response.json().get("output", "Error: No output")
    except requests.RequestException as e:
        return f"Error: API call failed - {str(e)}"

def start(update, context):
    update.message.reply_text("I'm your monster bot! Send me a prompt, and I'll generate code or text.")

def handle_message(update, context):
    user_prompt = update.message.text
    reply = generate_response(user_prompt)
    update.message.reply_text(reply)

updater = Updater(BOT_TOKEN, use_context=True)
dp = updater.dispatcher
dp.add_handler(CommandHandler("start", start))
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
updater.start_polling()
updater.idle()  # Keep running