#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-
from telegram.ext import Updater, CommandHandler
import filemanager
import random
import strings as s

import logging
logger = logging.getLogger()
logger.setLevel(logging.WARN)

logging.basicConfig(level=logging.WARN,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

token = filemanager.readfile('telegramapi.txt')
updater = Updater(token)


# Ruoli possibili per i giocatori
# Base di un ruolo
class Role:
    """Classe base di un ruolo. Da qui si sviluppano tutti gli altri ruoli."""
    def __init__(self):
        self.icon = "-"  # Icona del ruolo, da visualizzare di fianco al nome
        self.team = 'None'  # Squadra: 'None', 'Good', 'Evil'
        self.name = "UNDEFINED"  # Nome del ruolo, viene visualizzato dall'investigatore e durante l'assegnazione dei ruoli

    def power(self, bot, game: Game, player: Player, arg: str):
        """Il potere del ruolo. Si attiva quando il bot riceve un /power in chat privata."""
        pass

    def onendday(self, bot, game: Game):
        """Metodo chiamato alla fine di ogni giorno, per attivare o ripristinare allo stato iniziale il potere."""
        pass


class Royal(Role):
    """Un membro della Royal Games. Il ruolo principale, non ha alcun potere se non quello di votare."""
    def __init__(self):
        super().__init__()
        self.icon = s.royal_icon
        self.team = 'Good'
        self.name = s.royal_name


class Mifioso(Role):
    """Il nemico globale. Può impostare come bersaglio una persona al giorno, per poi ucciderla alla fine."""
    def __init__(self):
        super().__init__()
        self.icon = s.mifia_icon
        self.team = 'Evil'
        self.target = None
        self.name = s.mifia_name

    def power(self, bot, game: Game, player: Player, arg: str):
        # Imposta una persona come bersaglio da uccidere.
        self.target = game.findplayerbyusername(arg)
        if self.target is not None:
            player.message(bot, s.mifia_target_selected.format(target=self.target.tusername))

    def onendday(self, bot, game: Game):
        # Uccidi il bersaglio se non è protetto da un Angelo.
        if self.target is not None:
            if self.target.protectedby is None:
                self.target.kill()
                game.message(bot, s.mifia_target_killed.format(target=self.target.tusername, icon=self.target.role.icon, role=self.target.role.name))
            else:
                game.message(bot, s.mifia_target_protected.format(target=self.target.tusername, icon=self.target.protectedby.role.icon,
                                          protectedby=self.target.protectedby.tusername))
            self.target = None


class Investigatore(Role):
    """L'investigatore può indagare sul vero ruolo di una persona una volta al giorno."""
    def __init__(self):
        super().__init__()
        self.icon = s.detective_icon
        self.team = 'Good'
        self.poweruses = 1
        self.name = s.detective_name

    def power(self, bot, game: Game, player: Player, arg: str):
        # Indaga sul vero ruolo di una persona, se sono ancora disponibili usi del potere.
        if self.poweruses > 0:
            target = game.findplayerbyusername(arg)
            if target is not None:
                self.poweruses -= 1
                player.message(bot, s.detective_discovery
                                    .format(target=target.tusername, icon=target.role.icon, role=target.role.name, left=self.poweruses))
            else:
                player.message(bot, s.error_username)
        else:
            player.message(bot, s.error_no_uses)

    def onendday(self, bot, game: Game):
        # Ripristina il potere
        self.poweruses = 1


class Angelo(Role):
    """L'angelo può proteggere una persona al giorno dalla Mifia. Se ha successo nella protezione, il suo ruolo sarà rivelato a tutti."""
    def __init__(self):
        super().__init__()
        self.icon = s.angel_icon
        self.team = 'Good'  # Squadra: 'None', 'Good', 'Evil'
        self.name = s.angel_name
        self.protecting = None  # La persona che questo angelo sta proteggendo
    
    def power(self, bot, game: Game, player: Player, arg: str):
        # Imposta qualcuno come protetto
        selected = game.findplayerbyusername(arg)
        if player is not selected and selected is not None:
            selected.protectedby = player
            self.protecting = selected
            player.message(bot, s.angel_target_selected.format(target=self.protecting.tusername))
            
    def onendday(self, bot, game: Game):
        # Resetta la protezione
        if self.protecting is not None:
            self.protecting.protectedby = None
        self.protecting = None


class Player:
    """Classe di un giocatore. Contiene tutti i dati riguardanti un giocatore all'interno di una partita, come il ruolo, e i dati riguardanti telegram, come ID e username.""" 
    def message(self, bot, text: str):
        """Manda un messaggio privato al giocatore."""
        bot.sendMessage(self.tid, text)

    def kill(self):
        """Uccidi il giocatore."""
        # Perchè questo esiste?
        self.alive = False

    def __init__(self, tid: int, tusername: str):
        self.tid = tid  # ID di Telegram
        self.tusername = tusername  # Username di Telegram
        self.role = Role()  # Di base, ogni giocatore è un ruolo indefinito
        self.alive = True
        self.votingfor = None  # Diventa un player se ha votato
        self.votes = 0  # Voti che sta ricevendo questo giocatore. Aggiornato da updatevotes()
        self.protectedby = None  # Protettore. Oggetto player che protegge questo giocatore dalla mifia.


class Game:
    """Classe di una partita, contenente parametri riguardanti stato della partita e informazioni sul gruppo di Telegram."""
    def __init__(self, groupid: int, adminid: int):
        self.groupid = groupid  # ID del gruppo in cui si sta svolgendo una partita
        self.adminid = adminid  # ID telegram dell'utente che ha creato la partita con /newgame
        self.players = list()  # Lista dei giocatori in partita
        self.tokill = list()  # Giocatori che verranno uccisi all'endday
        self.phase = 'Join'  # Fase di gioco: 'Join', 'Voting', 'Ended'

    def message(self, bot, text: str):
        """Manda un messaggio nel gruppo."""
        bot.sendMessage(self.groupid, text)

    def adminmessage(self, bot, text: str):
        """Manda un messaggio privato al creatore della partita."""
        bot.sendMessage(self.adminid, text)

    def mifiamessage(self, bot, text: str):
        """Manda un messaggio privato a tutti i Mifiosi nella partita."""
        # Trova tutti i mifiosi nell'elenco dei giocatori
        for player in self.players:
            if isinstance(player.role, Mifioso):
                player.message(bot, text)
        # Inoltra il messaggio all'admin
        self.adminmessage(bot, text)

    def findplayerbyid(self, tid: int) -> Player:
        """Trova il giocatore con un certo id."""
        for player in self.players:
            if player.tid == tid:
                return player
        else:
            return None

    def findplayerbyusername(self, tusername: str) -> Player:
        """Trova il giocatore con un certo username."""
        for player in self.players:
            if player.tusername.lower() == tusername.lower():
                return player
        else:
            return None

    def assignroles(self, bot, mifia=0: int, investigatore=0: int, angelo=0: int):
        """Assegna ruoli casuali a tutti i giocatori."""
        random.seed()
        playersleft = self.players.copy()
        random.shuffle(playersleft)
        # Seleziona mifiosi
        while mifia > 0:
            try:
                selected = playersleft.pop()
            except IndexError:
                raise IndexError(s.error_not_enough_players)
            else:
                selected.role = Mifioso()
                mifia -= 1
        # Seleziona detective
        while investigatore > 0:
            try:
                selected = playersleft.pop()
            except IndexError:
                raise IndexError(s.error_not_enough_players)
            else:
                selected.role = Investigatore()
                investigatore -= 1
        # Seleziona angeli
        while angelo > 0:
            try:
                selected = playersleft.pop()
            except IndexError:
                raise IndexError(s.error_not_enough_players)
            else:
                selected.role = Angelo()
                angelo -= 1
        # Assegna il ruolo di Royal a tutti gli altri
        for player in playersleft:
            player.role = Royal()
        # Manda i ruoli assegnati a tutti
        for player in self.players:
            player.message(bot, s.role_assigned.format(icon=player.role.icon, name=player.role.name))

    def updatevotes(self):
        """Aggiorna il conteggio dei voti di tutti i giocatori."""
        for player in self.players:
            player.votes = 0
        for player in self.players:
            if player.votingfor is not None:
                player.votingfor.votes += 1

    def mostvotedplayer(self) -> Player:
        """Trova il giocatore più votato."""
        mostvoted = None
        self.updatevotes()
        for player in self.players:
            # Temo di aver fatto un disastro. Ma finchè va...
            if mostvoted is None and player.votes == 0:
                pass
            elif (mostvoted is None and player.votes >= 1) or (player.votes > mostvoted.votes):
                mostvoted = player
            elif mostvoted is not None and player.votes == mostvoted.votes:
                # Questo algoritmo non è equo per un pareggio a tre. Riscriverlo se c'è qualche problema
                mostvoted = random.choice([player, mostvoted])
        return mostvoted

    def endday(self, bot):
        """Finisci la giornata, esegui gli endday di tutti i giocatori e uccidi il più votato del giorno."""
        # Fai gli endday in un certo ordine.
        # Si potrebbe fare più velocemente, credo.
        # Ma non sto a ottimizzare senza poter eseguire il programma, quindi vado sul sicuro.
        # Mifiosi
        for player in self.players:
            if isinstance(player.role, Mifioso):
                player.role.onendday(bot, self)
        # Investigatori
        for player in self.players:
            if isinstance(player.role, Investigatore):
                player.role.onendday(bot, self)
        # Angeli
        for player in self.players:
            if isinstance(player.role, Angelo):
                player.role.onendday(bot, self)
        lynched = self.mostvotedplayer()
        if lynched is not None:
            self.message(bot, s.player_lynched.format(name=lynched.tusername, icon=lynched.role.icon, role=lynched.role.name))
            lynched.kill()
        else:
            self.message(bot, s.no_players_lynched)
        for player in self.players:
            player.votingfor = None
        # Condizioni di vittoria
        royal = 0
        mifiosi = 0
        for player in self.players:
            if player.alive and player.role.team == 'Evil':
                mifiosi += 1
            elif player.alive and player.role.team == 'Good':
                royal += 1
        if mifiosi >= royal:
            self.message(bot, s.victory_mifia)
            self.endgame()
        elif mifiosi == 0:
            self.message(bot, s.victory_royal)
            self.endgame()

    def endgame(self):
        inprogress.remove(self)

# Partite in corso
inprogress = list()


def findgamebyid(gid: int) -> Game:
    """Trova una partita con un certo id."""
    for game in inprogress:
        if game.groupid == gid:
            return game


# Comandi a cui risponde il bot
def ping(bot, update):
    """Ping!"""
    bot.sendMessage(update.message.chat['id'], s.pong)


def newgame(bot, update):
    """Crea una nuova partita."""
    if update.message.chat['type'] != 'private':
        g = findgamebyid(update.message.chat['id'])
        if g is None:
            g = Game(update.message.chat['id'], update.message.from_user['id'])
            inprogress.append(g)
            bot.sendMessage(update.message.chat['id'], s.new_game.format(g.groupid))
        else:
            bot.sendMessage(update.message.chat['id'], s.error_game_in_progress)
    else:
        bot.sendMessage(update.message.chat['id'], s.error_chat_type)


def join(bot, update):
    """Unisciti a una partita."""
    game = findgamebyid(update.message.chat['id'])
    if game is not None:
        if game.phase == 'Join':
            p = game.findplayerbyid(update.message.from_user['id'])
            if p is None:
                p = Player(update.message.from_user['id'], update.message.from_user['username'])
                game.players.append(p)
                bot.sendMessage(update.message.chat['id'], s.player_joined.format(name=p.tusername))
            else:
                bot.sendMessage(update.message.chat['id'], s.error_player_already_joined)


def debug(bot, update):
    """Visualizza tutti i ruoli e gli id."""
    game = findgamebyid(update.message.chat['id'])
    if game is None:
        bot.sendMessage(update.message.chat['id'], s.error_no_games_found)
    else:
        if game.adminid == update.message.from_user['id']:
            text = s.status_header.format(name=game.groupid, admin=game.adminid, phase=game.phase)
            game.updatevotes()
            # Aggiungi l'elenco dei giocatori
            for player in game.players:
                if not player.alive:
                    text += s.status_dead_player.format(name=player.tusername)
                elif player.votingfor is not None:
                    text += s.status_voting_player.format(icon=player.role.icon, name=player.tusername, votes=player.votes, voting=player.votingfor.tusername)
                else:
                    text += s.status_idle_player.format(icon=player.role.icon, name=player.tusername, votes=player.votes)
            bot.sendMessage(update.message.from_user['id'], text)


def status(bot, update):
    """Visualizza lo stato della partita."""
    game = findgamebyid(update.message.chat['id'])
    if game is None:
        bot.sendMessage(update.message.chat['id'], s.error_no_games_found)
    else:
        text = s.status_header.format(name=game.groupid, admin=game.adminid, phase=game.phase)
        game.updatevotes()
        # Aggiungi l'elenco dei giocatori
        for player in game.players:
            if not player.alive:
                text += s.status_dead_player.format(player.tusername)
            elif player.votingfor is not None:
                text += s.status_voting_player.format(icon="\U0001F610", name=player.tusername, votes=player.votes, voting=player.votingfor.tusername)
            else:
                text += s.status_idle_player.format(icon="\U0001F610", name=player.tusername, votes=player.votes)
        bot.sendMessage(update.message.chat['id'], text)


def endjoin(bot, update):
    """Termina la fase di join e inizia quella di votazione."""
    game = findgamebyid(update.message.chat['id'])
    if game is not None and game.phase is 'Join' and update.message.from_user['id'] == game.adminid:
        game.phase = 'Voting'
        game.message(bot, s.join_phase_ended)
        try:
            game.assignroles(bot, mifia=1, investigatore=0, angelo=1)
        except IndexError:
            game.message(bot, s.error_not_enough_players)
            game.endgame()
        else:
            bot.sendMessage(update.message.chat['id'], s.roles_assigned_successfully)



def vote(bot, update):
    """Vota per uccidere una persona."""
    game = findgamebyid(update.message.chat['id'])
    if game is not None and game.phase is 'Voting':
        player = game.findplayerbyid(update.message.from_user['id'])
        if player is not None and player.alive:
            target = game.findplayerbyusername(update.message.text.split(' ')[1])
            if target is not None:
                player.votingfor = target
                bot.sendMessage(update.message.chat['id'], s.vote.format(voted=target.tusername))
            else:
                bot.sendMessage(update.message.chat['id'], s.error_username)
        else:
            bot.sendMessage(update.message.chat['id'], s.error_dead)
    else:
        bot.sendMessage(update.message.chat['id'], s.error_no_games_found)


def endday(bot, update):
    """Termina la giornata attuale."""
    game = findgamebyid(update.message.chat['id'])
    if game is not None and game.phase is 'Voting' and update.message.from_user['id'] == game.adminid:
        game.endday(bot)


def power(bot, update):
    """Attiva il potere del tuo ruolo."""
    if update.message.chat['type'] == 'private':
        # Ho un'idea su come farlo meglio. Forse.
        cmd = update.message.text.split(' ', 2)
        game = findgamebyid(int(cmd[1]))
        if game is not None:
            player = game.findplayerbyid(update.message.from_user['id'])
            if player.alive:
                player.role.power(bot, game, player, cmd[2])
            else:
                bot.sendMessage(update.message.chat['id'], s.error_dead)
        else:
            bot.sendMessage(update.message.chat['id'], s.error_no_games_found)
    else:
        bot.sendMessage(update.message.chat['id'], s.error_private_required)


def debuggameslist(bot, update):
    """Visualizza l'elenco delle partite in corso."""
    bot.sendMessage(repr(inprogress))

updater.dispatcher.addHandler(CommandHandler('ping', ping))
updater.dispatcher.addHandler(CommandHandler('newgame', newgame))
updater.dispatcher.addHandler(CommandHandler('join', join))
updater.dispatcher.addHandler(CommandHandler('debug', debug))
updater.dispatcher.addHandler(CommandHandler('endjoin', endjoin))
updater.dispatcher.addHandler(CommandHandler('vote', vote))
updater.dispatcher.addHandler(CommandHandler('v', vote))
updater.dispatcher.addHandler(CommandHandler('endday', endday))
updater.dispatcher.addHandler(CommandHandler('power', power))
updater.dispatcher.addHandler(CommandHandler('status', status))
updater.dispatcher.addHandler(CommandHandler('s', status))
updater.dispatcher.addHandler(CommandHandler('debuggameslist', debuggameslist))
updater.start_polling()
updater.idle()
