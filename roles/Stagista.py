from .Role import Role
from .Derek import Derek
from .SignoreDelCaos import SignoreDelCaos
from .Servitore import Servitore
import strings as s

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

    def power(self, arg):
        target = self.player.game.findplayerbyusername(arg)
        if target is self.player:
            self.player.message(s.error_no_selfpower)
            return
        if target is None:
            self.player.message(s.error_username)
            return
        if not target.alive:
            self.player.message(s.error_target_is_dead)
        self.master = target
        self.player.message(s.intern_started_internship.format(master=self.master.tusername))

    def onendday(self):
        if self.master is not None:
            if isinstance(self.master.role, Derek) and self.master.role.chaos:
                self.player.game.message(s.intern_chaos_summoned)
                self.master.alive = True
                self.player.game.changerole(self.master, SignoreDelCaos)
                self.player.game.changerole(self.player, Servitore)
            else:
                self.player.game.message(s.intern_changed_role.format(icon=self.master.role.__class__.icon, role=self.master.role.__class__.name))
                self.player.game.changerole(self.player, self.master.role.__class__)
