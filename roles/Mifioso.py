from .Role import Role
import strings as s

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
            return "<Role: Mifioso>"
        else:
            return "<Role: Mifioso, targeting {target}>".format(target=self.target.tusername)

    def power(self, arg):
        # Imposta una persona come bersaglio da uccidere.
        selected = self.player.game.findplayerbyusername(arg)
        if selected is None:
            self.player.message(s.error_username)
            return
        self.target = selected
        self.player.message(s.mifia_target_selected.format(target=self.target.tusername))

    def onendday(self):
        if self.player.game.votingmifia:
            # Se la partita è in modalità votingmifia l'uccisione della mifia viene gestita dalla classe Game
            self.target = None
        else:
            # Uccidi il bersaglio se non è protetto da un Angelo.
            if self.target is not None:
                if self.target.protectedby is None:
                    # Uccisione riuscita
                    self.target.kill()
                    self.player.game.message(s.mifia_target_killed.format(target=self.target.tusername, icon=self.target.role.icon, role=self.target.role.name))
                else:
                    # Bersaglio protetto da un angelo
                    self.player.game.message(s.mifia_target_protected.format(target=self.target.tusername, icon=self.target.protectedby.role.icon, protectedby=self.target.protectedby.tusername))
                self.target = None
