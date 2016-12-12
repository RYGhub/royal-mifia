# -*- coding: utf-8 -*-
# Questo è l'elenco di tutte le stringhe usate in Royal Mifia.
# Modificando qui si dovrebbe riuscire a tradurre il gioco e rendere la modifica più semplice.

# Royal: icona
royal_icon = "\U0001F610"

# Royal: nome ruolo
royal_name = "Royal"

# Royal: come giocare
royal_help = "I Royal non hanno alcun potere speciale."

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
mifia_power_description = "Puoi selezionare come bersaglio di un'assassinio una persona.\n" \
                          "Per selezionare un bersaglio, scrivi in questa chat:\n" \
                          "`/power {gamename} nomeutentebersaglio`\n" \
                          "Alla fine del giorno, tutti i bersagli dei Mifiosi saranno eliminati!\n"

# Mifioso: uccisione fallita
mifia_target_missed = "@{target} ha subito un tentativo di assassinio da parte della Mifia!\n" \
                      "Per fortuna, è riuscito a evitare l'attacco."

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

# Terrorista: icona
terrorist_icon = "\U0001F60E"

# Terrorista: nome ruolo
terrorist_name = "Terrorista"

# Terrorista: descrizione del potere
terrorist_power_description = "Puoi fare saltare in aria un sacco di persone!\n" \
                              "Se vieni votato come colpevole di associazione mifiosa, potrai fare esplodere tutti" \
                              " quelli che ti hanno votato!\n" \
                              "La mifia non sa chi sei, ma fai parte della squadra dei malvagi.\n"

# Terrorista: esplosione
terrorist_kaboom = "Boom! Il terrorista si è fatto esplodere prima che poteste ucciderlo, mietendo vittime tra tutti" \
                   " quelli che lo hanno votato!"

# Terrorista: bersaglio ucciso
terrorist_target_killed = "Boom! @{target} è esploso!\n" \
                          "Era un *{icon} {role}*."

# Derek: icona
derek_icon = "\U0001F635"

# Derek: nome ruolo
derek_name = "Derek"

# Derek: descrizione del potere
derek_power_description = "Puoi decidere di suicidarti alla fine di un round.\n" \
                          "Potresti farlo per confondere le idee ai Royal, o per ragequittare malissimo.\n" \
                          "Sta a te la scelta.\n" \
                          "Per lasciare questo mondo alla fine del giorno, scrivi in questa chat:\n" \
                          "`/power {gamename}`\n"

# Derek: morte attivata
derek_deathwish_set = "*Morirai* alla fine di questo giorno."

# Derek: morte disattivata
derek_deathwish_unset = "*Vivrai* per morire un altro giorno."

# Derek: morte
derek_deathwish_successful = "SPOILER: alla fine di questa giornata *\U0001F635 Derek* (@{name}) muore schiacciato da un container.\n"

# Disastro: icona
disaster_icon = "\U0001F913"

# Disastro: nome ruolo
disaster_name = "Disastro"

# Mamma: icona
mom_icon = "\U0001F917"

# Mamma: nome ruolo
mom_name = "Mamma"

# Mamma: descrizione del potere
mom_power_description = "All'inizio della partita scoprirai il ruolo di un giocatore casuale.\n" \
                        "Usalo per sapere di chi (non) fidarti!\n"

# Mamma: scoperta di un ruolo
mom_discovery = "@{target} è un *{icon} {role}*.\n" \

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

# Generale: ti sei unito alla partita, in chat privata
you_joined = "Ti sei unito alla partita _{game}_!"

# Generale: fine della fase di join
join_phase_ended = "La fase di join è terminata."

# Generale: ruoli assegnati correttamente
roles_assigned_successfully = "I ruoli sono stati assegnati.\n" \
                              "Controlla la chat privata con @mifiabot per vedere il tuo."

# Generale: comunica ai mifiosi i loro compagni di squadra
mifia_team_intro = "I mifiosi in questa partita sono:\n"

# Generale: formattazione elenco mifiosi (deve terminare con \n)
mifia_team_player = "{icon} {name}\n"

# Generale: votazione completata
vote = "Hai votato per uccidere @{voted}."

# Generale: un admin ha ucciso un giocatore con /kill
admin_killed = "{name} è morto _di infarto_.\n" \
               "Era un *{icon} {role}*."

# Generale: inviato messaggio in chat privata
check_private = "Messaggio inviato in chat privata.\n" \
                "Controlla @mifiabot."

# Generale: partita caricata
game_loaded = "Partita caricata da file."

# Generale: partita terminata remotamente dal proprietario del bot
owner_ended = "Il proprietario del bot ha eliminato questa partita."

