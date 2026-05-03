import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.constants import ParseMode
from config import BOT_TOKEN, ADMIN_ID, SOURCE_CHANNELS, TARGET_CHANNEL, PHONE_NUMBER, CUSTOM_MAPPING
from database import Database
from tg_client import TelegramClientManager
from dumper import Dumper

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

db = Database()
client_manager = TelegramClientManager(PHONE_NUMBER)
dumper = Dumper(client_manager, db)

# Store dumping tasks
dumping_tasks = {}

async def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID

async def main_menu():
    keyboard = [
        [InlineKeyboardButton("📊 Daily Stats", callback_data="stats_daily"),
         InlineKeyboardButton("📈 Monthly Stats", callback_data="stats_monthly")],
        [InlineKeyboardButton("📋 Source Stats", callback_data="stats_sources"),
         InlineKeyboardButton("🔄 Start/Stop Dumping", callback_data="toggle_menu")],
        [InlineKeyboardButton("▶️ Start All", callback_data="start_all"),
         InlineKeyboardButton("⏸️ Stop All", callback_data="stop_all")],
        [InlineKeyboardButton("🔐 Login Status", callback_data="login_status"),
         InlineKeyboardButton("ℹ️ About", callback_data="about")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized!")
        return
    
    if not client_manager.is_connected():
        await update.message.reply_text("🔄 Please login first. Sending OTP...")
        await client_manager.start()
        await update.message.reply_text("✅ Login successful! Bot is ready.")
    
    await update.message.reply_text(
        "🤖 **Advanced Dumping Bot Active**\n\n"
        "Use buttons below to control dumping operations.\n\n"
        f"📤 Target Channel: `{TARGET_CHANNEL}`\n"
        f"📥 Source Channels: {len(SOURCE_CHANNELS)}\n"
        f"🔄 Status: {'Running' if dumper.is_running else 'Stopped'}",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=await main_menu()
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if not await is_admin(query.from_user.id):
        await query.edit_message_text("❌ Unauthorized!")
        return
    
    data = query.data
    
    if data == "stats_daily":
        daily = db.get_daily_stats()
        await query.edit_message_text(f"📊 **Today's Total Dumps:** `{daily}`", parse_mode=ParseMode.MARKDOWN, reply_markup=await main_menu())
    
    elif data == "stats_monthly":
        monthly = db.get_monthly_stats()
        await query.edit_message_text(f"📈 **This Month's Total Dumps:** `{monthly}`", parse_mode=ParseMode.MARKDOWN, reply_markup=await main_menu())
    
    elif data == "stats_sources":
        msg = "📋 **Source Channels Stats:**\n\n"
        for src in SOURCE_CHANNELS:
            stats = db.get_source_stats(src)
            msg += f"• `{src}`: {stats['total']} total | {stats['daily']} today\n"
        await query.edit_message_text(msg, parse_mode=ParseMode.MARKDOWN, reply_markup=await main_menu())
    
    elif data == "toggle_menu":
        keyboard = []
        for src in SOURCE_CHANNELS:
            active, _ = db.get_dumping_status(src)
            status = "✅" if active else "❌"
            keyboard.append([InlineKeyboardButton(f"{status} {src}", callback_data=f"toggle_{src}")])
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="back")])
        await query.edit_message_text("🔄 **Toggle dumping per channel:**", reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data.startswith("toggle_"):
        src = int(data.split("_")[1])
        active, _ = db.get_dumping_status(src)
        db.set_dumping_status(src, not active)
        await query.answer(f"Dumping {'started' if not active else 'stopped'} for {src}")
        # Restart dumper if needed
        if dumper.is_running:
            await dumper.stop()
            await dumper.start()
        await query.edit_message_text("✅ Updated!", reply_markup=await main_menu())
    
    elif data == "start_all":
        for src in SOURCE_CHANNELS:
            db.set_dumping_status(src, True)
        if not dumper.is_running:
            await dumper.start()
        await query.edit_message_text("✅ All sources started!", reply_markup=await main_menu())
    
    elif data == "stop_all":
        for src in SOURCE_CHANNELS:
            db.set_dumping_status(src, False)
        if dumper.is_running:
            await dumper.stop()
        await query.edit_message_text("⏸️ All sources stopped!", reply_markup=await main_menu())
    
    elif data == "login_status":
        status = "✅ Logged in" if client_manager.is_connected() else "❌ Not logged in"
        await query.edit_message_text(f"🔐 **Login Status:** {status}", parse_mode=ParseMode.MARKDOWN, reply_markup=await main_menu())
    
    elif data == "about":
        await query.edit_message_text(
            "🤖 **Advanced Dumping Bot v1.0**\n\n"
            "Features:\n"
            "• Multi-source dumping\n"
            "• Custom source→target mapping\n"
            "• Daily/Monthly stats\n"
            "• Per-source toggle\n"
            "• 24/7 operation\n\n"
            "Made for @Aryan",
            reply_markup=await main_menu()
        )
    
    elif data == "back":
        await query.edit_message_text("Main Menu", reply_markup=await main_menu())

async def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback))
    
    # Start dumper
    await dumper.start()
    
    logger.info("Bot started!")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
