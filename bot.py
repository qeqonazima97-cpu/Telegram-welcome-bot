import os
import sqlite3
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# SQLite DB Path (Railway Volume use korle /data directory use kora valo)
DB_DIR = "/data" if os.path.exists("/data") else "."
DB_NAME = os.path.join(DB_DIR, "bot_data.db")


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            chat_id INTEGER PRIMARY KEY,
            status INTEGER DEFAULT 1,
            welcome_msg TEXT DEFAULT 'Welcome {first_name} to the group!'
        )
    """)
    conn.commit()
    conn.close()


def get_settings(chat_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT status, welcome_msg FROM settings WHERE chat_id = ?", (chat_id,)
    )
    row = cursor.fetchone()
    if not row:
        cursor.execute(
            "INSERT INTO settings (chat_id, status, welcome_msg) VALUES (?, 1, ?)",
            (chat_id, "Welcome {first_name} to the group!"),
        )
        conn.commit()
        status, msg = 1, "Welcome {first_name} to the group!"
    else:
        status, msg = row[0], row[1]
    conn.close()
    return status, msg


def update_status(chat_id: int, status: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO settings (chat_id, status) VALUES (?, ?) ON CONFLICT(chat_id) DO UPDATE SET status = ?",
        (chat_id, status, status),
    )
    conn.commit()
    conn.close()


def update_welcome_msg(chat_id: int, msg: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO settings (chat_id, welcome_msg) VALUES (?, ?) ON CONFLICT(chat_id) DO UPDATE SET welcome_msg = ?",
        (chat_id, msg, msg),
    )
    conn.commit()
    conn.close()


async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    if update.effective_chat.type == "private":
        return True
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    member = await context.bot.get_chat_member(chat_id, user_id)
    return member.status in ["administrator", "creator"]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 **Welcome Bot Active!**\nUse `/adminhelp` for available controls.",
        parse_mode="Markdown",
    )


async def bot_on(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("⛔ Shudhu Group Admin-ra ei command use korte parbe.")
        return
    chat_id = update.effective_chat.id
    update_status(chat_id, 1)
    await update.message.reply_text("✅ Welcome System: **ON**", parse_mode="Markdown")


async def bot_off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("⛔ Shudhu Group Admin-ra ei command use korte parbe.")
        return
    chat_id = update.effective_chat.id
    update_status(chat_id, 0)
    await update.message.reply_text("❌ Welcome System: **OFF**", parse_mode="Markdown")


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    current_status, current_msg = get_settings(chat_id)
    state = "🟢 ON" if current_status == 1 else "🔴 OFF"
    await update.message.reply_text(
        f"📊 **Current Status:** {state}\n\n📝 **Welcome Message:**\n`{current_msg}`",
        parse_mode="Markdown",
    )


async def set_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("⛔ Shudhu Group Admin-ra ei command use korte parbe.")
        return
    if not context.args:
        await update.message.reply_text(
            "⚠️ Message text likhun.\nExample:\n`/setwelcome Welcome {first_name} to our group!`",
            parse_mode="Markdown",
        )
        return
    new_msg = " ".join(context.args)
    chat_id = update.effective_chat.id
    update_welcome_msg(chat_id, new_msg)
    await update.message.reply_text(
        f"✅ Welcome message saved successfully:\n\n`{new_msg}`", parse_mode="Markdown"
    )


async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    text = (
        f"ℹ️ **User & Chat Info**\n\n"
        f"👤 Name: `{user.full_name}`\n"
        f"🆔 User ID: `{user.id}`\n"
        f"💬 Group Title: `{chat.title if chat.title else 'Private Chat'}`\n"
        f"🆔 Group ID: `{chat.id}`"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def admin_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🛠 **Admin Command List:**\n\n"
        "• `/on` - Welcome feature enable\n"
        "• `/off` - Welcome feature disable\n"
        "• `/status` - Bot status & current text\n"
        "• `/setwelcome <text>` - Custom welcome msg\n"
        "   *(Variables: `{first_name}`, `{full_name}`, `{username}`)*\n"
        "• `/info` - User & Chat ID\n"
        "• `/adminhelp` - Ei Help menu"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    status_val, welcome_template = get_settings(chat_id)
    if status_val == 0:
        return
    for member in update.message.new_chat_members:
        if member.id == context.bot.id:
            continue
        formatted_msg = welcome_template.format(
            first_name=member.first_name,
            full_name=member.full_name,
            username=f"@{member.username}" if member.username else member.first_name,
        )
        await update.message.reply_text(formatted_msg)


def main():
    init_db()
    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        raise ValueError("BOT_TOKEN Environment Variable is missing!")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("on", bot_on))
    app.add_handler(CommandHandler("off", bot_off))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("setwelcome", set_welcome))
    app.add_handler(CommandHandler("info", info))
    app.add_handler(CommandHandler("adminhelp", admin_help))

    app.add_handler(
        MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member)
    )

    print("🤖 Welcome Bot is running on Railway...")
    app.run_polling()


if __name__ == "__main__":
    main()
