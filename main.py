#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-
import datetime
import pickle  # Per salvare la partita su file.
import math
import time
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram import ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import Unauthorized, TimedOut
import filemanager
import random
import strings as s
import logging
from roles.data import *

logging.basicConfig(level=logging.WARNING,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

token = filemanager.readfile('telegramapi.txt')
updater = Updater(token)

freenames = s.names_list.copy()


class Player:
    """Classe di un giocatore. Contiene tutti i dati riguardanti un giocatore all'interno di una partita, come il ruolo,
       e i dati riguardanti telegram, come ID e username."""
    def __init__(self, tid, tusername, dummy=False):
        self.tid = tid  # ID di Telegram
        self.tusername = tusername  # Username di Telegram
        self.role = Role(self)  # Di base, ogni giocatore è un ruolo indefinito
        self.alive = True  # Il giocatore è vivo?
        self.votingfor = None  # Diventa un player se ha votato
        self.votes = 0  # Voti che sta ricevendo questo giocatore. Aggiornato da updatevotes()
        self.protectedby = None  # Protettore. Oggetto player che protegge questo giocatore dalla mifia. Se è None, la mifia può uccidere questo giocatore
        self.mifiavotes = 0  # Voti che sta ricevendo questo giocatore dalla mifia. Aggiornato da updatemifiavotes()
        self.dummy = dummy  # E' un bot? Usato solo per il debug (/debugjoin)

    def __repr__(self) -> str:
        return "<Player {username}>".format(username=self.tusername)

    def __str__(self) -> str:
        return "@{}".format(self.tusername)

    def message(self, bot, text):
        """Manda un messaggio privato al giocatore."""
        if not self.dummy:
            try:
                bot.sendMessage(self.tid, text, parse_mode=ParseMode.MARKDOWN)
            except Unauthorized:
                print("Unauthorized to message {}".format(self))


    def kill(self, bot, game):
        """Uccidi il giocatore."""
        self.role.ondeath(bot, game)
        self.alive = False


class Game:
    """Classe di una partita, contenente parametri riguardanti stato della partita
       e informazioni sul gruppo di Telegram."""
    def __init__(self, groupid):
        self.groupid = groupid  # ID del gruppo in cui si sta svolgendo una partita
        self.admin = None  # ID telegram dell'utente che ha creato la partita con /newgame
        self.players = list()  # Lista dei giocatori in partita
        self.tokill = list()  # Giocatori che verranno uccisi all'endday
        self.phase = 'Join'  # Fase di gioco: 'Join', 'Preset', 'Config', 'Voting'
        self.day = 0  # Numero del giorno. 0 se la partita deve ancora iniziare

        self.configstep = 0  # Passo attuale di configurazione
        self.roleconfig = dict()  # Dizionario con le quantità di ruoli da aggiungere
        self.votingmifia = False  # Seguire le regole originali della mifia che vota?
        self.missingmifia = False  # La mifia può fallire un'uccisione
        self.misschance = 5  # Percentuale di fallimento di un'uccisione

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
        # Rimetti il nome che si è liberato in disponibili.
        try:
            int(self.name)
        except ValueError:
            freenames.append(self.name)

    def __repr__(self):
        r = "<Game {name} in group {groupid} with {nplayers} players in phase {phase}>" \
                .format(name=self.name, groupid=self.groupid, nplayers=len(self.players), phase=self.phase)
        return r

    def message(self, bot, text):
        """Manda un messaggio nel gruppo."""
        bot.sendMessage(self.groupid, text, parse_mode=ParseMode.MARKDOWN)

    def adminmessage(self, bot, text):
        """Manda un messaggio privato al creatore della partita."""
        self.admin.message(bot, text)

    def mifiamessage(self, bot, text):
        """Manda un messaggio privato a tutti i Mifiosi nella partita."""
        # Trova tutti i mifiosi nell'elenco dei giocatori
        for player in self.players:
            if isinstance(player.role, Mifioso):
                player.message(bot, text)

    def findplayerbyid(self, tid):
        """Trova il giocatore con un certo id."""
        for player in self.players:
            if player.tid == tid:
                return player
        else:
            return None

    def findplayerbyusername(self, tusername):
        """Trova il giocatore con un certo username."""
        for player in self.players:
            if player.tusername.lower() == tusername.strip("@").lower():
                return player
        else:
            return None

    def assignroles(self, bot):
        """Assegna ruoli casuali a tutti i giocatori."""
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
            player.message(bot, s.role_assigned.format(icon=player.role.icon, name=player.role.name))
            if player.role.powerdesc is not None:
                player.message(bot, player.role.powerdesc.format(gamename=self.name))
        # Manda ai mifiosi l'elenco dei loro compagni di squadra
        text = s.mifia_team_intro
        for player in self.playersinrole['Mifioso']:
            text += s.mifia_team_player.format(icon=player.role.icon, name=player.tusername)
        for player in self.playersinrole['Corrotto']:
            text += s.mifia_team_player.format(icon=player.role.icon, name=player.tusername)
        for player in self.playersinrole['Mifioso']:
            player.message(bot, text)
        for player in self.playersinrole['Corrotto']:
            player.message(bot, text)

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

    def mostvotedplayer(self) -> list:
        """Trova il giocatore più votato."""
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

    def mostvotedmifia(self) -> list:
        """Trova il giocatore più votato dalla mifia."""
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

    def endday(self, bot):
        """Finisci la giornata, uccidi il più votato del giorno ed esegui gli endday di tutti i giocatori."""
        # SALVA LA PARTITA, così se crasha si riprende da qui
        self.save(bot)
        # Conta i voti ed elimina il più votato.
        topvotes = self.mostvotedplayer()
        if len(topvotes) > 0:
            # In caso di pareggio, elimina un giocatore casuale.
            random.seed()
            random.shuffle(topvotes)
            lynched = topvotes.pop()
            if lynched.alive:
                self.message(bot, s.player_lynched.format(name=lynched.tusername,
                                                          icon=lynched.role.icon,
                                                          role=lynched.role.name))
                self.lastlynch = lynched
                lynched.kill(bot, self)
        elif self.day > 1:
            self.message(bot, s.no_players_lynched)
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
                        if self.missingmifia and random.randrange(0, 100) < self.misschance:
                            # Colpo mancato
                            self.message(bot, s.mifia_target_missed.format(target=killed.tusername))
                        else:
                            # Uccisione riuscita
                            killed.kill(bot, self)
                            self.message(bot, s.mifia_target_killed.format(target=killed.tusername,
                                                                           icon=killed.role.icon,
                                                                           role=killed.role.name))
                    else:
                        self.message(bot, s.mifia_target_protected.format(target=killed.tusername,
                                                                          icon=killed.protectedby.role.icon,
                                                                          protectedby=killed.protectedby.tusername))
        # Attiva gli onendday
        for currentrole in rolepriority:
            for player in self.playersinrole[currentrole.__name__]:
                if player.alive:
                    player.role.onendday(bot, self)
        # Cancella tutti i voti
        for player in self.players:
            player.votingfor = None
        # Controlla se qualcuno ha vinto
        self.victoryconditions(bot)
        # Incrementa il giorno
        self.day += 1
        # Notifica dell'inizi
        self.message(bot, s.new_day.format(day=self.day))

    def startpreset(self, bot):
        """Inizio della fase di preset"""
        self.phase = 'Preset'
        # Crea la tastiera
        kbmarkup = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(s.preset_simple, callback_data="simple"),
                InlineKeyboardButton(s.preset_classic, callback_data="classic"),
                InlineKeyboardButton(s.preset_advanced, callback_data="advanced")
            ],
            [
                InlineKeyboardButton(s.preset_custom, callback_data="custom")
            ]
        ])
        # Manda la tastiera
        bot.sendMessage(self.groupid, s.preset_choose, parse_mode=ParseMode.MARKDOWN, reply_markup=kbmarkup)

    def loadpreset(self, bot, preset):
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
            self.missingmifia = False
            self.message(bot, s.preset_simple_selected.format(mifioso=self.roleconfig["Mifioso"],
                                                              investigatore=self.roleconfig["Investigatore"],
                                                              royal=len(self.players) - self.roleconfig["Mifioso"] - self.roleconfig["Investigatore"]))
            self.endconfig(bot)
        elif preset == "classic":
            # Preset classico (solo Royal, Mifiosi, Investigatori, Angeli e Terroristi)
            self.roleconfig = {
                "Mifioso":        math.floor(len(self.players) / 8) + 1,  # 1 Mifioso ogni 8 giocatori
                "Investigatore":  math.floor(len(self.players) / 12) + 1,  # 1 Detective ogni 12 giocatori
                "Corrotto":       0,
                "Angelo":         math.floor(len(self.players) / 10) + 1,  # 1 Angelo ogni 10 giocatori
                "Terrorista":     1 if random.randrange(0, 100) > 70 else 0,  # 30% di avere un terrorista
                "Derek":          0,
                "Disastro":       0,
                "Mamma":          0,
                "Stagista":       0,
                "SignoreDelCaos": 0,
                "Servitore":      0
            }
            self.votingmifia = True
            self.missingmifia = False
            self.message(bot, s.preset_classic_selected)
            self.endconfig(bot)
        elif preset == "advanced":
            # Preset avanzato: genera i ruoli in modo da rendere la partita divertente
            self.roleconfig = {
                "Mifioso": 0,
                "Investigatore": 0,
                "Corrotto": 0,
                "Angelo": 0,
                "Terrorista": 0,
                "Derek": 0,
                "Disastro": 0,
                "Mamma": 0,
                "Stagista": 0,
                "SignoreDelCaos": 0,
                "Servitore": 0
            }
            unassignedplayers = len(self.players)
            balance = 0
            # Scegli casualmente il numero di mifiosi: più ce ne sono più ruoli ci saranno in partita!
            self.roleconfig["Mifioso"] = random.randint(1, math.ceil(unassignedplayers / 7))
            unassignedplayers -= self.roleconfig["Mifioso"]
            balance += Mifioso.value
            # Trova tutti i ruoli positivi
            positiveroles = list()
            for role in rolepriority:
                if role.team == "Good":
                    positiveroles.append(role)
            # Trova tutti i ruoli negativi
            negativeroles = list()
            for role in rolepriority:
                if role.team == "Evil":
                    positiveroles.append(role)
            # Aggiungi ruoli positivi casuali finchè la partita non viene bilanciata
            while balance < 0 and unassignedplayers > 0:
                role = random.sample(positiveroles, 1)[0]
                self.roleconfig[role.__name__] += 1
                balance += role.value
                unassignedplayers -= 1
            # Se la partita è leggermente sfavorita verso i Royal, aggiungi qualche ruolo negativo
            while balance > 0 and unassignedplayers > 0:
                role = random.sample(negativeroles, 1)[0]
                self.roleconfig[role.__name__] += 1
                balance += role.value
                unassignedplayers -= 1
            # Non ci sono SignoreDelCaos e Servitore per motivi ovvi
            self.roleconfig["SignoreDelCaos"] = 0
            self.roleconfig["Servitore"] = 0
            # Altri parametri
            self.votingmifia = False
            self.missingmifia = False
            self.message(bot, s.preset_advanced_selected)
            self.endconfig(bot)
        elif preset == "custom":
            # Preset personalizzabile
            self.startconfig(bot)

    def startconfig(self, bot):
        """Inizio della fase di config"""
        self.phase = 'Config'
        self.configstep = 0
        self.message(bot, s.config_list[0])

    def endconfig(self, bot):
        """Fine della fase di config, inizio assegnazione ruoli"""
        # Controlla che ci siano abbastanza giocatori per avviare la partita
        requiredplayers = 0
        for selectedrole in self.roleconfig:
            requiredplayers += self.roleconfig[selectedrole]
        # Se non ce ne sono abbastanza, torna alla fase di join
        if requiredplayers > len(self.players):
            self.message(bot, s.error_not_enough_players)
        else:
            self.phase = 'Voting'
            self.day += 1
            self.assignroles(bot)
            self.message(bot, s.roles_assigned_successfully)
            for player in self.players:
                player.role.onstartgame(bot, self)

    def revealallroles(self, bot):
        text = s.status_header.format(name=self.groupid, admin=self.admin.tid, phase=self.phase)
        self.updatevotes()
        # Aggiungi l'elenco dei giocatori
        for player in self.players:
            text += s.status_basic_player.format(icon=player.role.icon,
                                                 name=player.tusername)
        self.message(bot, text)

    def endgame(self):
        for player in self.players:
            # Togli la referenza circolare
            player.role.player = None
        inprogress.remove(self)

    def save(self, bot):
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
        self.message(bot, s.game_saved)
        file.close()

    def victoryconditions(self, bot):
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
            self.message(bot, s.end_game_wiped)
            for player in self.players:
                player.message(bot, s.end_game_wiped + s.tie)
            self.revealallroles(bot)
            self.endgame()
        # I mifiosi sono più del 50% dei vivi se la mifia è infallibile
        # o non ci sono più personaggi buoni se la mifia può mancare i colpi
        elif (not self.missingmifia and evil >= (alive-evil)) or good == 0:
            self.message(bot, s.end_mifia_outnumber + s.victory_mifia)
            for player in self.players:
                if player.role.team == 'Good':
                    player.message(bot, s.end_mifia_outnumber + s.defeat)
                elif player.role.team == 'Evil':
                    player.message(bot, s.end_mifia_outnumber + s.victory)
                elif player.role.team == 'Chaos':
                    player.message(bot, s.end_game_chaos + s.victory)
            self.revealallroles(bot)
            self.endgame()
        # Male distrutto
        elif evil == 0:
            self.message(bot, s.end_mifia_killed + s.victory_royal)
            for player in self.players:
                if player.role.team == 'Good':
                    player.message(bot, s.end_mifia_killed + s.victory)
                elif player.role.team == 'Evil':
                    player.message(bot, s.end_mifia_killed + s.defeat)
                elif player.role.team == 'Chaos':
                    player.message(bot, s.end_game_chaos + s.victory)
            self.revealallroles(bot)
            self.endgame()

    def changerole(self, bot, player, newrole):
        """Cambia il ruolo di un giocatore, aggiornando tutti i valori"""
        # Aggiorna le liste dei ruoli
        if player.role.__class__ != Royal:
            self.playersinrole[player.role.__class__.__name__].remove(player)
        if newrole != Royal:
            self.playersinrole[newrole.__name__].append(player)
        # Cambia il ruolo al giocatore
        player.role = newrole(player)
        # Manda i messaggi del nuovo ruolo
        player.message(bot, s.role_assigned.format(icon=player.role.icon, name=player.role.name))
        if player.role.powerdesc is not None:
            player.message(bot, player.role.powerdesc.format(gamename=self.name))
        # Aggiorna lo stato dei mifiosi
        if newrole == Mifioso:
            text = s.mifia_team_intro
            for player in self.playersinrole['Mifioso']:
                text += s.mifia_team_player.format(icon=player.role.icon, name=player.tusername)
            for player in self.playersinrole['Mifioso']:
                player.message(bot, text)

    def joinplayer(self, bot, player):
        self.players.append(player)
        self.message(bot, s.player_joined.format(name=player.tusername))
        # Se è il primo giocatore ad unirsi, diventa admin
        if len(self.players) == 1:
            self.admin = player

    def getrandomrole(self):
        availableroles = list()
        for role in self.playersinrole:
            if len(role) > 0:
                availableroles.append(role)
        return locals()[random.sample(availableroles, 1)[0]]



