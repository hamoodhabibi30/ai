import re
import requests
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Constants
BOT_TOKEN = '7596532900:AAF6p_RGYFddAwoWdwtBlr0lJwjFT2GhYPA'
TERABOXFAST_API = 'https://www.teraboxfast.com/p/video-player.html?q='

# Generate a random User-Agent
ua = UserAgent()
random_user_agent = ua.random

# Chrome Options (Bypasses Bot Detection)
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--log-level=3")
chrome_options.add_argument(f"user-agent={random_user_agent}")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")

# Setup WebDriver
def get_driver():
    driver = uc.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

# Validate TeraBox URL
def is_valid_terabox_url(url):
    return bool(re.match(r'^(https?://)?(?:1024)?terabox\.com/s/[a-zA-Z0-9_-]+$', url, re.IGNORECASE))

# Extract .m3u8 URL only
def extract_m3u8_link(teraboxfast_url):
    try:
        driver = get_driver()
        driver.get(teraboxfast_url)

        # Wait for iframes to load
        WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "iframe"))
        )

        # Parse page source
        soup = BeautifulSoup(driver.page_source, "html.parser")
        driver.quit()

        # Extract m3u8 from securityFrame iframe
        security_iframe = soup.find("iframe", {"id": "securityFrame"})
        if security_iframe and security_iframe.get("src"):
            alternative_url = security_iframe["src"]
            if "/terabox/" in alternative_url:
                return alternative_url.replace("/terabox/", "/terabox/video/").split("?")[0] + ".m3u8"

        return None

    except Exception as e:
        print(f"❌ Error extracting .m3u8 link: {e}")
        return None

# Fetch .m3u8 link
def get_m3u8_link(terabox_url):
    try:
        teraboxfast_url = TERABOXFAST_API + requests.utils.quote(terabox_url)
        return extract_m3u8_link(teraboxfast_url)
    except Exception as e:
        print(f"❌ Error fetching .m3u8 link: {e}")
        return None

# Telegram Bot Handlers
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "<b>👋 Welcome to TeraBox Bot!</b>\n\nSend me a TeraBox URL, and I'll provide the direct `.m3u8` video link.",
        parse_mode='HTML'
    )

async def handle_message(update: Update, context: CallbackContext):
    text = update.message.text.strip()

    if not text:
        await update.message.reply_text(
            "❌ <b>Please send a TeraBox URL to get the .m3u8 link.</b>",
            parse_mode='HTML'
        )
        return

    if is_valid_terabox_url(text):
        m3u8_link = get_m3u8_link(text)

        if m3u8_link:
            message = f"✅ <b>Your .m3u8 link:</b>\n<code>{m3u8_link}</code>"
            await update.message.reply_text(message, parse_mode='HTML')
        else:
            await update.message.reply_text("❌ <b>Could not extract .m3u8 link.</b>", parse_mode='HTML')
    else:
        await update.message.reply_text("❌ <b>Invalid TeraBox URL.</b>", parse_mode='HTML')

# Main Function
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🚀 Bot started with polling...")
    app.run_polling()

if __name__ == '__main__':
    main()
