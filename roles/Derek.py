from .Role import Role
import strings as s

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
        return "<Role: Derek>"

    def power(self, arg):
        # Attiva / disattiva la morte alla fine del round
        self.deathwish = not self.deathwish
        if self.deathwish:
            self.player.message(s.derek_deathwish_set)
        else:
            self.player.message(s.derek_deathwish_unset)

    def onendday(self):
        if self.deathwish:
            self.player.game.message(s.derek_deathwish_successful.format(name=self.player.tusername))
            self.player.kill()
            self.chaos = True