# Partite in corso
inprogress = list()


def findgamebyid(gid) -> Game:
    """Trova una partita con un certo id."""
    for game in inprogress:
        if game.groupid == gid:
            return game


def findgamebyname(name) -> Game:
    """Trova una partita con un certo nome."""
    for game in inprogress:
        if game.name.lower() == name.lower():
            return game


# Comandi a cui risponde il bot
def ping(bot, update):
    """Ping!"""
    bot.sendMessage(update.message.chat.id, s.pong, parse_mode=ParseMode.MARKDOWN)


def newgame(bot, update):
    """Crea una nuova partita."""
    if update.message.chat.type != 'private':
        game = findgamebyid(update.message.chat.id)
        if game is None:
            game = Game(update.message.chat.id)
            inprogress.append(game)
            game.message(bot, s.new_game.format(groupid=game.groupid, name=game.name))
            join(bot, update)
        else:
            bot.sendMessage(update.message.chat.id, s.error_game_in_progress, parse_mode=ParseMode.MARKDOWN)
    else:
        bot.sendMessage(update.message.chat.id, s.error_chat_type, parse_mode=ParseMode.MARKDOWN)


def join(bot, update):
    """Unisciti a una partita."""
    game = findgamebyid(update.message.chat.id)
    # Nessuna partita in corso
    if game is None:
        bot.sendMessage(update.message.chat.id, s.error_no_games_found, parse_mode=ParseMode.MARKDOWN)
        return
    # Fase di join finita
    if game.phase != 'Join':
        game.message(bot, s.error_join_phase_ended)
        return
    p = game.findplayerbyid(update.message.from_user['id'])
    # Giocatore già in partita
    if p is not None:
        game.message(bot, s.error_player_already_joined)
        return
    # Giocatore senza username
    if update.message.from_user.username is None:
        game.message(bot, s.error_no_username)
        return
    p = Player(update.message.from_user.id, update.message.from_user.username)
    try:
        p.message(bot, s.you_joined.format(game=game.name))
    except Unauthorized:
        # Bot bloccato dall'utente
        game.message(bot, s.error_chat_unavailable)
        return
    # Aggiungi il giocatore alla partita
    game.joinplayer(bot, p)
    # Salva
    game.save(bot)


