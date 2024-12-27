from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext
import hashlib

# Dictionary to store file IDs and file names (maps file ID to file name)
file_storage = {}

# Start command handler
def start(update: Update, context: CallbackContext) -> None:
    # Extract callback_data from the /start link
    callback_data = update.message.text.split(' ')[-1] if len(update.message.text.split(' ')) > 1 else None

    if callback_data and len(callback_data) == 32:  # Check if it's a valid hash
        # Retrieve the file ID from the stored data
        file_id = next((key for key in file_storage if hashlib.md5(key.encode()).hexdigest() == callback_data), None)

        if file_id:
            # Generate the "Get your file" button
            keyboard = [[InlineKeyboardButton("Get your file", callback_data=callback_data)]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text("Click the button below to retrieve your file.", reply_markup=reply_markup)
        else:
            update.message.reply_text("Sorry, I couldn't find the file associated with this link.")
    else:
        # If no callback_data or invalid callback_data, show the default welcome message
        update.message.reply_text("Welcome! Send me a video file ending with .mp4 or .mkv, and I'll save it for you.")

# Video file handler
def handle_video(update: Update, context: CallbackContext) -> None:
    if update.message.video:
        video = update.message.video

        # Check if the file name ends with .mp4 or .mkv
        file_name = video.file_name if video.file_name else "video.mp4"  # Default name if no name provided
        if not (file_name.endswith(".mp4") or file_name.endswith(".mkv")):
            update.message.reply_text("Please send a video file with .mp4 or .mkv extension.")
            return

        # Save the video details
        file_id = video.file_id
        file_storage[file_id] = file_name

        # Create a hash of the file_id to use as callback data
        callback_data = hashlib.md5(file_id.encode()).hexdigest()

        # Create the retrieve link
        bot_username = context.bot.username
        retrieve_link = f"https://t.me/{bot_username}?start={callback_data}"

        # Send the retrieve link to the user who uploaded the video
        update.message.reply_text(
            f"Video saved! Share this link with anyone to retrieve the file:\n{retrieve_link}"
        )
    else:
        update.message.reply_text("Please send a valid video file ending with .mp4 or .mkv.")

# Callback query handler for "Get your file" button
def retrieve_file(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    # Retrieve the file ID using the callback data
    callback_data = query.data
    file_id = next((key for key in file_storage if hashlib.md5(key.encode()).hexdigest() == callback_data), None)

    if file_id:
        file_name = file_storage[file_id]

        # Send the file back to the user
        context.bot.send_video(
            chat_id=query.message.chat.id,
            video=file_id,
            caption=f"Here's your file: {file_name}"
        )
    else:
        query.message.reply_text("Sorry, I couldn't find the file.")

# Main function
def main() -> None:
    # Replace 'YOUR_API_TOKEN' with your actual Telegram Bot API token
    updater = Updater("7777349321:AAHYFjctrufAV2VhFXkKtwcibzwoDTfnwPk")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add command handler for /start
    dp.add_handler(CommandHandler("start", start))

    # Add handler to handle video files
    dp.add_handler(MessageHandler(Filters.video & ~Filters.command, handle_video))

    # Add handler for callback queries (when a user clicks the inline button)
    dp.add_handler(CallbackQueryHandler(retrieve_file))

    # Start the bot
    updater.start_polling()
  # Run the bot until you send a signal (Ctrl+C)
    updater.idle()

if name == 'main':
    main()
