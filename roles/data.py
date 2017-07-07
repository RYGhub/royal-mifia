from .Role import Role
from .Angelo import Angelo
from .Corrotto import Corrotto
from .Derek import Derek
from .Disastro import Disastro
from .Investigatore import Investigatore
from .Mamma import Mamma
from .Mifioso import Mifioso
from .Royal import Royal
from .Servitore import Servitore
from .SignoreDelCaos import SignoreDelCaos
from .Stagista import Stagista
from .Terrorista import Terrorista

# Ordine in cui vengono eseguiti i onendday dei vari ruoli.
rolepriority = [Mifioso, Investigatore, Corrotto, Disastro, Angelo, Derek, Stagista, Terrorista, Mamma, SignoreDelCaos, Servitore]
