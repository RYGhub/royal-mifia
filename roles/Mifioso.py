from .Role import Role
import strings as s

class Mifioso(Role):
    """Il nemico globale. Può impostare come bersaglio una persona al giorno, per poi ucciderla alla fine."""
    icon = s.mifia_icon
    team = 'Evil'
    name = s.mifia_name
    powerdesc = s.mifia_power_description
    value = -100

    def __init__(self, player):
        super().__init__(player)
        self.target = None

    def __repr__(self) -> str:
        if self.target is None:
            return "<Role: Mifioso>"
        else:
            return "<Role: Mifioso, targeting {target}>".format(target=self.target.tusername)

    def power(self, bot, game, arg):
        # Imposta una persona come bersaglio da uccidere.
        selected = game.findplayerbyusername(arg)
        if selected is None:
            self.player.message(bot, s.error_username)
            return
        self.target = selected
        self.player.message(bot, s.mifia_target_selected.format(target=self.target.tusername))


    def onendday(self, bot, game):
        if game.votingmifia:
            # Se la partita è in modalità votingmifia l'uccisione della mifia viene gestita dalla classe Game
            self.target = None
        else:
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
                    # Bersaglio protetto da un angelo
                    game.message(bot, s.mifia_target_protected.format(target=self.target.tusername,
                                                                      icon=self.target.protectedby.role.icon,
                                                                      protectedby=self.target.protectedby.tusername))
                self.target = None
