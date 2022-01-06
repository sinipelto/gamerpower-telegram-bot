import threading
import time

import dotenv
from telegram import Update, Bot, ParseMode
from telegram.ext import Updater, CallbackContext, CommandHandler, MessageHandler, Filters, Dispatcher

import giveaway
import msg_parser

import builtins

config = dotenv.dotenv_values(".env")

# Ensure all prints get flushed in the logs immediately
def print(*args, **kwargs):
	kwargs['flush'] = True
	builtins.print(*args, **kwargs)


def process_giveaways(bot: Bot):
    print("Fetching giveaways..")
    data = giveaway.fetch_active_giveaways()

    print("Initialize database for use..")
    giveaway.init_db()

    print("Filtering new giveaways..")
    filtered = giveaway.filter_giveaways(
        data,
        True,
        float(config["MIN_VALUE"]) if config["MIN_VALUE"] != "None" else None,
        float(config["MAX_VALUE"]) if config["MAX_VALUE"] != "None" else None
    )

    if len(filtered) <= 0:
        print("No new giveaways detected. Exiting..")
        return

    for entry in filtered:
        ga = msg_parser.GiveawayMessage()
        ga.title = entry['title']
        ga.description = entry['description']
        ga.platform = entry['platforms']
        ga.price = entry['worth']
        ga.link = entry['open_giveaway']
        # ga.image = entry['image']

        msg = msg_parser.parse_template(config["MSG_GIVEAWAY"], ga)

        bot.send_message(
            chat_id=config["CHANNEL_ID"],
            text=msg,
            parse_mode=ParseMode.HTML
        )

    print("Sending giveaway message(s) done.")

    print("Inserting notified giveaways to db..")
    giveaway.insert_giveaways(filtered)


running = False


def giveaway_thread(bot: Bot):
    timeout = float(config["CHECK_INTERVAL"])
    slept = 0.0
    while running:
        time.sleep(1.0)
        slept += 1.0
        if slept < timeout:
            continue
        slept = 0.0
        print("Checking giveaways..")
        try:
            process_giveaways(bot)
        except Exception as exc:
            print(f"ERROR: Failed to process giveaways: {exc!r}")


def unknown_handler(update: Update, context: CallbackContext):
    print(f"Received unknown command: {update.effective_message.text}")
    with open(config["MSG_UNKNOWN"], "r", encoding="utf-8") as f:
        msg = f.read()
    try:
        context.bot.send_message(chat_id=update.effective_chat.id, text=msg)
    except Exception as exc:
        print(f"ERROR: {exc!r}")


def start_handler(update: Update, context: CallbackContext) -> None:
    print("Received start command.")
    with open(config["MSG_WELCOME"], "r", encoding="utf-8") as f:
        msg = f.read()
    try:
        context.bot.send_message(chat_id=update.effective_chat.id, text=msg)
    except Exception as exc:
        print(f"ERROR: {exc!r}")


def subscribe_handler(update: Update, context: CallbackContext) -> None:
    pass


def unsubscribe_handler(update: Update, context: CallbackContext) -> None:
    pass


def main() -> None:
    print("Starting up..")

    updater = Updater(token=config["TG_TOKEN"])
    dispatcher: Dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start_handler))
    dispatcher.add_handler(CommandHandler('help', start_handler))

    dispatcher.add_handler(MessageHandler(Filters.command, unknown_handler))
    print("Configured bot.")

    updater.start_polling()
    print("Started listening.")

    check_thread = threading.Thread(target=giveaway_thread, args=(updater.bot,))

    global running
    running = True

    check_thread.start()
    print("Giveaway thread started.")

    print("Waiting for incoming events..")
    updater.idle()

    running = False
    check_thread.join(timeout=float(config["KILL_TIMEOUT"]))

    print("Main thread exiting.")


if __name__ == '__main__':
    try:
        main()
    except Exception as ex:
        print(f"ERROR during execution of main: {ex!r}")
