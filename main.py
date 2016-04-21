from telegram.ext import Updater
import filemanager

token = filemanager.readfile('telegramapi.txt')
updater = Updater(token)


# Ruoli possibili per i giocatori
# Base di un ruolo
class Role:
    icon = str()
    haspower = False
    poweruses = 0

    def power(self):
        pass

    def onendday(self):
        pass


class Royal(Role):
    icon = "\U0001F610"


class Mifioso(Role):
    icon = "\U0001F47F"
    haspower = True
    poweruses = 1
    target = None

    def power(self):
        # Imposta qualcuno come bersaglio
        pass

    def onendday(self):
        # Ripristina il potere
        self.poweruses = 1
        # Uccidi il bersaglio


class Investigatore(Role):
    icon = "\U0001F575"
    haspower = True
    poweruses = 1

    def power(self):
        # Visualizza il ruolo di qualcuno
        pass

    def onendday(self):
        # Ripristina il potere
        self.poweruses = 1


# Comandi a cui risponde il bot
def ping(bot, update):
    bot.sendMessage(update.message.chat.id, "Pong!")

updater.dispatcher.addTelegramCommandHandler('ping', ping)
updater.start_polling()