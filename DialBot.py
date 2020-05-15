#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from torchtext.data.utils import _basic_english_normalize
import torch
import random
from argparse import ArgumentParser

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

#Load model and fields
text_field = torch.load('model/text_field.Field')
model = torch.load('model/model.pt', map_location=torch.device('cpu'))
torch.nn.Module.dump_patches = True
MAX_LENGTH = 10
# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')
    
def strategy(update, context):
    user = update.message.from_user
    logger.info("Strategy of %s: %s", user.first_name, update.message.text)
    update.message.reply_text('Okey')
    global decoding_strategy
    decoding_strategy = update.message.text



def echo(update, context):
    """Echo the user message."""
    sentence = ' '.join(_basic_english_normalize(update.message.text))
    with torch.no_grad():
        sentence = '<sos> ' + sentence + ' <eos>'
        sent_len = len(sentence.split())
        sentence = torch.Tensor([text_field.vocab.stoi[i] for i in sentence.lower().split()]).long().view(sent_len, 1)
        target = torch.Tensor([text_field.vocab.stoi['<sos>']]).long()
        output_sentence = ''
        encoder_outputs, hidden = model.encoder(sentence)
        for t in range(10):
            # first input to the decoder is the <sos> token
            output, hidden = model.decoder(target, hidden, encoder_outputs)
            if decoding_strategy=='top1':
              target = logits.max(1)[1]
            elif decoding_strategy=='topk':
              target = logits.topk(k)[1][0][random.randint(0, k-1)].unsqueeze(-1)
            else:
              target = torch.multinomial(logits.squeeze().div(temp).exp().cpu(), 1)

            word = text_field.vocab.itos[target.numpy()[0]]
            if word == '<eos>':
                break
            else:
                output_sentence = output_sentence + ' ' + word
    update.message.reply_text(output_sentence.strip().capitalize())


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("1135059011:AAHuqIWggoX9dECZSWo_csPj7xoTGf2CfQI", use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler('top1', strategy))
    dp.add_handler(CommandHandler('topk', strategy))
    dp.add_handler(CommandHandler('multinomial',strategy))
    dp.add_handler(CommandHandler("help", help))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
