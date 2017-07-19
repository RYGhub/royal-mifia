#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-
import datetime
import pickle  # Per salvare la partita su file.
import math
import time
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram import ParseMode, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.error import Unauthorized, TimedOut, RetryAfter
import filemanager
import random
import strings as s
import logging
from typing import List, Union, Dict
from roles.roles import *

logging.basicConfig(level=logging.WARNING,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

token = filemanager.readfile('telegramapi.txt')
updater = Updater(token)

freenames = s.names_list.copy()


class Player:
    """Classe di un giocatore. Contiene tutti i dati riguardanti un giocatore all'interno di una partita, come il ruolo,
       e i dati riguardanti telegram, come ID e username."""
    def __init__(self, game: 'Game', tid: int, tusername: str, dummy=False):
        self.tid = tid  # ID di Telegram
        self.tusername = tusername  # Username di Telegram
        self.role = Role(self)  # Di base, ogni giocatore è un ruolo indefinito
        self.alive = True  # Il giocatore è vivo?
        self.votingfor = None  # Diventa un player se ha votato
        self.votes = 0  # Voti che sta ricevendo questo giocatore. Aggiornato da updatevotes()
        self.protectedby = None  # Protettore. Oggetto player che protegge questo giocatore dalla mifia. Se è None, la mifia può uccidere questo giocatore
        self.mifiavotes = 0  # Voti che sta ricevendo questo giocatore dalla mifia. Aggiornato da updatemifiavotes()
        self.dummy = dummy  # E' un bot? Usato solo per il debug (/debugjoin)
        self.game = game  # La partita associata al giocatore

    def __repr__(self) -> str:
        return "<Player {username}>".format(username=self.tusername)

    def __str__(self) -> str:
        return "@{}".format(self.tusername)

    def message(self, text: str):
        """Manda un messaggio privato al giocatore."""
        if not self.dummy:
            self.game.bot.sendMessage(self.tid, text, parse_mode=ParseMode.MARKDOWN)

    def kill(self):
        """Uccidi il giocatore."""
        self.role.ondeath()
        self.alive = False


class Game:
    """Classe di una partita, contenente parametri riguardanti stato della partita
       e informazioni sul gruppo di Telegram."""
    def __init__(self, bot: Bot, groupid: int):
        self.groupid = groupid  # type: int
        self.bot = bot  # type: Bot
        self.admin = None  # type: Player
        self.players = list()  # type: List['Player']
        self.tokill = list()  # type: List['Player']
        self.phase = 'Join'  # type: str
        self.day = 0  # type: int

        self.configstep = 0  # type: int
        self.roleconfig = dict()  # type: Dict[int]
        self.votingmifia = False  # type: bool

        # Liste di ruoli in gioco, per velocizzare gli endday
        self.playersinrole = dict()
        for currentrole in rolepriority:
            self.playersinrole[currentrole.__name__] = list()

        # Trova un nome per la partita
        if len(freenames) > 0:
            random.shuffle(freenames)
            self.name = freenames.pop()
        else:
            self.name = str(groupid)

        self.lastlynch = None  # Ultima persona uccisa dai Royal, diventa un player

    def __del__(self):
        # Togli le referenze circolare
        for player in self.players:
            player.role.player = None
            player.game = None
        # Rimetti il nome che si è liberato in disponibili.
        try:
            int(self.name)
        except ValueError:
            freenames.append(self.name)
        for player in self.players:
            player.game = None

    def __repr__(self):
        r = "<Game {name} in group {groupid} with {nplayers} players in phase {phase}>" \
                .format(name=self.name, groupid=self.groupid, nplayers=len(self.players), phase=self.phase)
        return r

    def message(self, text: str):
        """Manda un messaggio nel gruppo."""
        self.bot.sendMessage(self.groupid, text, parse_mode=ParseMode.MARKDOWN)

    def adminmessage(self, text: str):
        """Manda un messaggio privato al creatore della partita."""
        self.admin.message(text)

    def mifiamessage(self, text: str):
        """Manda un messaggio privato a tutti i Mifiosi nella partita."""
        # Trova tutti i mifiosi nell'elenco dei giocatori
        for player in self.players:
            if isinstance(player.role, Mifioso) or isinstance(player.role, Corrotto):
                player.message(text)

    def findplayerbyid(self, tid: int) -> Union['Player', None]:
        """Trova il giocatore con un certo id."""
        for player in self.players:
            if player.tid == tid:
                return player
        return None

    def findplayerbyusername(self, tusername: str) -> Union['Player', None]:
        """Trova il giocatore con un certo username."""
        for player in self.players:
            if player.tusername.lower() == tusername.strip("@").lower():
                return player
        return None

    def updategroupname(self):
        """Cambia il titolo della chat. Per qualche motivo non funziona."""
        try:
            if self.phase == "Voting":
                self.bot.set_chat_title(self.groupid, s.group_name.format(phase=s.day.format(day=self.day), name=self.name))
            else:
                self.bot.set_chat_title(self.groupid, s.group_name.format(phase=self.phase, name=self.name))
        except Unauthorized:
            print("Bot is not administrator in group {}".format(self.groupid))

    def assignroles(self):
        """Assegna i ruoli specificati in playersinrole a tutti i giocatori."""
        random.seed()
        playersleft = self.players.copy()
        # Assegna i ruoli secondo i numeri all'interno di playersinrole
        for currentrole in rolepriority:
            for player in random.sample(playersleft, self.roleconfig[currentrole.__name__]):
                self.playersinrole[currentrole.__name__].append(player)
                player.role = currentrole(player)
                playersleft.remove(player)
        # Assegna il ruolo di Royal a tutti gli altri
        for player in playersleft:
            player.role = Royal(self)
        # Manda i ruoli assegnati a tutti
        for player in self.players:
            player.message(s.role_assigned.format(icon=player.role.icon, name=player.role.name))
            if player.role.powerdesc is not None:
                player.message(player.role.powerdesc.format(gamename=self.name))
        # Manda ai mifiosi l'elenco dei loro compagni di squadra
        text = s.mifia_team_intro
        for player in self.playersinrole['Mifioso']:
            text += s.mifia_team_player.format(icon=player.role.icon, name=player.tusername)
        for player in self.playersinrole['Corrotto']:
            text += s.mifia_team_player.format(icon=player.role.icon, name=player.tusername)
        self.mifiamessage(text)

    def updatevotes(self):
        """Aggiorna il conteggio dei voti di tutti i giocatori."""
        for player in self.players:
            player.votes = 0
        for player in self.players:
            if player.votingfor is not None and player.alive:
                player.votingfor.votes += 1

    def updatemifiavotes(self):
        """Aggiorna il conteggio dei voti mifiosi di tutti i giocatori."""
        for player in self.players:
            player.mifiavotes = 0
        for player in self.playersinrole['Mifioso']:
            if player.alive:
                if player.role.target is not None:
                    player.role.target.mifiavotes += 1

    def mostvotedplayers(self) -> List[Player]:
        """Trova i giocatori più votati."""
        mostvoted = list()
        currenttop = 0
        self.updatevotes()
        for player in self.players:
            if player.votes > currenttop:
                mostvoted = list()
                mostvoted.append(player)
                currenttop = player.votes
            elif player.votes == currenttop:
                mostvoted.append(player)
        if currenttop > 0:
            return mostvoted
        else:
            return list()

    def mostvotedmifia(self) -> List[Player]:
        """Trova i giocatori più votati dalla mifia."""
        mostvoted = list()
        currenttop = 0
        self.updatemifiavotes()
        for player in self.players:
            if player.mifiavotes > currenttop:
                mostvoted = list()
                mostvoted.append(player)
                currenttop = player.mifiavotes
            elif player.votes == currenttop:
                    mostvoted.append(player)
        if currenttop > 0:
            return mostvoted
        else:
            return list()

    def endday(self):
        """Finisci la giornata, uccidi il più votato del giorno ed esegui gli endday di tutti i giocatori."""
        # SALVA LA PARTITA, così se crasha si riprende da qui
        self.save()
        # Conta i voti ed elimina il più votato.
        topvotes = self.mostvotedplayers()
        if len(topvotes) > 0:
            # In caso di pareggio, elimina un giocatore casuale.
            random.seed()
            random.shuffle(topvotes)
            lynched = topvotes.pop()
            if lynched.alive:
                self.message(s.player_lynched.format(name=lynched.tusername, icon=lynched.role.icon, role=lynched.role.name))
                self.lastlynch = lynched
                lynched.kill()
        elif self.day > 1:
            self.message(s.no_players_lynched)
        # Fai gli endday in un certo ordine.
        # Si potrebbe fare più velocemente, credo.
        # Ma non sto ho voglia di ottimizzare ora.
        # Endday dei mifiosi se votingmifia è attivo
        if self.votingmifia:
            # Trova il più votato dai mifiosi e uccidilo
            killlist = self.mostvotedmifia()
            if len(killlist) > 0:
                # In caso di pareggio, elimina un giocatore casuale.
                random.seed()
                random.shuffle(killlist)
                killed = killlist.pop()
                if killed.alive:
                    if killed.protectedby is None:
                        killed.kill()
                        self.message(s.mifia_target_killed.format(target=killed.tusername, icon=killed.role.icon, role=killed.role.name))
                    else:
                        self.message(s.mifia_target_protected.format(target=killed.tusername, icon=killed.protectedby.role.icon, protectedby=killed.protectedby.tusername))
        # Attiva gli \
        for currentrole in rolepriority:
            for player in self.playersinrole[currentrole.__name__]:
                if player.alive:
                    player.role.onendday()
        # Cancella tutti i voti
        for player in self.players:
            player.votingfor = None
        # Incrementa il giorno
        self.nextday()
        # Notifica del nuovo giorno
        self.message(s.new_day.format(day=self.day))
        # Controlla se qualcuno ha vinto
        self.victoryconditions()

    def startpreset(self):
        """Inizio della fase di preset"""
        self.newphase("Preset")
        # Crea la tastiera
        kbmarkup = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(s.preset_simple, callback_data="simple"),
                InlineKeyboardButton(s.preset_classic, callback_data="classic")
            ],
            [
                InlineKeyboardButton(s.preset_oneofall, callback_data="oneofall")
            ]
        ])
        # Manda la tastiera
        self.bot.sendMessage(self.groupid, s.preset_choose, parse_mode=ParseMode.MARKDOWN, reply_markup=kbmarkup)

    def loadpreset(self, preset: str):
        """Fine della fase di preset: carica il preset selezionato o passa a config"""
        if preset == "simple":
            # Preset semplice (solo Royal, Mifiosi e Investigatori)
            self.roleconfig = {
                "Mifioso":        math.floor(len(self.players) / 8) + 1,  # 1 Mifioso ogni 8 giocatori
                "Investigatore":  math.floor(len(self.players) / 12) + 1,  # 1 Detective ogni 12 giocatori
                "Corrotto":       0,
                "Angelo":         0,
                "Terrorista":     0,
                "Derek":          0,
                "Disastro":       0,
                "Mamma":          0,
                "Stagista":       0,
                "SignoreDelCaos": 0,
                "Servitore":      0
            }
            self.votingmifia = True
            self.message(s.preset_simple_selected.format(mifioso=self.roleconfig["Mifioso"],
                                                              investigatore=self.roleconfig["Investigatore"],
                                                              royal=len(self.players) - self.roleconfig["Mifioso"] - self.roleconfig["Investigatore"]))
            self.endconfig()
        elif preset == "classic":
            # Preset classico (solo Royal, Mifiosi, Investigatori, Angeli e Terroristi)
            self.roleconfig = {
                "Mifioso":        math.floor(len(self.players) / 8) + 1,  # 1 Mifioso ogni 8 giocatori
                "Investigatore":  math.floor(len(self.players) / 12) + 1,  # 1 Detective ogni 12 giocatori
                "Corrotto":       0,
                "Angelo":         math.floor(len(self.players) / 10) + 1,  # 1 Angelo ogni 10 giocatori
                "Terrorista":     1 if random.randrange(0, 100) >= 50 else 0,  # 50% di avere un terrorista
                "Derek":          0,
                "Disastro":       0,
                "Mamma":          0,
                "Stagista":       0,
                "SignoreDelCaos": 0,
                "Servitore":      0
            }
            self.votingmifia = True
            self.message(s.preset_classic_selected.format(mifioso=self.roleconfig["Mifioso"], investigatore=self.roleconfig["Investigatore"], angelo=self.roleconfig["Angelo"], royal=len(self.players) - self.roleconfig["Mifioso"] - self.roleconfig["Investigatore"] - self.roleconfig["Angelo"], royalmenouno=len(self.players) - self.roleconfig["Mifioso"] - self.roleconfig["Investigatore"] - self.roleconfig["Angelo"] - 1))
            self.endconfig()
        elif preset == "oneofall":
            self.roleconfig = {
                "Mifioso": 1,
                "Investigatore": 1,
                "Corrotto": 1,
                "Angelo": 1,
                "Terrorista": 1,
                "Derek": 1,
                "Disastro": 1,
                "Mamma": 1,
                "Stagista": 1,
                "SignoreDelCaos": 0,
                "Servitore": 0
            }
            unassignedplayers = len(self.players) - 9
            availableroles = list() 
            while unassignedplayers > 0:
                if len(availableroles) == 0:
                    availableroles = rolepriority.copy()
                    availableroles.remove(SignoreDelCaos)
                    availableroles.remove(Servitore)
                    random.shuffle(availableroles)
                self.roleconfig[availableroles.pop().__name__] += 1
                unassignedplayers -= 1
            self.votingmifia = False
            self.message(s.preset_oneofall_selected)
            self.endconfig()


    def endconfig(self):
        """Fine della fase di config, inizio assegnazione ruoli"""
        # Controlla che ci siano abbastanza giocatori per avviare la partita
        requiredplayers = 0
        for selectedrole in self.roleconfig:
            requiredplayers += self.roleconfig[selectedrole]
        # Se non ce ne sono abbastanza, torna alla fase di join
        if requiredplayers > len(self.players):
            self.message(s.error_not_enough_players)
            self.newphase("Join")
        else:
            self.newphase("Voting", silent=True)
            self.nextday()
            self.players.sort(key=lambda p: p.tusername)
            self.assignroles()
            self.message(s.roles_assigned_successfully)
            for player in self.players:
                player.role.onstartgame()

    def revealallroles(self):
        text = s.status_header.format(name=self.name, admin=self.admin.tusername, phase=self.phase)
        self.updatevotes()
        # Aggiungi l'elenco dei giocatori
        for player in self.players:
            text += s.status_basic_player.format(icon=player.role.icon,
                                                 name=player.tusername)
        self.message(text)

    def endgame(self):
        self.newphase("End")
        self.revealallroles()
        inprogress.remove(self)

    def save(self):
        # Crea il file.
        try:
            file = open(str(self.groupid) + ".p", 'x')
        except FileExistsError:
            pass
        else:
            file.close()
        # Scrivi sul file.
        file = open(str(self.groupid) + ".p", 'wb')
        pickle.dump(self, file)
        file.close()
        # Crea un file uguale ma con un timestamp
        # Non sono troppo sicuro che il timestamp si faccia così però funziona
        t = datetime.datetime(2000,1,1,1,1).now()
        try:
            file = open("{group}-{yy}-{mm}-{dd}-{hh}-{mi}.p".format(group=str(self.groupid), yy=t.year, mm=t.month, dd=t.day, hh=t.hour, mi=t.minute), 'x')
        except FileExistsError:
            pass
        else:
            file.close()
        # Scrivi sul file.
        file = open("{group}-{yy}-{mm}-{dd}-{hh}-{mi}.p".format(group=str(self.groupid), yy=t.year, mm=t.month, dd=t.day, hh=t.hour, mi=t.minute), 'wb')
        pickle.dump(self, file)
        self.adminmessage(s.game_saved.format(name=self.name))
        file.close()

    def victoryconditions(self):
        """Controlla se qualcuno ha completato le condizioni di vittoria."""
        good = 0
        evil = 0
        alive = 0
        for player in self.players:
            if player.alive:
                if player.role.team == 'Evil':
                    evil += 1
                elif player.role.team == 'Good':
                    good += 1
                alive += 1
        # Distruzione atomica!
        if alive == 0:
            self.message(s.end_game_wiped)
            for player in self.players:
                player.message(s.end_game_wiped + s.tie)
            self.endgame()
        # I mifiosi vincono se sono più dei royal
        elif evil >= good:
            self.message(s.end_mifia_outnumber + s.victory_mifia)
            for player in self.players:
                if player.role.team == 'Good':
                    player.message(s.end_mifia_outnumber + s.defeat)
                elif player.role.team == 'Evil':
                    player.message(s.end_mifia_outnumber + s.victory)
                elif player.role.team == 'Chaos':
                    player.message(s.end_game_chaos + s.victory)
            self.endgame()
        # Male distrutto
        elif evil == 0:
            self.message(s.end_mifia_killed + s.victory_royal)
            for player in self.players:
                if player.role.team == 'Good':
                    player.message(s.end_mifia_killed + s.victory)
                elif player.role.team == 'Evil':
                    player.message(s.end_mifia_killed + s.defeat)
                elif player.role.team == 'Chaos':
                    player.message(s.end_game_chaos + s.victory)
            self.endgame()

    def changerole(self, player: Player, newrole):
        """Cambia il ruolo di un giocatore, aggiornando tutti i valori"""
        # Aggiorna le liste dei ruoli
        if player.role.__class__ != Royal:
            self.playersinrole[player.role.__class__.__name__].remove(player)
        if newrole != Royal:
            self.playersinrole[newrole.__name__].append(player)
        # Cambia il ruolo al giocatore
        player.role = newrole(player)
        # Manda i messaggi del nuovo ruolo
        player.message(s.role_assigned.format(icon=player.role.icon, name=player.role.name))
        if player.role.powerdesc is not None:
            player.message(player.role.powerdesc.format(gamename=self.name))
        # Manda ai mifiosi l'elenco dei loro compagni di squadra
        text = s.mifia_team_intro
        for player in self.playersinrole['Mifioso']:
            text += s.mifia_team_player.format(icon=player.role.icon, name=player.tusername)
        for player in self.playersinrole['Corrotto']:
            text += s.mifia_team_player.format(icon=player.role.icon, name=player.tusername)
        self.mifiamessage(text)

    def joinplayer(self, player: Player, silent=False):
        self.players.append(player)
        if not silent:
            self.message(s.player_joined.format(name=player.tusername, players=len(self.players)))
        # Se è il primo giocatore ad unirsi, diventa admin
        if len(self.players) == 1:
            self.admin = player

    def getrandomrole(self):
        availableroles = list()
        for existingrole in self.playersinrole:
            if len(existingrole) > 0:
                availableroles.append(existingrole)
        return globals()[random.sample(availableroles, 1)[0]]  # EWWW

    def newphase(self, phase: str, silent: bool=False):
        self.phase = phase
        if not silent:
            self.updategroupname()

    def nextday(self, silent: bool=False):
        self.day += 1
        if not silent:
            self.updategroupname()


