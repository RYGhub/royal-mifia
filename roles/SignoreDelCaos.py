from .Role import Role
import strings as s

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

    def power(self, arg):
        selected = self.player.game.findplayerbyusername(arg)
        if selected is not None and selected is not self.player and selected.alive:
            self.target = selected
            self.player.message(s.chaos_lord_target_selected.format(target=self.target.tusername))
        else:
            self.player.message(s.error_no_username)

    def onendday(self):
        if self.target is not None:
            if self.target.alive and self.player.alive:
                if not isinstance(self.target.role, SignoreDelCaos):
                    randomrole = self.player.game.getrandomrole()
                    self.player.game.changerole(self.target, randomrole)
                    self.player.game.message(s.chaos_lord_randomized)
                else:
                    self.player.game.message(s.chaos_lord_failed)
