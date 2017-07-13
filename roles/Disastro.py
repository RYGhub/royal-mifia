from .Role import Role
import strings as s
import random

class Disastro(Role):
    """L'investigatore sbadato investiga, ma giunge a conclusioni sbagliate..."""
    icon = s.detective_icon
    team = 'Good'
    name = s.detective_name
    powerdesc = s.detective_power_description
    value = 5
    refillpoweruses = 1

    def __init__(self, player):
        super().__init__(player)
        self.poweruses = self.refillpoweruses

    def __repr__(self) -> str:
        return "<Role: Investigatore, {uses} uses left>".format(uses=self.poweruses)

    def power(self, bot, game, arg):
        # Indaga sul vero ruolo di una persona, se sono ancora disponibili usi del potere.
        if self.poweruses > 0:
            target = game.findplayerbyusername(arg)
            if target is not None:
                self.poweruses -= 1
                randomrole = game.getrandomrole()
                while isinstance(target.role, randomrole):
                    # TODO:  se ci fossero solo disastri in una partits cosa succederebbe?	
                    randomrole = game.getrandomrole()
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