# Partite in corso
inprogress = list()


def findgamebyid(gid: int) -> Game:
    """Trova una partita con un certo id."""
    for game in inprogress:
        if game.groupid == gid:
            return game


def findgamebyname(name: str) -> Game:
    """Trova una partita con un certo nome."""
    for game in inprogress:
        if game.name.lower() == name.lower():
            return game


# Comandi a cui risponde il bot
def ping(bot: Bot, update):
    """Ping!"""
    bot.sendMessage(update.message.chat.id, s.pong, parse_mode=ParseMode.MARKDOWN)


def newgame(bot: Bot, update):
    """Crea una nuova partita."""
    if update.message.chat.type != 'supergroup':
        bot.sendMessage(update.message.chat.id, s.error_chat_type, parse_mode=ParseMode.MARKDOWN)
        return
    game = findgamebyid(update.message.chat.id)
    if game is not None:
        bot.sendMessage(update.message.chat.id, s.error_game_in_progress, parse_mode=ParseMode.MARKDOWN)
        return
    game = Game(bot, update.message.chat.id)
    inprogress.append(game)
    game.message(s.new_game.format(name=game.name))
    join(bot, update)


def join(bot: Bot, update):
    """Unisciti a una partita."""
    game = findgamebyid(update.message.chat.id)
    # Nessuna partita in corso
    if game is None:
        bot.sendMessage(update.message.chat.id, s.error_no_games_found, parse_mode=ParseMode.MARKDOWN)
        return
    # Fase di join finita
    if game.phase != 'Join':
        game.message(s.error_join_phase_ended)
        return
    p = game.findplayerbyid(update.message.from_user['id'])
    # Giocatore già in partita
    if p is not None:
        game.message(s.error_player_already_joined)
        return
    # Giocatore senza username
    if update.message.from_user.username is None:
        game.message(s.error_no_username)
        return
    p = Player(game, update.message.from_user.id, update.message.from_user.username)
    try:
        p.message(s.you_joined.format(game=game.name, adminname=game.admin.tusername if game.admin is not None else p.tusername))
    except Unauthorized:
        # Bot bloccato dall'utente
        game.message(s.error_chat_unavailable)
        return
    # Aggiungi il giocatore alla partita
    game.joinplayer(p)
    # Salva
    game.save()


