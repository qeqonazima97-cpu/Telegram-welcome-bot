import logging
from telegram import Update
from telegram.ext import (
    Application,
    ChatMemberHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# Enable logging to track errors or activity
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

BOT_TOKEN = "8661874156:AAGm8-QmbvfLC5as1DytnFiyxvuzGaXNsSs"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text(
        "Hello! I am your Group Welcome Bot. Add me to a group and grant admin privileges to greet new members!"
    )


async def welcome_new_member(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Greet new members when they join the group."""
    for new_member in update.message.new_chat_members:
        # Ignore if the bot itself was added
        if new_member.id == context.bot.id:
            continue

        welcome_text = (
            f"Welcome to the group, {new_member.mention_html()}! 🎉\n\n"
            "We are glad to have you here. Please feel free to introduce yourself!"
        )

        await update.message.reply_html(welcome_text)


async def goodbye_member(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Send a goodbye message when a member leaves the group."""
    left_member = update.message.left_chat_member

    # Ignore if the bot itself left/was removed
    if left_member.id == context.bot.id:
        return

    goodbye_text = f"Goodbye, {left_member.full_name}. We wish you all the best!"
    await update.message.reply_text(goodbye_text)


def main() -> None:
    """Start the bot."""
    # Create the Application instance
    application = Application.builder().token(BOT_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))

    # Handler for new members joining
    application.add_handler(
        MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member)
    )

    # Handler for members leaving
    application.add_handler(
        MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, goodbye_member)
    )

    # Run the bot until interrupted (Ctrl+C)
    logger.info("Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
