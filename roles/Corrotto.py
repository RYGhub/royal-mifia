from .Role import Role
import strings as s

class Corrotto(Role):
    """Il corrotto è un investigatore che lavora per la Mifia."""
    icon = s.corrupt_icon
    team = 'Evil'
    name = s.corrupt_name
    powerdesc = s.corrupt_power_description
    refillpoweruses = 1

    def __init__(self, player):
        super().__init__(player)
        self.poweruses = self.refillpoweruses

    def __repr__(self) -> str:
        return "<Role: Corrotto, {uses} uses left>".format(uses=self.poweruses)

    def power(self, bot, game, arg):
        # Indaga sul vero ruolo di una persona, se sono ancora disponibili usi del potere.
        if self.poweruses <= 0:
            # Non hai abbastanza cariche!
            self.player.message(bot, s.error_no_uses)
            return
        target = game.findplayerbyusername(arg)
        if target is None:
            # Username non valido
            self.player.message(bot, s.error_username)
            return
        # Utilizza il potere su quella persona
        self.poweruses -= 1
        self.player.message(bot, s.detective_discovery.format(target=target.tusername,
                                                         icon=target.role.icon,
                                                         role=target.role.name,
                                                         left=self.poweruses))

    def onendday(self, bot, game):
        # Ripristina il potere
        self.poweruses = self.refillpoweruses