def debugjoin(bot: Bot, update):
    """Aggiungi dei bot alla partita."""
    if __debug__:
        game = findgamebyid(update.message.chat.id)
        if game is None:
            bot.sendMessage(update.message.chat.id, s.error_no_games_found, parse_mode=ParseMode.MARKDOWN)
            return
        if game.phase != 'Join':
            game.message(s.error_join_phase_ended)
            return
        arg = update.message.text.split(" ")
        for name in range(1, int(arg[1]) + 1):
            p = Player(game, int(name), str(name), True)
            try:
                game.joinplayer(p, silent=True)
            except RetryAfter:
                pass


def status(bot: Bot, update):
    """Visualizza lo stato della partita."""
    game = findgamebyid(update.message.chat.id)
    if game is not None:
        text = str()
        if __debug__:
            text += s.debug_mode
        text += s.status_header.format(name=game.name, admin=game.admin.tusername if game.admin is not None else "-", phase=game.phase)
        game.updatevotes()
        # Aggiungi l'elenco dei giocatori
        for player in game.players:
            if not player.alive:
                text += s.status_dead_player.format(name=player.tusername)
            elif game.day > 1:
                text += s.status_alive_player.format(icon="\U0001F610",
                                                     name=player.tusername,
                                                     votes=str(player.votes))
            else:
                text += s.status_basic_player.format(icon="\U0001F610",
                                                     name=player.tusername)
        game.message(text)
    else:
        bot.sendMessage(update.message.chat.id, s.error_no_games_found, parse_mode=ParseMode.MARKDOWN)


