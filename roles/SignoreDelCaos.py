from .Role import Role
import strings as s
import random

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
            if self.target.alive and self.player.alive:
                if not isinstance(self.target.role, SignoreDelCaos):
                    randomrole = game.getrandomrole()
                    game.changerole(bot, self.target, randomrole)
                    game.message(bot, s.chaos_lord_randomized)
                else:
                    game.message(bot, s.chaos_lord_failed)
