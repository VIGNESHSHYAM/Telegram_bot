import os
import subprocess
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
import requests
gist_files_directory = "C:\\Users\\91934\\Desktop\\gist_files"  

user_data = {}
gist_urls = []


gist_directory = "gist_files"
os.makedirs(gist_directory, exist_ok=True)

def install_gist(update: Update, context: CallbackContext):
    try:
        url = update.message.text.partition(' ')[2]

        if not url:
            update.message.reply_text("Please provide a Gist URL to install.")
            return

        gist_id = url.split("/")[-1]

        response = requests.get(f"https://api.github.com/gists/{gist_id}")

        if response.status_code == 200:
            gist_info = response.json()

            files = gist_info["files"]

            for file_name, file_data in files.items():
                file_content = file_data["content"]
                file_path = os.path.join(gist_directory, file_name)
                with open(file_path, "w") as file:
                    file.write(file_content)
                print(f"File '{file_name}' from Gist URL '{url}' downloaded and stored.")
            
            gist_urls.append(url)
            update.message.reply_text("Gist installed successfully.")
        else:
            update.message.reply_text("Failed to retrieve Gist information.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        update.message.reply_text("An error occurred while installing the Gist.")
def execute_code(update: Update, context: CallbackContext):
    try:
        file_name = update.message.text.partition(' ')[2]

        if not file_name:
            update.message.reply_text("Please provide a file name to execute.")
            return

        file_path = os.path.join(gist_files_directory, file_name)
        if not os.path.isfile(file_path):
            update.message.reply_text(f"File '{file_name}' does not exist.")
            return

        user_id = update.message.from_user.id
        user_data[user_id] = {
            "file_path": file_path,
            "waiting_for_input": True,
            "output": "",
        }

        update.message.reply_text(
            f"File '{file_name}' is ready for execution. Send your input message."
        )
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        update.message.reply_text("An error occurred while preparing for execution.")

def execute_with_input(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id in user_data and user_data[user_id]["waiting_for_input"]:
        user_input = update.message.text

        file_path = user_data[user_id]["file_path"]
        result = subprocess.run(
            ['python', file_path],
            input=user_input,
            capture_output=True,
            text=True
        )

        user_data[user_id]["output"] = result.stdout

        update.message.reply_text(result.stdout)

        user_data[user_id]["waiting_for_input"] = True
    else:
        update.message.reply_text("Invalid or unexpected input.")

def stop_execution(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id in user_data and user_data[user_id]["waiting_for_input"]:
        del user_data[user_id]
        update.message.reply_text("Code execution stopped.")
    else:
        update.message.reply_text("No active code execution to stop.")

def remove_gist_file(update: Update, context: CallbackContext):
    try:
        file_name = update.message.text.partition(' ')[2]

        if not file_name:
            update.message.reply_text("Please provide a file name to remove.")
            return

        file_path = os.path.join(gist_directory, file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)
            update.message.reply_text(f"File '{file_name}' has been removed.")
        else:
            update.message.reply_text(f"File '{file_name}' does not exist.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        update.message.reply_text("An error occurred while removing the file.")
def main():
    updater = Updater(token='your bot token', use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('run', execute_code))

    dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), execute_with_input))
    dispatcher.add_handler(CommandHandler('install', install_gist))

    dispatcher.add_handler(CommandHandler('remove', remove_gist_file))

    dispatcher.add_handler(CommandHandler('stop', stop_execution))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