def endjoin(bot: Bot, update):
    """Termina la fase di join e inizia quella di votazione."""
    game = findgamebyid(update.message.chat.id)
    if game is not None and game.phase == 'Join':
        if update.message.from_user.id == game.admin.tid:
            game.message(s.join_phase_ended)
            game.startpreset()
        else:
            game.message(s.error_not_admin)
    else:
        bot.sendMessage(update.message.chat.id, s.error_no_games_found, parse_mode=ParseMode.MARKDOWN)


def vote(bot: Bot, update):
    """Vota per uccidere una persona."""
    # Trova la partita
    game = findgamebyid(update.message.chat.id)
    if game is None:
        bot.sendMessage(update.message.chat.id, s.error_no_games_found, parse_mode=ParseMode.MARKDOWN)
        return
    elif game.phase is not 'Voting':
        bot.sendMessage(update.message.chat.id, s.error_no_games_found, parse_mode=ParseMode.MARKDOWN)
        return
    elif game.day <= 1:
        game.message(s.error_no_votes_on_first_day)
        return
    # Genera la tastiera
    table = list()
    for player in game.players:
        if not player.alive:
            continue
        row = list()
        row.append(InlineKeyboardButton(s.vote_keyboard_line.format(player=player, votes=player.votes), callback_data=player.tusername))
        table.append(row)
    row = list()
    row.append(InlineKeyboardButton(s.vote_keyboard_nobody, callback_data="-"))
    table.append(row)
    keyboard = InlineKeyboardMarkup(table)
    # Manda la tastiera
    bot.sendMessage(game.groupid, s.vote_keyboard, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard)


