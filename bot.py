from telegram import Update
from telegram.ext import ApplicationBuilder, ChatMemberHandler, ContextTypes, CommandHandler

# Notun member group-e join korle ba /start dile ei welcome message-ti jabe
async def send_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # User info collect kora
    user = update.effective_user
    name = user.first_name if user else "Friend"
    username = f"@{user.username}" if user and user.username else "No username"

    # Apnar customize kora message
    welcome_text = f"""⚜️ WELCOME TO THIS GROUP ⚜️

 👋 Hey, {name}
 📃 {username}

Thank you for coming in this group
                               💝💝"""

    # Message-ti group ba chat-e pathano
    if update.message:
        await update.message.reply_text(welcome_text)

# Notun member join handle korar function
async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    result = update.chat_member
    if result.old_chat_member.status in ["left", "kicked"] and result.new_chat_member.status == "member":
        user = result.new_chat_member.user
        name = user.first_name
        username = f"@{user.username}" if user.username else "No username"

        welcome_text = f"""⚜️ WELCOME TO THIS GROUP ⚜️

 👋 Hey, {name}
 📃 {username}

Thank you for coming in this group
                               💝💝"""

        await context.bot.send_message(chat_id=update.effective_chat.id, text=welcome_text)

if __name__ == '__main__':
    # 'YOUR_NEW_BOT_TOKEN' er jaygay apnar notun bot token-ti din
    app = ApplicationBuilder().token("8661874156:AAGm8-QmbvfLC5as1DytnFiyxvuzGaXNsSs").build()

    # /start command-er jonno
    app.add_handler(CommandHandler("start", send_welcome))
    
    # Group-e notun member join korle auto welcome korar jonno
    app.add_handler(ChatMemberHandler(welcome_new_member, ChatMemberHandler.CHAT_MEMBER))

    print("Bot is running...")
    app.run_polling()
