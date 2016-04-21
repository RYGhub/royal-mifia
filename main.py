from telegram.ext import Updater
import filemanager

token = filemanager.readfile('telegramapi.txt')
updater = Updater(token)


def ping(bot, update):
    bot.sendMessage(update.message.chat.id, "Pong!")

updater.dispatcher.addTelegramCommandHandler('ping', ping)
updater.start_polling()