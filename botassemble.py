import os
import subprocess
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
import requests
gist_files_directory = "C:\\Users\\91934\\Desktop\\gist_files"  

# Create a dictionary to store user-specific execution data
user_data = {}
gist_urls = []

# Create a directory to store the Gist files

gist_directory = "gist_files"
os.makedirs(gist_directory, exist_ok=True)

# Handler function for the /install command
def install_gist(update: Update, context: CallbackContext):
    try:
        # Get the Gist URL from the message
        url = update.message.text.partition(' ')[2]

        # Check if the message text is empty
        if not url:
            update.message.reply_text("Please provide a Gist URL to install.")
            return

        # Extract the Gist ID from the URL
        gist_id = url.split("/")[-1]

        # Send a GET request to the GitHub API to retrieve the Gist information
        response = requests.get(f"https://api.github.com/gists/{gist_id}")

        # Check if the request was successful
        if response.status_code == 200:
            gist_info = response.json()

            # Extract the filenames and contents from the Gist information
            files = gist_info["files"]

            # Download and store each file from the Gist
            for file_name, file_data in files.items():
                file_content = file_data["content"]
                file_path = os.path.join(gist_directory, file_name)
                with open(file_path, "w") as file:
                    file.write(file_content)
                print(f"File '{file_name}' from Gist URL '{url}' downloaded and stored.")
            
            # Add the Gist URL to the list
            gist_urls.append(url)
            update.message.reply_text("Gist installed successfully.")
        else:
            update.message.reply_text("Failed to retrieve Gist information.")
    except Exception as e:
        # Log the exception
        print(f"An error occurred: {str(e)}")
        # You can also send an error message to the user if desired
        update.message.reply_text("An error occurred while installing the Gist.")
# Handler function for the /executecode command
def execute_code(update: Update, context: CallbackContext):
    try:
        # Get the file name from the message
        file_name = update.message.text.partition(' ')[2]

        # Check if the message text is empty
        if not file_name:
            update.message.reply_text("Please provide a file name to execute.")
            return

        # Check if the file exists
        file_path = os.path.join(gist_files_directory, file_name)
        if not os.path.isfile(file_path):
            update.message.reply_text(f"File '{file_name}' does not exist.")
            return

        # Store user-specific execution data in the user_data dictionary
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
        # Log the exception
        print(f"An error occurred: {str(e)}")
        # You can also send an error message to the user if desired
        update.message.reply_text("An error occurred while preparing for execution.")

# Handler function to execute code with user input
def execute_with_input(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id in user_data and user_data[user_id]["waiting_for_input"]:
        # Get the user input
        user_input = update.message.text

        # Get the file path and execute the code using subprocess
        file_path = user_data[user_id]["file_path"]
        result = subprocess.run(
            ['python', file_path],
            input=user_input,
            capture_output=True,
            text=True
        )

        # Update the output
        user_data[user_id]["output"] = result.stdout

        # Send the output back to the user
        update.message.reply_text(result.stdout)

        # Allow for another input
        user_data[user_id]["waiting_for_input"] = True
    else:
        update.message.reply_text("Invalid or unexpected input.")

# Handler function to stop code execution
def stop_execution(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id in user_data and user_data[user_id]["waiting_for_input"]:
        # Clear the user-specific execution data to stop execution
        del user_data[user_id]
        update.message.reply_text("Code execution stopped.")
    else:
        update.message.reply_text("No active code execution to stop.")

def remove_gist_file(update: Update, context: CallbackContext):
    try:
        # Get the file name from the message
        file_name = update.message.text.partition(' ')[2]

        # Check if the message text is empty
        if not file_name:
            update.message.reply_text("Please provide a file name to remove.")
            return

        # Check if the file exists
        file_path = os.path.join(gist_directory, file_name)
        if os.path.isfile(file_path):
            # Remove the file
            os.remove(file_path)
            update.message.reply_text(f"File '{file_name}' has been removed.")
        else:
            update.message.reply_text(f"File '{file_name}' does not exist.")
    except Exception as e:
        # Log the exception
        print(f"An error occurred: {str(e)}")
        # You can also send an error message to the user if desired
        update.message.reply_text("An error occurred while removing the file.")
def main():
    # Initialize the Telegram bot
    updater = Updater(token='6209324242:AAH4n4xK7fprk1SvAbOx-5I2BUvz68GBX60', use_context=True)
    dispatcher = updater.dispatcher

    # Add the /executecode command handler
    dispatcher.add_handler(CommandHandler('run', execute_code))

    # Add a MessageHandler for user input during code execution
    dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), execute_with_input))
    dispatcher.add_handler(CommandHandler('install', install_gist))

# Add the /runcode
    dispatcher.add_handler(CommandHandler('remove', remove_gist_file))

    # Add the /stop command handler
    dispatcher.add_handler(CommandHandler('stop', stop_execution))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