def debugjoin(bot, update):
    """Aggiungi un bot alla partita."""
    if __debug__:
        game = findgamebyid(update.message.chat.id)
        if game is None:
            bot.sendMessage(update.message.chat.id, s.error_no_games_found, parse_mode=ParseMode.MARKDOWN)
            return
        if game.phase != 'Join':
            game.message(bot, s.error_join_phase_ended)
            return
        arg = update.message.text.split(" ")
        p = Player(random.randrange(0, 10000), arg[1], True)  # ewwwwww
        game.joinplayer(bot, p)


def status(bot, update):
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
        game.message(bot, text)
    else:
        bot.sendMessage(update.message.chat.id, s.error_no_games_found, parse_mode=ParseMode.MARKDOWN)


def endjoin(bot, update):
    """Termina la fase di join e inizia quella di votazione."""
    game = findgamebyid(update.message.chat.id)
    if game is not None and game.phase == 'Join':
        if update.message.from_user.id == game.admin.tid:
            game.message(bot, s.join_phase_ended)
            game.startpreset(bot)
        else:
            game.message(bot, s.error_not_admin)
    else:
        bot.sendMessage(update.message.chat.id, s.error_no_games_found, parse_mode=ParseMode.MARKDOWN)


def config(bot, update):
    """Configura il parametro richiesto."""
    game = findgamebyid(update.message.chat.id)
    if game is not None and game.phase is 'Config':
        if update.message.from_user.id == game.admin.tid:
            cmd = update.message.text.split(' ', 1)
            if len(cmd) >= 2:
                if game.configstep == 0:
                    try:
                        game.roleconfig["Mifioso"] = int(cmd[1])
                    except ValueError:
                        game.message(bot, s.error_invalid_config)
                    else:
                        game.configstep += 1
                        game.message(bot, s.config_list[game.configstep])
                elif game.configstep == 1:
                    try:
                        game.roleconfig["Investigatore"] = int(cmd[1])
                    except ValueError:
                        game.message(bot, s.error_invalid_config)
                    else:
                        game.configstep += 1
                        game.message(bot, s.config_list[game.configstep])
                elif game.configstep == 2:
                    try:
                        game.roleconfig["Angelo"] = int(cmd[1])
                    except ValueError:
                        game.message(bot, s.error_invalid_config)
                    else:
                        game.configstep += 1
                        game.message(bot, s.config_list[game.configstep])
                elif game.configstep == 3:
                    try:
                        game.roleconfig["Terrorista"] = int(cmd[1])
                    except ValueError:
                        game.message(bot, s.error_invalid_config)
                    else:
                        game.configstep += 1
                        game.message(bot, s.config_list[game.configstep])
                elif game.configstep == 4:
                    try:
                        game.roleconfig["Derek"] = int(cmd[1])
                    except ValueError:
                        game.message(bot, s.error_invalid_config)
                    else:
                        game.configstep += 1
                        game.message(bot, s.config_list[game.configstep])
                elif game.configstep == 5:
                    try:
                        game.roleconfig["Disastro"] = int(cmd[1])
                    except ValueError:
                        game.message(bot, s.error_invalid_config)
                    else:
                        game.configstep += 1
                        game.message(bot, s.config_list[game.configstep])
                elif game.configstep == 6:
                    try:
                        game.roleconfig["Mamma"] = int(cmd[1])
                    except ValueError:
                        game.message(bot, s.error_invalid_config)
                    else:
                        game.configstep += 1
                        game.message(bot, s.config_list[game.configstep])
                elif game.configstep == 7:
                    try:
                        game.roleconfig["Stagista"] = int(cmd[1])
                    except ValueError:
                        game.message(bot, s.error_invalid_config)
                    else:
                        game.configstep += 1
                        game.message(bot, s.config_list[game.configstep])
                elif game.configstep == 8:
                    try:
                        game.roleconfig["SignoreDelCaos"] = int(cmd[1])
                    except ValueError:
                        game.message(bot, s.error_invalid_config)
                    else:
                        game.configstep += 1
                        game.message(bot, s.config_list[game.configstep])
                elif game.configstep == 9:
                    try:
                        game.roleconfig["SignoreDelCaos"] = int(cmd[1])
                    except ValueError:
                        game.message(bot, s.error_invalid_config)
                    else:
                        game.configstep += 1
                        game.message(bot, s.config_list[game.configstep])
                elif game.configstep == 10:
                    if cmd[1].lower() == 'testa':
                        game.votingmifia = False
                        game.configstep += 1
                        game.message(bot, s.config_list[game.configstep])
                    elif cmd[1].lower() == 'unica':
                        game.votingmifia = True
                        game.configstep += 1
                        game.message(bot, s.config_list[game.configstep])
                    else:
                        game.message(bot, s.error_invalid_config)
                elif game.configstep == 11:
                    if cmd[1].lower() == 'perfetti':
                        game.missingmifia = False
                        game.endconfig(bot)
                    elif cmd[1].lower() == 'mancare':
                        game.missingmifia = True
                        game.configstep += 1
                        game.message(bot, s.config_list[game.configstep])
                    else:
                        game.message(bot, s.error_invalid_config)
                elif game.configstep == 12:
                    try:
                        miss = int(cmd[1])
                    except ValueError:
                        game.message(bot, s.error_invalid_config)
                    else:
                        if miss < 100:
                            game.misschance = miss
                        else:
                            game.misschance = 100
                        game.endconfig(bot)
            else:
                game.message(bot, s.config_list[game.configstep])
        else:
            game.message(bot, s.error_not_admin)
    else:
        bot.sendMessage(update.message.chat.id, s.error_no_games_found, parse_mode=ParseMode.MARKDOWN)


