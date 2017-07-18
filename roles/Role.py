# Base di un ruolo
class Role:
    """Classe base di un ruolo. Da qui si sviluppano tutti gli altri ruoli."""
    icon = "-"  # Icona del ruolo, da visualizzare di fianco al nome
    team = 'None'  # Squadra: 'None', 'Good', 'Evil', 'Chaos'; conta per le condizioni di vittoria
    name = "UNDEFINED"  # Nome del ruolo, viene visualizzato dall'investigatore e durante l'assegnazione
    powerdesc = None  # Ha un potere? Se sì, queste sono le info su come usarlo in seconda persona.

    def __init__(self, player):
        self.player = player

    def __repr__(self) -> str:
        return "<undefined Role>"

    def __str__(self) -> str:
        return "{} {}".format(self.icon, self.name)

    def power(self, arg):
        """Il potere del ruolo. Si attiva quando il bot riceve un /power in chat privata."""
        pass

    def onendday(self):
        """Metodo chiamato alla fine di ogni giorno."""
        pass

    def ondeath(self):
        """Metodo chiamato alla morte del giocatore."""
        pass

    def onstartgame(self):
        """Metodo chiamato all'inizio della partita."""
        pass