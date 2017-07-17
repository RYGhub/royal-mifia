from .Role import Role
from .SignoreDelCaos import SignoreDelCaos
import strings as s

class Servitore(Role):
    """Il servitore del Caos è il sottoposto al Signore del Caos.
    Se non ci sono Signori del Caos in partita diventa Signore del Caos."""
    icon = s.chaos_servant_icon
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
            game.changerole(bot, self.player, SignoreDelCaos)
            game.message(bot, s.chaos_servant_inherited)
