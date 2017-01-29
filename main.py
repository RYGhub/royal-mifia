#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-
import datetime
import pickle

import math
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram import ParseMode, TelegramError, InlineKeyboardButton, InlineKeyboardMarkup
import filemanager
import random
import strings as s
import logging

logging.basicConfig(level=logging.WARNING,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

token = filemanager.readfile('telegramapi.txt')
updater = Updater(token)

freenames = s.names_list.copy()


# Ruoli possibili per i giocatori
# Base di un ruolo
class Role:
    """Classe base di un ruolo. Da qui si sviluppano tutti gli altri ruoli."""
    icon = "-"  # Icona del ruolo, da visualizzare di fianco al nome
    team = 'None'  # Squadra: 'None', 'Good', 'Evil'
    name = "UNDEFINED"  # Nome del ruolo, viene visualizzato dall'investigatore e durante l'assegnazione
    powerdesc = None  # Ha un potere? Se sì, inviagli le info su come usarlo.

    def __init__(self, player):
        self.player = player

    def __repr__(self) -> str:
        r = "<undefined Role>"
        return r

    def power(self, bot, game, arg):
        """Il potere del ruolo. Si attiva quando il bot riceve un /power in chat privata."""
        pass

    def onendday(self, bot, game):
        """Metodo chiamato alla fine di ogni giorno."""
        pass

    def ondeath(self, bot, game):
        """Metodo chiamato alla morte del giocatore."""
        pass

    def onstartgame(self, bot, game):
        """Metodo chiamato all'inizio della partita."""
        pass


class Royal(Role):
    """Un membro della Royal Games. Il ruolo principale, non ha alcun potere se non quello di votare."""
    icon = s.royal_icon
    team = 'Good'
    name = s.royal_name

    def __init__(self, player):
        super().__init__(player)

    def __repr__(self) -> str:
        r = "<Role: Royal>"
        return r


class Mifioso(Role):
    """Il nemico globale. Può impostare come bersaglio una persona al giorno, per poi ucciderla alla fine."""
    icon = s.mifia_icon
    team = 'Evil'
    name = s.mifia_name
    powerdesc = s.mifia_power_description

    def __init__(self, player):
        super().__init__(player)
        self.target = None

    def __repr__(self) -> str:
        if self.target is None:
            r = "<Role: Mifioso>"
        else:
            r = "<Role: Mifioso, targeting {target}>".format(target=self.target.tusername)
        return r

    def power(self, bot, game, arg):
        # Imposta una persona come bersaglio da uccidere.
        selected = game.findplayerbyusername(arg)
        if selected is not None:
            self.target = selected
            self.player.message(bot, s.mifia_target_selected.format(target=self.target.tusername))
        else:
            self.player.message(bot, s.error_username)

    def onendday(self, bot, game):
        if not game.votingmifia:
            # Uccidi il bersaglio se non è protetto da un Angelo.
            if self.target is not None:
                if self.target.protectedby is None:
                    if game.missingmifia and random.randrange(0, 100) < game.misschance:
                        # Colpo mancato
                        game.message(bot, s.mifia_target_missed.format(target=self.target.tusername))
                    else:
                        # Uccisione riuscita
                        self.target.kill(bot, self)
                        game.message(bot, s.mifia_target_killed.format(target=self.target.tusername,
                                                                       icon=self.target.role.icon,
                                                                       role=self.target.role.name))
                else:
                    game.message(bot, s.mifia_target_protected.format(target=self.target.tusername,
                                                                      icon=self.target.protectedby.role.icon,
                                                                      protectedby=self.target.protectedby.tusername))
                self.target = None
        else:
            self.target = None


class Investigatore(Role):
    """L'investigatore può indagare sul vero ruolo di una persona una volta al giorno."""
    icon = s.detective_icon
    team = 'Good'
    name = s.detective_name
    powerdesc = s.detective_power_description
    refillpoweruses = 1

    def __init__(self, player):
        super().__init__(player)
        self.poweruses = self.refillpoweruses

    def __repr__(self) -> str:
        r = "<Role: Investigatore, {uses} uses left>".format(uses=self.poweruses)
        return r

    def power(self, bot, game, arg):
        # Indaga sul vero ruolo di una persona, se sono ancora disponibili usi del potere.
        if self.poweruses > 0:
            target = game.findplayerbyusername(arg)
            if target is not None:
                self.poweruses -= 1
                self.player.message(bot, s.detective_discovery.format(target=target.tusername,
                                                                 icon=target.role.icon,
                                                                 role=target.role.name,
                                                                 left=self.poweruses))
            else:
                self.player.message(bot, s.error_username)
        else:
            self.player.message(bot, s.error_no_uses)

    def onendday(self, bot, game):
        # Ripristina il potere
        self.poweruses = self.refillpoweruses


class Angelo(Role):
    """L'angelo può proteggere una persona al giorno dalla Mifia.
       Se ha successo nella protezione, il suo ruolo sarà rivelato a tutti."""
    icon = s.angel_icon
    team = 'Good'  # Squadra: 'None', 'Good', 'Evil'
    name = s.angel_name
    powerdesc = s.angel_power_description

    def __init__(self, player):
        super().__init__(player)
        self.protecting = None  # La persona che questo angelo sta proteggendo

    def __repr__(self) -> str:
        if self.protecting is None:
            r = "<Role: Angelo>"
        else:
            r = "<Role: Angelo, protecting {target}>".format(target=self.protecting.tusername)
        return r

    def power(self, bot, game, arg):
        # Imposta qualcuno come protetto
        selected = game.findplayerbyusername(arg)
        if selected is not None:
            if selected is not Player:  # TODO: cavolo ho scritto qui?
                # Togli la protezione a quello che stavi proteggendo prima
                if self.protecting is not None:
                    self.protecting.protectedby = None
                selected.protectedby = self.player
                self.protecting = selected
                self.player.message(bot, s.angel_target_selected.format(target=self.protecting.tusername))
            else:
                self.player.message(bot, s.error_angel_no_selfprotect)
        else:
            self.player.message(bot, s.error_username)

    def onendday(self, bot, game):
        # Resetta la protezione
        if self.protecting is not None:
            self.protecting.protectedby = None
        self.protecting = None


class Terrorista(Role):
    """Il terrorista è un mifioso che può uccidere in un solo modo: facendosi uccidere dai Royal.
       Se riesce, vince la partita e uccide tutti quelli che lo hanno votato."""
    icon = s.terrorist_icon
    team = "Evil"
    name = s.terrorist_name
    powerdesc = s.terrorist_power_description

    def __repr__(self) -> str:
        r = "<Role: Terrorista>"
        return r

    def ondeath(self, bot, game):
        # Se è stato ucciso da una votazione, attiva il suo potere
        if self.player == game.lastlynch:
            game.message(bot, s.terrorist_kaboom)
            for selectedplayer in game.players:
                if selectedplayer.votingfor == self.player:
                    game.message(bot, s.terrorist_target_killed.format(target=selectedplayer.tusername,
                                                                       icon=selectedplayer.role.icon,
                                                                       role=selectedplayer.role.name))
                    selectedplayer.kill(bot, game)


class Derek(Role):
    """Derek muore. Quando gli pare."""
    icon = s.derek_icon
    team = "Good"
    name = s.derek_name
    powerdesc = s.derek_power_description

    def __init__(self, player):
        super().__init__(player)
        # Per qualche motivo assurdo ho deciso di tenere l'oggetto Player qui
        self.deathwish = False
        self.chaos = False

    def __repr__(self) -> str:
        r = "<Role: Derek>"
        return r

    def power(self, bot, game, arg):
        # Attiva / disattiva la morte alla fine del round
        if self.deathwish:
            self.deathwish = False
            self.player.message(bot, s.derek_deathwish_unset)
        else:
            self.deathwish = True
            self.player.message(bot, s.derek_deathwish_set)

    def onendday(self, bot, game):
        if self.deathwish:
            game.message(bot, s.derek_deathwish_successful.format(name=self.player.tusername))
            self.player.kill(bot, game)
            self.chaos = True


class Disastro(Role):
    """L'investigatore sbadato investiga, ma giunge a conclusioni sbagliate..."""
    icon = s.detective_icon
    team = 'Good'
    name = s.detective_name
    powerdesc = s.detective_power_description
    refillpoweruses = 1

    def __init__(self, player):
        super().__init__(player)
        self.poweruses = self.refillpoweruses

    def __repr__(self) -> str:
        r = "<Role: Investigatore, {uses} uses left>".format(uses=self.poweruses)
        return r

    def power(self, bot, game, arg):
        # Indaga sul vero ruolo di una persona, se sono ancora disponibili usi del potere.
        if self.poweruses > 0:
            target = game.findplayerbyusername(arg)
            if target is not None:
                self.poweruses -= 1
                randomrole = random.sample(rolepriority, 1)[0]
                self.player.message(bot, s.detective_discovery.format(target=target.tusername,
                                                                 icon=randomrole.icon,
                                                                 role=randomrole.name,
                                                                 left=self.poweruses))
            else:
                self.player.message(bot, s.error_username)
        else:
            self.player.message(bot, s.error_no_uses)

    def onendday(self, bot, game):
        # Ripristina il potere
        self.poweruses = self.refillpoweruses

    def ondeath(self, bot, game):
        self.icon = s.disaster_icon
        self.name = s.disaster_name


class Mamma(Role):
    """La mamma sente i pettegolezzi in giro per la città e inizia conoscendo un ruolo a caso..."""
    icon = s.mom_icon
    team = 'Good'
    name = s.mom_name
    powerdesc = s.mom_power_description

    def __repr__(self) -> str:
        r = "<Role: Mamma>"
        return r

    def onstartgame(self, bot, game):
        while True:
            target = random.sample(game.players, 1)[0]
            if target == self.player:
                continue
            self.player.message(bot, s.mom_discovery.format(target=target.tusername,
                                                            icon=target.role.icon,
                                                            role=target.role.name))
            break


class Stagista(Role):
    """Lo stagista sceglie una persona da cui andare in stage e prende il suo ruolo."""
    icon = s.intern_icon
    team = 'Good'
    name = s.intern_name
    powerdesc = s.intern_power_description

    def __init__(self, player):
        super().__init__(player)
        self.master = None

    def __repr__(self) -> str:
        return "<Role: Stagista>"

    def power(self, bot, game, arg):
        target = game.findplayerbyusername(arg)
        if target is not None and target is not self.player and target.alive:
            self.master = target
            self.player.message(bot, s.intern_started_internship.format(master=self.master.tusername))
        else:
            self.player.message(bot, s.error_no_username)

    def onendday(self, bot, game):
        if self.master is not None:
            if isinstance(self.master.role, Derek) and self.master.role.chaos:
                game.message(bot, s.intern_chaos_summoned)
                self.master.alive = True
                game.changerole(bot, self.master, SignoreDelCaos)
                game.changerole(bot, self.player, Servitore)
            else:
                game.message(bot, s.intern_changed_role.format(icon=self.master.role.__class__.icon, role=self.master.role.__class__.name))
                game.changerole(bot, self.player, self.master.role.__class__)


class SignoreDelCaos(Role):
    """Il Signore del Caos è un Derek negli ultimi secondi prima della morte.
    Può cambiare la vita delle altre persone... Anche se non può decidere in cosa."""
    icon = s.chaos_lord_icon
    team = 'Chaos'
    name = s.chaos_lord_name
    powerdesc = s.chaos_lord_power_description

    def __init__(self, player):
        super().__init__(player)
        self.target = None

    def __repr__(self) -> str:
        return "<Role: Signore del Caos>"

    def power(self, bot, game, arg):
        selected = game.findplayerbyusername(arg)
        if selected is not None and selected is not self.player and selected.alive:
            self.target = selected
            self.player.message(bot, s.chaos_lord_target_selected.format(target=self.target.tusername))
        else:
            self.player.message(bot, s.error_no_username)

    def onendday(self, bot, game):
        if self.target is not None:
            if self.target.alive:
                if not isinstance(self.target.role, SignoreDelCaos) or not isinstance(self.target.role, Servitore):
                    randomrole = random.sample(rolepriority, 1)
                    game.changerole(bot, self.target, randomrole)
                    game.message(bot, s.chaos_lord_randomized)
                else:
                    game.message(bot, s.chaos_lord_failed)



class Servitore(Role):
    """Il servitore del Caos è il sottoposto al Signore del Caos.
    Se non ci sono Signori del Caos in partita diventa Signore del Caos."""
    icon = s.derek_icon
    team = 'Chaos'
    name = s.chaos_servant_name
    powerdesc = s.chaos_servant_power_description

    def __repr__(self) -> str:
        return "<Role: Servitore del Caos>"

    def onendday(self, bot, game):
        for chaoslord in game.playersinrole["SignoreDelCaos"]:
            if chaoslord.alive:
                break
        else:
            game.changerole(bot, self, SignoreDelCaos)
            game.message(bot, s.chaos_servant_inherited)


# Ordine in cui vengono eseguiti i onendday dei vari ruoli.
rolepriority = [Mifioso, Investigatore, Disastro, Angelo, Derek, Stagista, Terrorista, Mamma, SignoreDelCaos, Servitore]


class Player:
    """Classe di un giocatore. Contiene tutti i dati riguardanti un giocatore all'interno di una partita, come il ruolo,
       e i dati riguardanti telegram, come ID e username."""
    def __init__(self, tid, tusername, dummy=False):
        self.tid = tid  # ID di Telegram
        self.tusername = tusername  # Username di Telegram
        self.role = Role(self)  # Di base, ogni giocatore è un ruolo indefinito
        self.alive = True
        self.votingfor = None  # Diventa un player se ha votato
        self.votes = 0  # Voti che sta ricevendo questo giocatore. Aggiornato da updatevotes()
        self.protectedby = None  # Protettore. Oggetto player che protegge questo giocatore dalla mifia.
        self.mifiavotes = 0  # Voti che sta ricevendo questo giocatore dalla mifia. Aggiornato da updatemifiavotes()
        if __debug__:
            self.dummy = dummy  # E' un bot?

    def __repr__(self) -> str:
        r = "<Player {username}>".format(username=self.tusername)
        return r

    def message(self, bot, text):
        """Manda un messaggio privato al giocatore."""
        if not self.dummy:
            try:
                bot.sendMessage(self.tid, text, parse_mode=ParseMode.MARKDOWN)
            except TelegramError:
                pass


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

    def findplayerbyid(self, tid) -> Player:
        """Trova il giocatore con un certo id."""
        for player in self.players:
            if player.tid == tid:
                return player
        else:
            return None

    def findplayerbyusername(self, tusername) -> Player:
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
        # Seleziona mifiosi
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
        for player in self.playersinrole['Mifioso']:
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
        # Mifiosi
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
        self.day += 1

    def startpreset(self, bot):
        """Inizio della fase di preset"""
        self.phase = 'Preset'
        if __debug__:
            # Preset di debug
            self.roleconfig = {
                "Mifioso":        0,
                "Investigatore":  0,
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
            self.endconfig(bot)
            self.message(bot, "Utilizzando il preset di debug (tutti royal, cambia ruolo con `/debugchangerole nomeutente ruolo`.")
        else:
            # Crea la tastiera
            kbmarkup = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(s.preset_simple, callback_data="simple"),
                    InlineKeyboardButton(s.preset_classic, callback_data="classic"),
                    InlineKeyboardButton(s.preset_full, callback_data="full")
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
            # Preset semplice
            self.roleconfig = {
                "Mifioso":        math.floor(len(self.players) / 8) + 1,  # 1 Mifioso ogni 8 giocatori
                "Investigatore":  math.floor(len(self.players) / 12) + 1,  # 1 Detective ogni 12 giocatori
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
            self.endconfig(bot)
        elif preset == "classic":
            # Preset classico
            self.roleconfig = {
                "Mifioso":        math.floor(len(self.players) / 8) + 1,  # 1 Mifioso ogni 8 giocatori
                "Investigatore":  math.floor(len(self.players) / 12) + 1,  # 1 Detective ogni 12 giocatori
                "Angelo":         math.floor(len(self.players) / 10) + 1,  # 1 Angelo ogni 10 giocatori
                "Terrorista":     1 if random.randrange(0, 99) > 70 else 0,  # 30% di avere un terrorista
                "Derek":          0,
                "Disastro":       0,
                "Mamma":          0,
                "Stagista":       0,
                "SignoreDelCaos": 0,
                "Servitore":      0
            }
            self.votingmifia = True
            self.missingmifia = False
            self.endconfig(bot)
        elif preset == "full":
            # Preset completo
            self.roleconfig = {
                # 1 di ogni ruolo
                "Mifioso":        math.floor(len(self.players) / 9) + 1,
                "Investigatore":  math.floor(len(self.players) / 10) + 1,
                "Angelo":         math.floor(len(self.players) / 11) + 1,
                "Terrorista":     math.floor(len(self.players) / 12) + 1,
                "Derek":          math.floor(len(self.players) / 13) + 1,
                "Disastro":       math.floor(len(self.players) / 14) + 1,
                "Mamma":          math.floor(len(self.players) / 15) + 1,
                "Stagista":       math.floor(len(self.players) / 16) + 1,
                "SignoreDelCaos": 0,
                "Servitore":      0
            }
            self.votingmifia = True
            self.missingmifia = True
            self.misschance = 5
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

    def endgame(self):
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
        for player in self.players:
            if player.alive and player.role.team == 'Evil':
                evil += 1
            elif player.alive and player.role.team == 'Good':
                good += 1
        # Distruzione atomica!
        if good == 0 and evil == 0:
            self.message(bot, s.end_game_wiped)
            for player in self.players:
                player.message(bot, s.end_game_wiped + s.tie)
        # Mifiosi più dei Royal
        elif (not self.missingmifia and evil >= good) or good == 0:
            self.message(bot, s.end_mifia_outnumber + s.victory_mifia)
            for player in self.players:
                if player.role.team == 'Good':
                    player.message(bot, s.end_mifia_outnumber + s.defeat)
                elif player.role.team == 'Evil':
                    player.message(bot, s.end_mifia_outnumber + s.victory)
            self.endgame()
        # Male distrutto
        elif evil == 0:
            self.message(bot, s.end_mifia_killed + s.victory_royal)
            for player in self.players:
                if player.role.team == 'Good':
                    player.message(bot, s.end_mifia_killed + s.victory)
                elif player.role.team == 'Evil':
                    player.message(bot, s.end_mifia_killed + s.defeat)
            self.endgame()

    def changerole(self, bot, player, newrole):
        """Cambia il ruolo di un giocatore, aggiornando tutti i valori"""
        # Aggiorna le liste dei ruoli
        if player.role.__class__ != Royal:
            self.playersinrole[player.role.__class__.__name__].remove(player)
        if player.role.__class__ != Royal:
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
    bot.sendMessage(update.message.chat['id'], s.pong, parse_mode=ParseMode.MARKDOWN)


def newgame(bot, update):
    """Crea una nuova partita."""
    if update.message.chat['type'] != 'private':
        game = findgamebyid(update.message.chat['id'])
        if game is None:
            game = Game(update.message.chat['id'])
            inprogress.append(game)
            game.message(bot, s.new_game.format(groupid=game.groupid, name=game.name))
            join(bot, update)
        else:
            bot.sendMessage(update.message.chat['id'], s.error_game_in_progress, parse_mode=ParseMode.MARKDOWN)
    else:
        bot.sendMessage(update.message.chat['id'], s.error_chat_type, parse_mode=ParseMode.MARKDOWN)


def join(bot, update):
    """Unisciti a una partita."""
    game = findgamebyid(update.message.chat['id'])
    if game is not None:
        if game.phase == 'Join':
            p = game.findplayerbyid(update.message.from_user['id'])
            if p is None:
                try:
                    p = Player(update.message.from_user['id'], update.message.from_user['username'])
                except KeyError:
                    game.message(bot, s.error_no_username)
                else:
                    try:
                        p.message(bot, s.you_joined.format(game=game.name))
                    except TelegramError:
                        game.message(bot, s.error_chat_unavailable)
                    else:
                        game.message(bot, s.player_joined.format(name=p.tusername))
                        if len(game.players) == 0:
                            game.admin = p
                        game.players.append(p)
            else:
                game.message(bot, s.error_player_already_joined)
        else:
            game.message(bot, s.error_join_phase_ended)
    else:
        bot.sendMessage(update.message.chat['id'], s.error_no_games_found, parse_mode=ParseMode.MARKDOWN)


def debugjoin(bot, update):
    """Aggiungi un bot alla partita."""
    if __debug__:
        game = findgamebyid(update.message.chat['id'])
        if game is not None:
            if game.phase == 'Join':
                arg = update.message.text.split(" ")
                p = Player(random.randrange(0, 10000), arg[1], True)
                game.message(bot, s.player_joined.format(name=p.tusername))
                game.players.append(p)
            else:
                game.message(bot, s.error_join_phase_ended)
        else:
            bot.sendMessage(update.message.chat['id'], s.error_no_games_found, parse_mode=ParseMode.MARKDOWN)


def status(bot, update):
    """Visualizza lo stato della partita."""
    game = findgamebyid(update.message.chat['id'])
    if game is not None:
        text = str()
        if __debug__:
            text += s.debug_mode
        text += s.status_header.format(name=game.name, admin=game.admin.tusername, phase=game.phase)
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
        bot.sendMessage(update.message.chat['id'], s.error_no_games_found, parse_mode=ParseMode.MARKDOWN)


def endjoin(bot, update):
    """Termina la fase di join e inizia quella di votazione."""
    game = findgamebyid(update.message.chat['id'])
    if game is not None and game.phase == 'Join':
        if update.message.from_user['id'] == game.admin.tid:
            game.message(bot, s.join_phase_ended)
            game.startpreset(bot)
        else:
            game.message(bot, s.error_not_admin)
    else:
        bot.sendMessage(update.message.chat['id'], s.error_no_games_found, parse_mode=ParseMode.MARKDOWN)


def config(bot, update):
    """Configura il parametro richiesto."""
    game = findgamebyid(update.message.chat['id'])
    if game is not None and game.phase is 'Config':
        if update.message.from_user['id'] == game.admin.tid:
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
        bot.sendMessage(update.message.chat['id'], s.error_no_games_found, parse_mode=ParseMode.MARKDOWN)


def vote(bot, update):
    """Vota per uccidere una persona."""
    # Trova la partita
    game = findgamebyid(update.message.chat['id'])
    if game is None:
        bot.sendMessage(update.message.chat['id'], s.error_no_games_found, parse_mode=ParseMode.MARKDOWN)
        return
    elif game.phase is not 'Voting':
        bot.sendMessage(update.message.chat['id'], s.error_no_games_found, parse_mode=ParseMode.MARKDOWN)
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
    game = findgamebyid(update.message.chat['id'])
    if game is not None and game.phase is 'Voting' and update.message.from_user['id'] == game.admin.tid:
        game.endday(bot)


def power(bot, update):
    """Attiva il potere del tuo ruolo."""
    if update.message.chat['type'] == 'private':
        cmd = update.message.text.split(' ', 2)
        game = findgamebyname(cmd[1])
        # Se non lo trovi con il nome, prova con l'id
        if game is None:
            try:
                game = findgamebyid(int(cmd[1]))
            except ValueError:
                pass
        if game is not None:
            player = game.findplayerbyid(int(update.message.from_user['id']))
            if player is not None:
                if player.alive:
                    if len(cmd) > 2:
                        player.role.power(bot, game, cmd[2])
                    else:
                        player.message(bot, s.error_missing_parameters)
                else:
                    player.message(bot, s.error_dead)
            else:
                bot.sendMessage(update.message.chat['id'], s.error_not_in_game, parse_mode=ParseMode.MARKDOWN)
        else:
            bot.sendMessage(update.message.chat['id'], s.error_no_games_found, parse_mode=ParseMode.MARKDOWN)
    else:
        bot.sendMessage(update.message.chat['id'], s.error_private_required, parse_mode=ParseMode.MARKDOWN)


def role(bot, update):
    """Visualizza il tuo ruolo."""
    game = findgamebyid(update.message.chat['id'])
    if game is not None and game.phase is 'Voting':
        player = game.findplayerbyid(update.message.from_user['id'])
        if player is not None:
            if player.alive:
                player.message(bot, s.role_assigned.format(icon=player.role.icon, name=player.role.name))
                game.message(bot, s.check_private)
            else:
                game.message(bot, s.error_dead)
        else:
            bot.sendMessage(update.message.chat['id'], s.error_not_in_game, parse_mode=ParseMode.MARKDOWN)
    else:
        bot.sendMessage(update.message.chat['id'], s.error_no_games_found, parse_mode=ParseMode.MARKDOWN)


def kill(bot, update):
    """Uccidi un giocatore in partita."""
    if __debug__:
        game = findgamebyid(update.message.chat['id'])
        if game is not None and game.phase is 'Voting':
            if update.message.from_user['id'] == game.admin.tid:
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
            bot.sendMessage(update.message.chat['id'], s.error_no_games_found, parse_mode=ParseMode.MARKDOWN)


def delete(bot, update):
    """Elimina una partita in corso."""
    if update.message.chat['type'] == 'private':
        if update.message.from_user['username'] == "Steffo":
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
            bot.sendMessage(update.message.chat['id'], s.error_not_owner, parse_mode=ParseMode.MARKDOWN)
    else:
        bot.sendMessage(update.message.chat['id'], s.error_chat_type, parse_mode=ParseMode.MARKDOWN)


def fakerole(bot, update):
    """Manda un finto messaggio di ruolo."""
    if update.message.chat['type'] == 'private':
        for singlerole in rolepriority:
            bot.sendMessage(update.message.chat['id'], s.role_assigned.format(icon=singlerole.icon, name=singlerole.name),
                            parse_mode=ParseMode.MARKDOWN)
    else:
        bot.sendMessage(update.message.chat['id'], s.error_private_required, parse_mode=ParseMode.MARKDOWN)


def load(bot, update):
    """Carica una partita salvata."""
    file = open(str(update.message.chat['id']) + ".p", "rb")
    game = pickle.load(file)
    inprogress.append(game)
    game.message(bot, s.game_loaded)


def save(bot, update):
    """Salva una partita su file."""
    game = findgamebyid(update.message.chat['id'])
    if game is not None:
        game.save(bot)
    else:
        bot.sendMessage(update.message.chat['id'], s.error_no_games_found, parse_mode=ParseMode.MARKDOWN)


def debug(bot, update):
    """Visualizza tutti i ruoli e gli id."""
    if __debug__:
        game = findgamebyid(update.message.chat['id'])
        if game is not None:
            text = s.status_header.format(name=game.groupid, admin=game.admin.tid, phase=game.phase)
            game.updatevotes()
            # Aggiungi l'elenco dei giocatori
            for player in game.players:
                if not player.alive:
                    text += s.status_dead_player.format(name=player.tusername)
                else:
                    text += s.status_alive_player.format(icon=player.role.icon,
                                                         name=player.tusername,
                                                         votes=str(player.votes))
            game.message(bot, text)
        else:
            bot.sendMessage(update.message.chat['id'], s.error_no_games_found, parse_mode=ParseMode.MARKDOWN)


def debugchangerole(bot, update):
    """Cambia il ruolo a un giocatore."""
    if __debug__:
        game = findgamebyid(update.message.chat['id'])
        if game is not None:
            cmd = update.message.text.split(' ', 2)
            game.changerole(bot, game.findplayerbyusername(cmd[1]), globals()[cmd[2]])
        else:
            bot.sendMessage(update.message.chat['id'], s.error_no_games_found, parse_mode=ParseMode.MARKDOWN)


def debuggameslist(bot, update):
    """Visualizza l'elenco delle partite in corso."""
    if __debug__:
        bot.sendMessage(update.message.from_user['id'], repr(inprogress), parse_mode=ParseMode.MARKDOWN)


def inlinekeyboard(bot, update):
    """Seleziona un preset dalla tastiera."""
    game = findgamebyid(update.callback_query.message.chat['id'])
    if game is not None:
        if game.phase is 'Preset':
            if update.callback_query.from_user['id'] == game.admin.tid:
                game.loadpreset(bot, update.callback_query.data)
        elif game.phase is 'Voting':
            # Trova il giocatore
            player = game.findplayerbyid(update.callback_query.from_user['id'])
            if player is not None:
                # Trova il bersaglio
                target = game.findplayerbyusername(update.callback_query.data)
                player.votingfor = target
                game.message(bot, s.vote.format(voting=player.tusername, voted=target.tusername))
                bot.answerCallbackQuery(callback_query_id=update.callback_query.id, text=s.vote_fp.format(voted=target.tusername))


def handleerror(bot, update, error):
    print("Error: " + error)
    try:
        bot.sendMessage(update.message.chat['id'], error)
    except AttributeError:
        # Magari invece che pass are questo si potrebbe mandare un msg di debug o roba del genere
        pass


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
updater.dispatcher.add_error_handler(handleerror)
updater.start_polling()
print("Bot avviato!")
if __name__ == "__main__":
    updater.idle()
