#!/usr/bin/env python3

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram import InputMediaPhoto, ParseMode, ChatAction
import time
import logging
import data_loader
from telegram_token_key import m_token

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

def convert_income(input : str) -> float:
    num = input 
    thousand = False
    if num[-1] == 'k' or num[-1] == 'K':
        num = num[0:-1]
        thousand = True
    num = int(num)
    if thousand:
        num *= 1000.0
    return num


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def help(update: Update, _: CallbackContext) -> None:
    update.message.reply_text('Help Menu:\n'
                             '/help - Print this menu\n'
                             '/info - to print the README')

def info(update: Update, _: CallbackContext) -> None:
    readme = open("README.md", "r")
    outString = readme.read()
    update.message.reply_text(outString)
    readme.close()

def income_calculator(update: Update, context : CallbackContext) -> None:
    try:
        if len(context.args) < 3:
            raise KeyError("User needs to provide three inputs")
        income = convert_income(context.args[0])
        country = context.args[1]
        state = " ".join(context.args[2:])
        print(income, country, state)
        update.message.reply_text(data_loader.state_summary(country, state, income))
    except KeyError:
        update.message.reply_text("Usage: /calc <income> <Country> <State>")

def compare_states(update: Update, context : CallbackContext) -> None:
    try:
        data_loader.plotComparisons(context.args)
        image = open('graph.png', 'rb')
        update.message.reply_photo(image)
        image.close()
    except KeyError:
        update.message.reply_text("Couldn't find one of the states, check the state codes, and try again")

def compare_states_taxes(update: Update, context : CallbackContext) -> None:
    try:
        data_loader.plotComparisons(context.args, plotIncome=False)
        image = open('graph.png', 'rb')
        update.message.reply_photo(image)
        image.close()
    except KeyError:
        update.message.reply_text("Couldn't find one of the states, check the state codes, and try again")

def compare_states_rates(update: Update, context : CallbackContext) -> None:
    try:
        data_loader.plotComparisons(context.args, plotIncome=False, plotRate=True)
        image = open('graph.png', 'rb')
        update.message.reply_photo(image)
        image.close()
    except KeyError:
        update.message.reply_text("Couldn't find one of the states, check the state codes, and try again")

def list_state_codes(udpate : Update, context : CallbackContext) -> None:
    return

def main() -> None:
    """Run bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(m_token)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    function_list = {
        "start": help,
        "calc" : income_calculator,
        "compare" : compare_states,
        "compare_taxes" : compare_states_taxes,
        "compare_rates" : compare_states_rates,
        "help" : help,
        "info" : info
        }
    for key, value in function_list.items():
        dispatcher.add_handler(CommandHandler(key, value))

    # Start the Bot
    updater.start_polling()

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
