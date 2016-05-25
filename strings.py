# -*- coding: utf-8 -*-
# Questo è l'elenco di tutte le stringhe usate in Royal Mifia.
# Modificando qui si dovrebbe riuscire a tradurre il gioco e rendere la modifica più semplice.

# Royal: icona
royal_icon = "\U0001F610"

# Royal: nome ruolo
royal_name = "Royal"

# Mifioso: icona
mifia_icon = "\U0001F47F"

# Mifioso: nome ruolo
mifia_name = "Mifioso"

# Mifioso: bersaglio selezionato
mifia_target_selected = "Hai selezionato come bersaglio {target}."

# Mifioso: bersaglio ucciso
mifia_target_killed = "{target} è stato ucciso dalla Mifia.\n"
                      "Era un {icon} {role}."

# Mifioso: bersaglio protetto da un angelo
mifia_target_protected = "{target} è stato protetto dalla Mifia da {icon} {protectedby}!"

# Investigatore: icona
detective_icon = "\U0001F575"

# Investigatore: nome ruolo
detective_name = "Investigatore"

# Investigatore: scoperta nuove informazioni
detective_discovery = "{target} è un {icon} {role}.\n"
                      "Puoi usare il tuo potere ancora {left} volte oggi."

# Angelo: icona
angel_icon = "\U0001F607"

# Angelo: nome ruolo
angel_name = "Angelo"

# Angelo: bersaglio selezionato
angel_target_selected = "Hai selezionato come protetto {target}."

# Generale: ruolo assegnato
role_assigned = "Ti è stato assegnato il ruolo di {icon} {name}."

# Generale: giocatore ucciso dalle votazioni
player_lynched = "{name} era il più votato ed è stato ucciso dai Royal.\n"
                 "Era un {icon} {role}."

# Generale: nessun voto, nessun giocatore ucciso
no_players_lynched = "La Royal Games non è giunta a una decisione in questo giorno e non ha ucciso nessuno."

# Generale: partita creata
new_game = "E' stata creata una nuova partita in questo gruppo.\n"
           "Nome: {name}"

# Generale: un giocatore si è unito
player_joined = "{name} si è unito alla partita!"

# Generale: fine della fase di join
join_phase_ended = "La fase di join è terminata."

# Generale: ruoli assegnati correttamente
roles_assigned_successfully = "I ruoli sono stati assegnati.\n"
                              "Controlla la chat privata con @mifiabot per vedere il tuo."

# Generale: votazione completata
vote = "Hai votato per uccidere {voted}."

# Vittoria: team Mifia
victory_mifia = "I Mifiosi rimasti sono più dei Royal.\n"
                "La Mifia vince!"

# Vittoria: team Royal
victory_royal = "Tutti i Mifiosi sono stati eliminati.\n"
                "La Royal Games vince!"

# Status: parte aggiunta prima dell'elenco dei giocatori (deve terminare con \n)
status_header = "Nome: {name}\n"
                "Creatore: {admin}\n"
                "Fase: {phase}\n" 
                "Giocatori partecipanti:\n"

# Status: giocatore inattivo (deve terminare con \n)
status_idle_player =  "{icon} {name} ({votes})\n"

# Status: giocatore votante (deve terminare con \n)
status_voting_player = "{icon} {name} ({votes}) vota per {voting}\n"

# Status: giocatore morto (deve terminare con \n)
status_dead_player = "\U0001F480 {name}\n"

# Ping!
pong = "Pong!"

# Errore: nome utente inesistente
error_username = "Il nome utente specificato non esiste."

# Errore: usi del potere esauriti
error_no_uses = "Non puoi più usare il tuo potere per oggi."

# Errore: numero troppo basso di giocatori
error_not_enough_players = "Non ci sono abbastanza giocatori per avviare la partita."

# Errore: partita già in corso nel gruppo
error_game_in_progress = "In questo gruppo è già in corso una partita."

# Errore: tipo di chat non supportato
error_chat_type = "Non puoi creare una partita in questo tipo di chat."

# Errore: per usare power, devi scrivere in chat privata
error_private_required = "Non puoi usare /power in un gruppo.\n"
                         "Scrivimi in chat privata a @mifiabot."

# Errore: giocatore già presente nella partita.
error_player_already_joined = "Ti sei già unito alla partita."

# Errore: nessuna partita in corso
error_no_games_found = "In questo gruppo non ci sono partite in corso."

# Errore: sei morto
error_dead = "Sei morto."