def endday(_: Bot, update):
    """Termina la giornata attuale."""
    game = findgamebyid(update.message.chat.id)
    if game is not None and game.phase is 'Voting' and update.message.from_user.id == game.admin.tid:
        game.endday()


def power(bot: Bot, update):
    """Attiva il potere del tuo ruolo."""
    if update.message.chat.type == 'private':
        cmd = update.message.text.split(' ', 2)
        game = findgamebyname(cmd[1])
        # Se non lo trovi con il nome, prova con l'id
        if game is None:
            try:
                game = findgamebyid(int(cmd[1]))
            except ValueError:
                pass
        if game is not None:
            player = game.findplayerbyid(int(update.message.from_user.id))
            if player is not None:
                if player.alive:
                    if len(cmd) > 2:
                        player.role.power(cmd[2])
                    else:
                        player.message(s.error_missing_parameters)
                else:
                    player.message(s.error_dead)
            else:
                bot.sendMessage(update.message.chat.id, s.error_not_in_game, parse_mode=ParseMode.MARKDOWN)
        else:
            bot.sendMessage(update.message.chat.id, s.error_no_games_found, parse_mode=ParseMode.MARKDOWN)
    else:
        bot.sendMessage(update.message.chat.id, s.error_private_required, parse_mode=ParseMode.MARKDOWN)