def vote(bot, update):
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
        game.message(bot, s.error_no_votes_on_first_day)
        return
    # Genera la tastiera
    table = list()
    for player in game.players:
        row = list()
        row.append(InlineKeyboardButton(s.vote_keyboard_line.format(name=player.tusername), callback_data=player.tusername))
        table.append(row)
    keyboard = InlineKeyboardMarkup(table)
    # Manda la tastiera
    bot.sendMessage(game.groupid, s.vote_keyboard, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard)


def endday(bot, update):
    """Termina la giornata attuale."""
    game = findgamebyid(update.message.chat.id)
    if game is not None and game.phase is 'Voting' and update.message.from_user.id == game.admin.tid:
        game.endday(bot)


def power(bot, update):
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
                        player.role.power(bot, game, cmd[2])
                    else:
                        player.message(bot, s.error_missing_parameters)
                else:
                    player.message(bot, s.error_dead)
            else:
                bot.sendMessage(update.message.chat.id, s.error_not_in_game, parse_mode=ParseMode.MARKDOWN)
        else:
            bot.sendMessage(update.message.chat.id, s.error_no_games_found, parse_mode=ParseMode.MARKDOWN)
    else:
        bot.sendMessage(update.message.chat.id, s.error_private_required, parse_mode=ParseMode.MARKDOWN)


