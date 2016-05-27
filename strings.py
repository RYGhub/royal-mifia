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
mifia_target_selected = "Hai selezionato come bersaglio @{target}."

# Mifioso: bersaglio ucciso
mifia_target_killed = "@{target} è stato ucciso dalla Mifia.\n" \
                      "Era un *{icon} {role}*."

# Mifioso: bersaglio protetto da un angelo
mifia_target_protected = "@{target} è stato protetto dalla Mifia da {icon} @{protectedby}!"

# Mifioso: descrizione del potere
mifia_power_description = "Puoi selezionare come bersaglio di un'assassinio una personas.\n" \
                          "Per selezionare un bersaglio, scrivi in questa chat:\n" \
                          "`/power {gamename} nomeutentebersaglio`\n" \
                          "Alla fine del giorno, tutti i bersagli dei Mifiosi saranno eliminati!"

# Investigatore: icona
detective_icon = "\U0001F575"

# Investigatore: nome ruolo
detective_name = "Investigatore"

# Investigatore: scoperta nuove informazioni
detective_discovery = "@{target} è un *{icon} {role}*.\n" \
                      "Puoi usare il tuo potere ancora *{left}* volte oggi."

# Investigatore: descrizione del potere
detective_power_description = "Puoi indagare sul vero ruolo di una persona una volta al giorno.\n" \
                              "Per indagare su qualcuno, scrivi in questa chat:\n" \
                              "`/power {gamename} nomeutentebersaglio`\n"

# Angelo: icona
angel_icon = "\U0001F607"

# Angelo: nome ruolo
angel_name = "Angelo"

# Angelo: bersaglio selezionato
angel_target_selected = "Hai selezionato come protetto @{target}."

# Angelo: descrizione del potere
angel_power_description = "Puoi proteggere una persona dalla Mifia ogni notte.\n" \
                          "Se questa persona verrà attaccata, rimarrà viva, e il tuo ruolo sarà scoperto.\n" \
                          "Per proteggere una persona, scrivi in questa chat:\n" \
                          "`/power {gamename} nomeutentebersaglio`\n"

# Generale: ruolo assegnato
role_assigned = "Ti è stato assegnato il ruolo di *{icon} {name}*."

# Generale: giocatore ucciso dalle votazioni
player_lynched = "@{name} era il più votato ed è stato ucciso dai Royal.\n" \
                 "Era un *{icon} {role}*."

# Generale: nessun voto, nessun giocatore ucciso
no_players_lynched = "La Royal Games non è giunta a una decisione in questo giorno e non ha ucciso nessuno."

# Generale: partita creata
new_game = "E' stata creata una nuova partita in questo gruppo.\n" \
           "*ID:* {groupid}\n" \
           "*Nome:* {name}"

# Generale: un giocatore si è unito
player_joined = "@{name} si è unito alla partita!"

# Generale: fine della fase di join
join_phase_ended = "La fase di join è terminata."

# Generale: ruoli assegnati correttamente
roles_assigned_successfully = "I ruoli sono stati assegnati.\n" \
                              "Controlla la chat privata con @mifiabot per vedere il tuo."

# Generale: votazione completata
vote = "Hai votato per uccidere @{voted}."

# Generale: un admin ha ucciso un giocatore con /kill
admin_killed = "{name} è morto _di infarto_.\n" \
               "Era un *{icon} {role}*."

# Generale: richiesta la visualizzazione del proprio ruolo
display_role = "Il tuo ruolo è *{icon} {role}*."

# Generale: inviato messaggio in chat privata
check_private = "Messaggio inviato in chat privata.\n" \
                "Controlla @mifiabot."

# Vittoria: team Mifia
victory_mifia = "I Mifiosi rimasti sono più dei Royal.\n" \
                "*La Mifia vince!*"

# Vittoria: team Royal
victory_royal = "Tutti i Mifiosi sono stati eliminati.\n" \
                "*La Royal Games vince!*"

# Status: parte aggiunta prima dell'elenco dei giocatori (deve terminare con \n)
status_header = "*ID:* {name}\n" \
                "*Creatore:* {admin}\n" \
                "*Fase:* {phase}\n" \
                "*Giocatori partecipanti:*\n" 

# Status: giocatore inattivo (deve terminare con \n)
status_idle_player =  "{icon} @{name} ({votes})\n"

# Status: giocatore votante (deve terminare con \n)
status_voting_player = "{icon} @{name} ({votes}) vota per @{voting}\n"

# Status: giocatore morto (deve terminare con \n)
status_dead_player = "\U0001F480 @{name}\n"

# Ping!
pong = "Pong!"

# Errore: nome utente inesistente
error_username = "\U000026A0 Il nome utente specificato non esiste."

# Errore: usi del potere esauriti
error_no_uses = "\U000026A0 Non puoi più usare il tuo potere per oggi."

# Errore: numero troppo basso di giocatori
error_not_enough_players = "\U000026A0 Non ci sono abbastanza giocatori per avviare la partita."

# Errore: partita già in corso nel gruppo
error_game_in_progress = "\U000026A0 In questo gruppo è già in corso una partita."

# Errore: tipo di chat non supportato
error_chat_type = "\U000026A0 Non puoi creare una partita in questo tipo di chat."

# Errore: per usare questo comando, devi scrivere in chat privata
error_private_required = "\U000026A0 Non puoi usare questo comando in un gruppo.\n" \
                         "Scrivimi in chat privata a @mifiabot."

# Errore: giocatore già presente nella partita.
error_player_already_joined = "\U000026A0 Ti sei già unito alla partita."

# Errore: nessuna partita trovata
error_no_games_found = "\U000026A0 Non è stata trovata una partita su cui usare il comando."

# Errore: sei morto
error_dead = "\U000026A0 Sei morto." 

# Errore: azione riservata agli admin
error_not_admin = "\U000026A0 Questa azione è riservata al creatore della partita."

# Errore: non sei nella partita
error_not_in_game = "\U000026A0 Non fai parte della partita in corso."

# Errore: fase di join finita
error_join_phase_ended = "\U000026A0 La fase di unione è finita."

# Errore: angelo non può proteggere sè stesso
error_angel_no_selfprotect = "\U000026A0 Non puoi proteggere te stesso."

# Errore: parametro della configurazione non valido
error_invalid_config = "\U000026A0 Configurazione non valida."

# Lista dei possibili nomi di una partita
names_list = ["Modena",
              "Nonantola",
              "Sassuolo",
              "Vignola",
              "Carpi",
              "Formigine",
              "Mirandola",
              "Castelfranco",
              "Pavullo",
              "Maranello",
              "Fiorano",
              "Finale",
              "Soliera",
              "Castelnuovo",
              "Spilamberto",
              "Castelvetro",
              "Novi",
              "Bomporto",
              "Savignano",
              "Campogalliano",
              "Concordia",
              "Serramazzoni",
              "Cavezzo",
              "Medolla",
              "Ravarino",
              "Marano",
              "Zocca",
              "Guiglia"]

# Lista dei passi di configurazione da eseguire
config_list = ["Quanti Mifiosi devono essere nella partita?",
               "Quanti Investigatori devono essere nella partita?",
               "Quanti Angeli devono essere nella partita?",
               "I mifiosi possono uccidere una persona a `testa` al giorno o votano e decidono un'`unica` persona da uccidere per tutta la squadra?"]