def role(bot: Bot, update):
    """Visualizza il tuo ruolo."""
    game = findgamebyid(update.message.chat.id)
    if game is not None and game.phase is 'Voting':
        player = game.findplayerbyid(update.message.from_user.id)
        if player is not None:
            if player.alive:
                player.message(s.role_assigned.format(icon=player.role.icon, name=player.role.name))
                game.message(s.check_private)
            else:
                game.message(s.error_dead)
        else:
            bot.sendMessage(update.message.chat.id, s.error_not_in_game, parse_mode=ParseMode.MARKDOWN)
    else:
        bot.sendMessage(update.message.chat.id, s.error_no_games_found, parse_mode=ParseMode.MARKDOWN)


def kill(bot: Bot, update):
    """Uccidi un giocatore in partita."""
    if __debug__:
        game = findgamebyid(update.message.chat.id)
        if game is not None and game.phase is 'Voting':
            if update.message.from_user.id == game.admin.tid:
                target = game.findplayerbyusername(update.message.text.split(' ')[1])
                if target is not None:
                    target.kill()
                    game.message(s.admin_killed.format(name=target.tusername,
                                                            icon=target.role.icon,
                                                            role=target.role.name))
                else:
                    game.message(s.error_username)
            else:
                game.message(s.error_not_admin)
        else:
            bot.sendMessage(update.message.chat.id, s.error_no_games_found, parse_mode=ParseMode.MARKDOWN)