def role(bot, update):
    """Visualizza il tuo ruolo."""
    game = findgamebyid(update.message.chat.id)
    if game is not None and game.phase is 'Voting':
        player = game.findplayerbyid(update.message.from_user.id)
        if player is not None:
            if player.alive:
                player.message(bot, s.role_assigned.format(icon=player.role.icon, name=player.role.name))
                game.message(bot, s.check_private)
            else:
                game.message(bot, s.error_dead)
        else:
            bot.sendMessage(update.message.chat.id, s.error_not_in_game, parse_mode=ParseMode.MARKDOWN)
    else:
        bot.sendMessage(update.message.chat.id, s.error_no_games_found, parse_mode=ParseMode.MARKDOWN)


def kill(bot, update):
    """Uccidi un giocatore in partita."""
    if __debug__:
        game = findgamebyid(update.message.chat.id)
        if game is not None and game.phase is 'Voting':
            if update.message.from_user.id == game.admin.tid:
                target = game.findplayerbyusername(update.message.text.split(' ')[1])
                if target is not None:
                    target.kill(bot, game)
                    game.message(bot, s.admin_killed.format(name=target.tusername,
                                                            icon=target.role.icon,
                                                            role=target.role.name))
                else:
                    game.message(bot, s.error_username)
            else:
                game.message(bot, s.error_not_admin)
        else:
            bot.sendMessage(update.message.chat.id, s.error_no_games_found, parse_mode=ParseMode.MARKDOWN)


