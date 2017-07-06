from .Role import Role
import strings as s

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
        return "<Role: Investigatore, {uses} uses left>".format(uses=self.poweruses)

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