def delete(bot: Bot, update):
    """Elimina una partita in corso."""
    if update.message.chat.type == 'private':
        if update.message.from_user.username == "Steffo":
            cmd = update.message.text.split(' ', 2)
            game = findgamebyname(cmd[1])
            # Se non lo trovi con il nome, prova con l'id
            if game is None:
                game = findgamebyid(int(cmd[1]))
            if game is not None:
                game.message(s.owner_ended)
                game.endgame()
            else:
                game.message(s.error_no_games_found)
        else:
            bot.sendMessage(update.message.chat.id, s.error_not_owner, parse_mode=ParseMode.MARKDOWN)
    else:
        bot.sendMessage(update.message.chat.id, s.error_chat_type, parse_mode=ParseMode.MARKDOWN)


def load(bot: Bot, update):
    """Carica una partita salvata."""
    file = open(str(update.message.chat.id) + ".p", "rb")
    game = pickle.load(file)
    inprogress.append(game)
    game.message(bot, s.game_loaded)


def save(bot: Bot, update):
    """Salva una partita su file."""
    game = findgamebyid(update.message.chat.id)
    if game is not None:
        game.save()
    else:
        bot.sendMessage(update.message.chat.id, s.error_no_games_found, parse_mode=ParseMode.MARKDOWN)


