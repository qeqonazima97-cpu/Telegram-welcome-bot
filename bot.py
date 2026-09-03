import logging
from datetime import datetime
import pytz
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Date & Time format korar function (Bangladesh Time)
def get_bd_datetime():
    tz = pytz.timezone('Asia/Dhaka')
    now = datetime.now(tz)
    date_str = now.strftime('%d-%m-%Y')
    time_str = now.strftime('%I:%M %p')
    return date_str, time_str

# Dynamic Welcome Message
def create_welcome_message(name: str, username: str, user_id: int) -> str:
    date_str, time_str = get_bd_datetime()
    return f"""╭━━━〔 ✦ 𝐖𝐄𝐋𝐂𝐎𝐌𝐄 ✦ 〕━━━╮
👑 𝐇𝐞𝐲, {name}! 👑
🧾 𝐔𝐬𝐞𝐫 : {username}
📝 𝐈𝐃  : {user_id}
📅 𝐃𝐚𝐭𝐞 : {date_str}
🕖 𝐓𝐢𝐦𝐞 : {time_str}
╰━━━━━━━━━━━━━━━━━━━━╯

✨ 𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐭𝐨 𝐭𝐡𝐢𝐬 𝐠𝐫𝐨𝐮𝐩!
💫 𝐆𝐥𝐚𝐝 𝐭𝐨 𝐡𝐚𝐯𝐞 𝐲𝐨𝐮 𝐡𝐞𝐫𝐞.
🤝 𝐒𝐭𝐚𝐲 𝐚𝐜𝐭𝐢𝐯𝐞 • 𝐒𝐭𝐚𝐲 𝐫𝐞𝐬𝐩𝐞𝐜𝐭𝐟𝐮𝐥
🔥 𝐄𝐧𝐣𝐨𝐲 𝐭𝐡𝐞 𝐠𝐫𝐨𝐮𝐩!

╰─「 ❤️ 𝐇𝐚𝐯𝐞 𝐚 𝐠𝐫𝐞𝐚𝐭 𝐭𝐢𝐦𝐞 ❤️ 」─╯"""

# Dynamic Goodbye Message
def create_goodbye_message(name: str) -> str:
    return f"👋 GOODBYE, {name} 😔"

# /start command handler
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    name = user.first_name if user else "Friend"
    username = f"@{user.username}" if user and user.username else "No username"
    user_id = user.id if user else 0

    welcome_text = create_welcome_message(name, username, user_id)
    await update.message.reply_text(welcome_text)

# Notun member join korle Welcome message pathanor function
async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    for new_user in update.message.new_chat_members:
        if new_user.id == context.bot.id:
            continue

        name = new_user.first_name
        username = f"@{new_user.username}" if new_user.username else "No username"
        user_id = new_user.id

        welcome_text = create_welcome_message(name, username, user_id)
        await update.message.reply_text(welcome_text)

# Keu group leave nile Goodbye message pathanor function
async def member_left(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    left_user = update.message.left_chat_member
    
    # Bot nijai leave nile message dibe na
    if left_user.id == context.bot.id:
        return

    name = left_user.first_name
    goodbye_text = create_goodbye_message(name)
    await update.message.reply_text(goodbye_text)

if __name__ == '__main__':
    # Apnar bot token-ti ekhane din
    TOKEN = "YOUR_NEW_BOT_TOKEN"

    app = ApplicationBuilder().token(TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))
    app.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, member_left))

    print("Bot is running...")
    app.run_polling()