def delete(bot, update):
    """Elimina una partita in corso."""
    if update.message.chat.type == 'private':
        if update.message.from_user.username == "Steffo":
            cmd = update.message.text.split(' ', 2)
            game = findgamebyname(cmd[1])
            # Se non lo trovi con il nome, prova con l'id
            if game is None:
                game = findgamebyid(int(cmd[1]))
            if game is not None:
                game.message(bot, s.owner_ended)
                game.endgame()
            else:
                game.message(bot, s.error_no_games_found)
        else:
            bot.sendMessage(update.message.chat.id, s.error_not_owner, parse_mode=ParseMode.MARKDOWN)
    else:
        bot.sendMessage(update.message.chat.id, s.error_chat_type, parse_mode=ParseMode.MARKDOWN)


def fakerole(bot, update):
    """Manda un finto messaggio di ruolo."""
    if update.message.chat.type == 'private':
        roles = rolepriority.copy()
        roles.append(Royal)
        for singlerole in roles:
            bot.sendMessage(update.message.chat.id, s.role_assigned.format(icon=singlerole.icon, name=singlerole.name),
                            parse_mode=ParseMode.MARKDOWN)
    else:
        bot.sendMessage(update.message.chat.id, s.error_private_required, parse_mode=ParseMode.MARKDOWN)