# Vittoria: Mifia >= Royal
end_mifia_outnumber = "I Mifiosi rimasti sono più dei Royal.\n" \
                      "La Mifia ha preso il controllo della città.\n"

# Vittoria: Mifia == 0
end_mifia_killed = "Tutti i Mifiosi sono stati eliminati.\n"

# Vittoria: nessuno vivo lol
end_game_wiped = "Nessuno è più vivo. La specie umana si è estinta.\n"

# Vittoria: team Royal
victory_royal = "**La Royal Games vince!**"

# Vittoria: team Mifia
victory_mifia = "**La Mifia vince!**"

# Vittoria!
victory = "*Hai vinto!*"

# Sconfitta.
defeat = "*Hai perso...*"

# Pareggio?
tie = "*Pareggio?*"

# Status: parte aggiunta prima dell'elenco dei giocatori (deve terminare con \n)
status_header = "*ID:* {name}\n" \
                "*Creatore:* {admin}\n" \
                "*Fase:* {phase}\n" \
                "*Giocatori partecipanti:*\n" 

# Status: giocatore vivo durante la prima giornata / fase di join (deve terminare con \n)
status_basic_player = "{icon} @{name}\n"

# Status: giocatore vivo (deve terminare con \n)
status_alive_player = "{icon} @{name} ({votes} voti)\n"

# Status: giocatore morto (deve terminare con \n)
status_dead_player = "\U0001F480 @{name}\n"

# Status: Modalità debug
debug_mode = "*DEBUG/CHEATS MODE*\n"

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

# Errore: azione riservata al proprietario
error_not_owner = "\U000026A0 Questa azione è riservata al proprietario del bot."

# Errore: non sei nella partita
error_not_in_game = "\U000026A0 Non fai parte della partita in corso."

# Errore: fase di join finita
error_join_phase_ended = "\U000026A0 La fase di unione è finita."

# Errore: angelo non può proteggere sè stesso
error_angel_no_selfprotect = "\U000026A0 Non puoi proteggere te stesso."

# Errore: parametro della configurazione non valido
error_invalid_config = "\U000026A0 Configurazione non valida."

# Errore: il giocatore non ha mai scritto un messaggio in chat privata al bot
error_chat_unavailable = "\U000026A0 Non hai mai scritto un messaggio in chat privata a @mifiabot!\n" \
                         "Scrivigli nella chat privata `/start` e riprova."

# Erorre: nessun username
error_no_username = "\U000026A0 Non hai nessun username di Telegram!\n" \
                    "Specificane uno nelle opzioni!"

# Errore: non si può votare nella prima giornata
error_no_votes_on_first_day = "\U000026A0 I Royal non votano nella prima giornata, dato che non si sono ancora verificati omicidii."

# Lista dei possibili nomi di una partita
names_list = ["Cassata",
              "Cannoli",
              "Granita",
              "Mandorle",
              "Salame",
              "Torrone",
              "Sorbetto",
              "Limone",
              "Arancia"]

# Lista dei passi di configurazione da eseguire
config_list = ["Quanti *Mifiosi* devono essere nella partita?",
               "Quanti *Investigatori* devono essere nella partita?",
               "Quanti *Angeli* devono essere nella partita?",
               "Quanti *Terroristi* devono essere nella partita?",
               "Quanti *Derek* devono essere nella partita?",
               "Quanti *Disastri* devono essere nella partita?",
               "Quante *Mamme* devono essere nella partita?",
               "I mifiosi possono uccidere una persona a `testa` al giorno "
               "o votano e decidono un'`unica` persona da uccidere per tutta la squadra?",
               "La mifia può `mancare` le uccisioni o i loro attacchi sono `perfetti`?",
               "Qual è la percentuale di attacchi falliti della mifia?"]

# Scegli il preset
preset_choose = "*Seleziona un preset per la partita:*\n" \
                "`Semplice`: solo royal, mifia e investigatori e niente meccaniche avanzate. _(minimo 3 giocatori)_\n" \
                "`Classico`: royal, mifia, investigatori, angeli e la comparsa casuale di un terrorista! _(minimo 4 giocatori)_\n" \
                "`Completo`: tutti i ruoli e le meccaniche nuove! _(minimo 7 giocatori)_\n" \
                "`Personalizzato`: scegli tu i ruoli e le meccaniche che vuoi in partita!"

# Preset semplice
preset_simple = "Semplice"

# Preset classico
preset_classic = "Classico"

# Preset completo
preset_full = "Completo"

# Personalizza
preset_custom = "Personalizzato"

# Preset selezionato
preset_selected = "Preset selezionato: {selected}"