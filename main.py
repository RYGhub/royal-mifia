from telegram.ext import Updater
import filemanager

token = filemanager.readfile('telegramapi.txt')
updater = Updater(token)


# Ruoli possibili per i giocatori
# Base di un ruolo
class Role:
    icon = str()
    team = 'None'  # Squadra: 'None', 'Good', 'Evil'
    haspower = False
    poweruses = 0

    def power(self):
        pass

    def onendday(self):
        pass


class Royal(Role):
    icon = "\U0001F610"
    team = 'Good'


class Mifioso(Role):
    icon = "\U0001F47F"
    team = 'Evil'
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
    team = 'Good'
    haspower = True
    poweruses = 1

    def power(self):
        # Visualizza il ruolo di qualcuno
        pass

    def onendday(self):
        # Ripristina il potere
        self.poweruses = 1


# Classi per i giocatori
class Player:
    tid = int()
    tusername = str()
    role = Role()  # Di base, ogni giocatore è un ruolo indefinito
    alive = True
    votingfor = str()

    def message(self, bot, text):
        bot.sendMessage(self.tid, text)

    def __init__(self, tid, tusername):
        self.tid = tid
        self.tusername = tusername


# Classe di ogni partita
class Game:
    adminid = int()
    groupid = int()
    players = list()
    tokill = list()  # Giocatori che verranno uccisi all'endday
    phase = 'Join'  # Fase di gioco: 'Join', 'Voting', 'Ended'

    def __init__(self, groupid, adminid):
        self.groupid = groupid
        self.adminid = adminid

    def message(self, bot, text):
        bot.sendMessage(self.groupid, text)

    def adminmessage(self, bot, text):
        bot.sendMessage(self.adminid, text)

    def mifiamessage(self, bot, text):
        # Trova tutti i mifiosi nell'elenco dei giocatori
        for player in self.players:
            if isinstance(player.role, Mifioso):
                player.message(bot, text)
        # Inoltra il messaggio all'admin
        self.adminmessage(bot, text)


# Comandi a cui risponde il bot
def ping(bot, update):
    bot.sendMessage(update.message.chat.id, "Pong!")

updater.dispatcher.addTelegramCommandHandler('ping', ping)
updater.start_polling()