def load(bot, update):
    """Carica una partita salvata."""
    file = open(str(update.message.chat.id) + ".p", "rb")
    game = pickle.load(file)
    inprogress.append(game)
    game.message(bot, s.game_loaded)


def save(bot, update):
    """Salva una partita su file."""
    game = findgamebyid(update.message.chat.id)
    if game is not None:
        game.save(bot)
    else:
        bot.sendMessage(update.message.chat.id, s.error_no_games_found, parse_mode=ParseMode.MARKDOWN)


def debug(bot, update):
    """Visualizza tutti i ruoli e gli id."""
    if __debug__:
        game = findgamebyid(update.message.chat.id)
        if game is not None:
            game.revealallroles(bot)
        else:
            bot.sendMessage(update.message.chat.id, s.error_no_games_found, parse_mode=ParseMode.MARKDOWN)


def debugchangerole(bot, update):
    """Cambia il ruolo a un giocatore."""
    if __debug__:
        game = findgamebyid(update.message.chat.id)
        if game is not None:
            cmd = update.message.text.split(' ', 2)
            game.changerole(bot, game.findplayerbyusername(cmd[1]), globals()[cmd[2]])
        else:
            bot.sendMessage(update.message.chat.id, s.error_no_games_found, parse_mode=ParseMode.MARKDOWN)


def debuggameslist(bot, update):
    """Visualizza l'elenco delle partite in corso."""
    if __debug__:
        bot.sendMessage(update.message.from_user.id, repr(inprogress), parse_mode=ParseMode.MARKDOWN)


def inlinekeyboard(bot, update):
    """Seleziona un preset dalla tastiera."""
    game = findgamebyid(update.callback_query.message.chat.id)
    if game is not None:
        if game.phase is 'Preset':
            if update.callback_query.from_user.id == game.admin.tid:
                game.loadpreset(bot, update.callback_query.data)
        elif game.phase is 'Voting':
            # Trova il giocatore
            player = game.findplayerbyid(update.callback_query.from_user.id)
            if player is not None and player.alive:
                # Trova il bersaglio
                target = game.findplayerbyusername(update.callback_query.data)
                player.votingfor = target
                game.message(bot, s.vote.format(voting=player.tusername, voted=target.tusername))
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
updater.dispatcher.add_handler(CommandHandler('config', config))
updater.dispatcher.add_handler(CommandHandler('fakerole', fakerole))
updater.dispatcher.add_handler(CommandHandler('save', save))
updater.dispatcher.add_handler(CommandHandler('load', load))
updater.dispatcher.add_handler(CommandHandler('delete', delete))
updater.dispatcher.add_handler(CommandHandler('debugchangerole', debugchangerole))
updater.dispatcher.add_handler(CallbackQueryHandler(inlinekeyboard))
updater.start_polling()
print("Bot avviato!")
if __name__ == "__main__":
    while True:
        try:
            updater.idle()
        except TimedOut:
            time.sleep(10)