def debug(bot: Bot, update):
    """Visualizza tutti i ruoli e gli id."""
    if __debug__:
        game = findgamebyid(update.message.chat.id)
        if game is not None:
            game.revealallroles()
        else:
            bot.sendMessage(update.message.chat.id, s.error_no_games_found, parse_mode=ParseMode.MARKDOWN)


def debugchangerole(bot: Bot, update):
    """Cambia il ruolo a un giocatore."""
    if __debug__:
        game = findgamebyid(update.message.chat.id)
        if game is not None:
            cmd = update.message.text.split(' ', 2)
            game.changerole(game.findplayerbyusername(cmd[1]), globals()[cmd[2]])
        else:
            bot.sendMessage(update.message.chat.id, s.error_no_games_found, parse_mode=ParseMode.MARKDOWN)


def debuggameslist(bot: Bot, update):
    """Visualizza l'elenco delle partite in corso."""
    if __debug__:
        bot.sendMessage(update.message.from_user.id, repr(inprogress), parse_mode=ParseMode.MARKDOWN)


def inlinekeyboard(bot: Bot, update):
    """Seleziona un preset dalla tastiera."""
    game = findgamebyid(update.callback_query.message.chat.id)
    if game is None:
        bot.answerCallbackQuery(callback_query_id=update.callback_query.id, text=s.error_no_games_found, show_alert=True)
        return
    if game.phase is 'Preset':
        if update.callback_query.from_user.id != game.admin.tid:
            bot.answerCallbackQuery(callback_query_id=update.callback_query.id, text=s.error_not_admin, show_alert=True)
            return
        game.loadpreset(update.callback_query.data)
        bot.answerCallbackQuery(callback_query_id=update.callback_query.id, text=s.preset_selected.format(selected=update.callback_query.data))
    elif game.phase is 'Voting':
        # Trova il giocatore
        player = game.findplayerbyid(update.callback_query.from_user.id)
        if player is None:
            bot.answerCallbackQuery(callback_query_id=update.callback_query.id, text=s.error_not_in_game, show_alert=True)
            return
        if not player.alive:
            bot.answerCallbackQuery(callback_query_id=update.callback_query.id, text=s.error_dead, show_alert=True)
            return
        if update.callback_query.data == "-":
            # Annulla il voto
            player.votingfor = None
            game.message(s.vote_none.format(player=player))
            bot.answerCallbackQuery(callback_query_id=update.callback_query.id, text=s.vote_none_fp)
        else:
            # Cambia il voto
            target = game.findplayerbyusername(update.callback_query.data)
            player.votingfor = target
            game.message(s.vote.format(voting=player.tusername, voted=target.tusername))
            bot.answerCallbackQuery(callback_query_id=update.callback_query.id, text=s.vote_fp.format(voted=target.tusername))


updater.dispatcher.add_handler(CommandHandler('ping', ping))
updater.dispatcher.add_handler(CommandHandler('newgame', newgame))
updater.dispatcher.add_handler(CommandHandler('join', join))
updater.dispatcher.add_handler(CommandHandler('debugjoin', debugjoin))
updater.dispatcher.add_handler(CommandHandler('endjoin', endjoin))
updater.dispatcher.add_handler(CommandHandler('vote', vote))
updater.dispatcher.add_handler(CommandHandler('endday', endday))
updater.dispatcher.add_handler(CommandHandler('power', power))
updater.dispatcher.add_handler(CommandHandler('status', status))
updater.dispatcher.add_handler(CommandHandler('role', role))
updater.dispatcher.add_handler(CommandHandler('debug', debug))
updater.dispatcher.add_handler(CommandHandler('debuggameslist', debuggameslist))
updater.dispatcher.add_handler(CommandHandler('kill', kill))
updater.dispatcher.add_handler(CommandHandler('save', save))
updater.dispatcher.add_handler(CommandHandler('load', load))
updater.dispatcher.add_handler(CommandHandler('delete', delete))
updater.dispatcher.add_handler(CommandHandler('debugchangerole', debugchangerole))
updater.dispatcher.add_handler(CallbackQueryHandler(inlinekeyboard))

if __name__ == "__main__":
    updater.start_polling()
    while True:
        try:
            updater.idle()
        except TimedOut:
            time.sleep(10)
