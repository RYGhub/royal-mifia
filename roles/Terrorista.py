from .Role import Role
import strings as s

class Terrorista(Role):
    """Il terrorista è un mifioso che può uccidere in un solo modo: facendosi uccidere dai Royal.
       Se riesce, vince la partita e uccide tutti quelli che lo hanno votato."""
    icon = s.terrorist_icon
    team = "Evil"
    name = s.terrorist_name
    powerdesc = s.terrorist_power_description

    def __repr__(self) -> str:
        return "<Role: Terrorista>"

    def ondeath(self, bot, game):
        # Se è stato ucciso da una votazione, attiva il suo potere
        if self.player == game.lastlynch:
            game.message(bot, s.terrorist_kaboom)
            for selectedplayer in game.players:
                # Elimina ogni giocatore che sta votando per sè stesso
                if selectedplayer.votingfor == self.player:
                    game.message(bot, s.terrorist_target_killed.format(target=selectedplayer.tusername,
                                                                       icon=selectedplayer.role.icon,
                                                                       role=selectedplayer.role.name))
                    selectedplayer.kill(bot, game)