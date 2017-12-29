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
detective_discovery = "Sei sicuro al *{target_score}%* che @{target} sia un *{icon} {role}*."

# Investigatore: descrizione del potere
detective_power_description = "Puoi provare a scoprire il ruolo di una persona ogni giorno.\n" \
                              "Non è garantito che l'investigazione abbia successo, ma la probabilità è piuttosto alta e ti verrà annunciata.\n" \
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
terrorist_kaboom = "\U0001F4A3 *Boom!* Il terrorista si è fatto esplodere prima che poteste ucciderlo, mietendo vittime tra tutti" \
                   " quelli che lo hanno votato!"

# Terrorista: bersaglio ucciso
terrorist_target_killed = "\U0001F4A3 *Boom!* @{target} è morto a causa dell'esplosione!\n" \
                          "Era un *{icon} {role}*."

# Derek: icona
derek_icon = "\U0001F635"

# Derek: nome ruolo
derek_name = "Derek"

# Derek: descrizione del potere
derek_power_description = "Puoi decidere di suicidarti alla fine di un round.\n" \
                          "Potresti farlo per confondere le idee ai Royal, o per ragequittare con stile.\n" \
                          "Sta a te la scelta.\n" \
                          "Per lasciare questo mondo alla fine del giorno, scrivi in questa chat:\n" \
                          "`/power {gamename} banana`\n"

# Derek: morte attivata
derek_deathwish_set = "*Morirai* alla fine di questo giorno."

# Derek: morte disattivata
derek_deathwish_unset = "*Vivrai* per morire un altro giorno."

# Derek: morte
derek_deathwish_successful = "*SPOILER:* alla fine di questo giorno *\U0001F635 Derek Shepard* (@{name}) è morto schiacciato da un container durante una missione su Ilium.\n"

# Disastro: icona
disaster_icon = "\U0001F46E"

# Disastro: nome ruolo
disaster_name = "Carabiniere"

# Mamma: icona
mom_icon = "\U0001F917"

# Mamma: nome ruolo
mom_name = "Mamma"

# Mamma: descrizione del potere
mom_power_description = "Durante la partita scoprirai i ruoli di alcuni giocatori.\n" \
                        "A differenza dell'Investigatore, sei infallibile.\n"

# Mamma: scoperta di un ruolo
mom_discovery = "Hai scoperto che @{target} è un *{icon} {role}*.\n" \

# Stagista: icona
intern_icon = "\U0001F913"

# Stagista: nome ruolo
intern_name = "Stagista"

# Stagista: descrizione del potere
intern_power_description = "In qualsiasi momento della partita puoi scegliere un altro giocatore.\n" \
                           "Il tuo ruolo diventerà uguale al suo.\n" \
                           "Ricordati che, qualsiasi cosa succeda, è sempre colpa dello stagista, cioè tua!\n" \
                           "Per andare in stage, scrivi in questa chat:\n" \
                           "`/power {gamename} nomeutentedatoredilavoro`"

# Stagista: inizia lo stage
intern_started_internship = "Andrai in stage da @{master}."

# Stagista: cambiato ruolo
intern_changed_role = "Lo stagista ha finito il tirocinio ed ha imparato i segreti del mestiere di *{icon} {role}*."

# Stagista: EVOCATO IL SIGNORE DEL CAOS
intern_chaos_summoned = "Il *\U0001F479 Signore del Caos* e il suo fedele servitore sono scesi sulla Terra.\n" \
                        "Preparatevi... a non capirci più niente."

# Corrotto: icona
corrupt_icon = "\U0001F482"

# Corrotto: nome ruolo
corrupt_name = "Corrotto"

# Corrotto: descrizione potere
corrupt_power_description = "Puoi indagare sul vero ruolo di una persona una volta al giorno.\n" \
                            "Per indagare su qualcuno, scrivi in questa chat:\n" \
                            "`/power {gamename} nomeutentebersaglio`\n" \
                            "Sei praticamente un Investigatore, solo che lavori per la Mifia!\n"

# Signore del Caos: icona
chaos_lord_icon = "\U0001F479"

# Signore del Caos: nome ruolo
chaos_lord_name = "Signore del Caos"

# Signore del Caos: descrizione del potere
chaos_lord_power_description = "Sei il *SIGNORE DEL CAOS*!\n" \
                               "Le faccende dei mortali non ti interessano, quindi non fai parte nè del team Mifia nè del team Royal.\n" \
                               "Di conseguenza, hai automaticamente _vinto la partita_!\n" \
                               "Puoi usare i tuoi poteri del Caos per cambiare ruolo a un altro giocatore.\n" \
                               "Il ruolo che riceverà sarà casuale.\n" \
                               "Per usare i tuoi poteri, scrivi in questa chat:\n" \
                               "`/power {gamename} nomeutentebersaglio`"

# Signore del Caos: bersaglio selezionato
chaos_lord_target_selected = "BWHAHAHA. Hai deciso di usare i tuoi poteri del Caos su @{target}."

# Signore del Caos: bersaglio randomizzato
chaos_lord_randomized = "Il Caos è nell'aria...\n" \
                        "*Qualcuno ha cambiato ruolo!*"

# Signore del Caos: randomizzazione fallita
chaos_lord_failed = "Il Caos è nell'aria...\n" \
                    "_Ma non è successo nulla!?_"

# Servitore del Caos: nome ruolo
chaos_servant_name = "Servitore del Caos"

# Servitore del Caos: icona
chaos_servant_icon = "\U0001F468\u200d\U0001F3A4"

# Servitore del Caos: descrizione potere
chaos_servant_power_description = "Il Signore del Caos ti cederà i suoi poteri quando sarà morto.\n" \
                                  "Facendo parte della fazione del Caos, hai automaticamente _vinto la partita_!"

# Vigilante: nome ruolo
vigilante_name = "Vigilante"

# Vigilante: icona
vigilante_icon = "🤠"

# Vigilante: descrizione potere
vigilante_power_description = "Puoi scegliere una persona da uccidere anonimamente alla fine della giornata.\n" \
                              "Fai attenzione a non uccidere un tuo alleato Royal: sei in squadra con loro!\n" \
                              "Per uccidere qualcuno, scrivi in questa chat:\n" \
                              "`/power {gamename} nomeutentebersaglio`"

# Vigilante: bersaglio scelto
vigilante_target_selected = "Stai puntando la tua pistola contro @{target}."

# Vigilante: esecuzione
vigilante_execution = "@{target} è stato eseguito da un Vigilante della Royal Games.\n" \
                      "Era un *{icon} {role}*."

# Servitore del Caos: ereditato i poteri
chaos_servant_inherited = "Il servitore ha ereditato i poteri del *\U0001F479 Signore del Caos*."

# Generale: ruolo assegnato
role_assigned = "Ti è stato assegnato il ruolo di *{icon} {name}*."

# Generale: giocatore ucciso dalle votazioni
player_lynched = "@{name} era il più votato ed è stato ucciso dai Royal.\n" \
                 "Era un *{icon} {role}*."

# Generale: nessun voto, nessun giocatore ucciso
no_players_lynched = "La Royal Games non è giunta a una decisione in questo giorno e non ha ucciso nessuno."

# Generale: partita creata
new_game = "E' stata creata una nuova partita in questo gruppo.\n" \
           "*Nome:* {name}"

# Generale: un giocatore si è unito
player_joined = "@{name} si è unito alla partita!\n" \
                "Adesso ci sono {players} giocatori in partita."

# Generale: ti sei unito alla partita, in chat privata
you_joined = "Ti sei unito alla partita _{game}_!\n" \
             "Il ruolo ti verrà assegnato appena @{adminname} chiuderà le iscrizioni."

# Generale: fine della fase di join
join_phase_ended = "La fase di join è terminata."

# Generale: ruoli assegnati correttamente
roles_assigned_successfully = "I ruoli sono stati assegnati.\n" \
                              "Controlla la chat privata con @mifiabot per vedere il tuo."

# Generale: comunica ai mifiosi i loro compagni di squadra
mifia_team_intro = "I mifiosi in questa partita sono:\n"

# Generale: formattazione elenco mifiosi (deve terminare con \n)
mifia_team_player = "{icon} @{name}\n"

# Generale: votazione completata
vote = "@{voting} ha votato per uccidere @{voted}."

# Generale: votazione annullata
vote_none = "{player} ha annullato il suo voto."

# Generale: votazione completata in prima persona
vote_fp = "Hai votato per uccidere @{voted}."

# Generale: votazione annullata in prima persona
vote_none_fp = "Hai annullato il tuo voto."

# Generale: un admin ha ucciso un giocatore con /kill
admin_killed = "{name} è morto _di infarto_.\n" \
               "Era un *{icon} {role}*."

# Generale: inviato messaggio in chat privata
check_private = "Messaggio inviato in chat privata.\n" \
                "Controlla @mifiabot."

# Generale: partita salvata
game_saved = "Partita _{name}_ salvata su file."

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

# Vittoria: Sei un Signore del Caos.
end_game_chaos = "Sei un Signore del Caos."

# Generale: scegli per chi votare
vote_keyboard = "Scegli chi vuoi linciare!\n" \
                "Se più giocatori hanno lo stesso numero di voti, uno tra loro verrà selezionato per essere linciato.\n" \
                "Se nessuno ha votato, "

# Generale: riga della tastiera del voto
vote_keyboard_line = "{status} {votes} - {player}"

# Generale: riga della tastiera per annullare il voto
vote_keyboard_nobody = "\u2796 Nessuno"

# Generale: inizia un nuovo giorno
new_day = "Sorge l'alba del giorno *{day}*!"

# Vittoria: team Royal
victory_royal = "*La Royal Games vince!*"

# Vittoria: team Mifia
victory_mifia = "*La Mifia vince!*"

# Vittoria!
victory = "*Hai vinto!*"

# Sconfitta.
defeat = "*Hai perso...*"

# Pareggio?
tie = "*Pareggio?*"

# Status: parte aggiunta prima dell'elenco dei giocatori (deve terminare con \n)
status_header = "*Nome:* {name}\n" \
                "*Creatore:* {admin}\n" \
                "*Fase:* {phase}\n" \
                "*Giocatori partecipanti:*\n"

# Status: parte aggiunta prima della rivelazione finale dei ruoli
status_final_header = "*Ruoli della partita {name}:*\n"

# Status: giocatore vivo durante la prima giornata / fase di join (deve terminare con \n)
status_basic_player = "{icon} {player}\n"

# Status: risultati finali della partita

# Status: giocatore vivo (deve terminare con \n)
status_alive_player = "{icon} {player} __(vota per {target})__\n"

# Status: giocatore morto (deve terminare con \n)
status_dead_player = "\U0001F480 {player}\n"

# Status: giocatore più votato della partita
status_most_voted = "\U0001F534"

# Status: voti giocatore normali
status_normal_voted = "\u26AA"

# Status: Modalità debug
debug_mode = "*DEBUG/CHEATS MODE*\n"

# Ping!
pong = "Pong!"

# Attenzione: il bot non è amministratore
warning_bot_not_admin = "\U000026A0 Attenzione! Il bot non è amministratore in questo supergruppo.\n" \
                        "E' possibile comunque giocare una partita, ma alcune funzioni non saranno disponibili."

# Errore: nome utente inesistente
error_username = "\U000026A0 Il nome utente specificato non esiste."

# Errore: usi del potere esauriti
error_no_uses = "\U000026A0 Hai finito gli utilizzi del tuo potere."

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

# Errore: il bersaglio è morto
error_target_is_dead = "\U000026A0 Non puoi bersagliare giocatori morti."

# Errore: azione riservata agli admin
error_not_admin = "\U000026A0 Questa azione è riservata al creatore della partita."

# Errore: azione riservata al proprietario
error_not_owner = "\U000026A0 Questa azione è riservata al proprietario del bot."

# Errore: non sei nella partita
error_not_in_game = "\U000026A0 Non fai parte della partita in corso."

# Errore: fase di join finita
error_join_phase_ended = "\U000026A0 La fase di unione è finita."

# Errore: non puoi usare il potere su te stesso
error_no_selfpower = "\U000026A0 Non puoi usare il potere su te stesso."

# Errore: parametro della configurazione non valido
error_invalid_config = "\U000026A0 Configurazione non valida."

# Errore: il giocatore non ha mai scritto un messaggio in chat privata al bot
error_chat_unavailable = "\U000026A0 Non hai mai scritto un messaggio in chat privata a @mifiabot!\n" \
                         "Scrivigli nella chat privata `/start` e riprova."

# Erorre: nessun username
error_no_username = "\U000026A0 Non hai nessun username di Telegram!\n" \
                    "Vai nelle impostazioni e inseriscine uno!"

# Errore: non si può votare nella prima giornata
error_no_votes_on_first_day = "\U000026A0 I Royal non votano nella prima giornata, dato che non si sono ancora verificati omicidii."

# Errore: mancano dei parametri nel comando
error_missing_parameters = "\U000026A0 Mancano uno o più parametri.\n" \
                           "Controlla la sintassi del comando e riprova."

# Critico: Server di telegram Timed Out
fatal_bot_timed_out = "\U0001F6D1 **Errore critico:** I server di Telegram non hanno risposto in tempo al messaggio.\n" \
                      "Se una partita era in corso, potrebbero essersi creati dei bug.\n" \
                      "E' consigliato cancellarla e ricaricare l'ultimo salvataggio disponibile."

# Critico: Rate limited
fatal_bot_rate_limited = "\U0001F6D1 **Errore critico:** Il bot ha inviato troppe richieste a Telegram ed è stato bloccato.\n" \
                         "Se una partita era in corso, potrebbero essersi creati dei bug.\n" \
                         "E' consigliato attendere 5 minuti, cancellarla e ricaricare l'ultimo salvataggio disponibile."

# Lista dei possibili nomi di una partita
if __debug__:
    names_list = ["Dev"]
else:
    names_list = ["Tredici"]

# Scegli il preset
preset_choose = "*Seleziona un preset per la partita:*" 

# Preset semplice
preset_simple = "Semplice"

# Preset semplice selezionato
preset_simple_selected = "Selezionato il preset *Semplice*.\n" \
                         "In partita saranno presenti:\n" \
                         "*{mifioso}* Mifiosi,\n" \
                         "*{investigatore}* Investigatori\n" \
                         "e *{royal}* Royal."

# Preset classico
preset_classic = "Classico"

# Preset classico selezionato
preset_classic_selected = "Selezionato il preset *Classico*.\n" \
                          "In questa partita saranno presenti:\n" \
                          "*{mifioso}* Mifiosi,\n" \
                          "*{investigatore}* Investigatori,\n" \
                          "*{angelo}* Angeli,\n" \
                          "*forse* un Terrorista \n" \
                          "e *{royalmenouno}* o *{royal}* Royal.\n" \

# Preset avanzato
preset_advanced = "Avanzato"

# Preset avanzato selezionato
preset_advanced_selected = "Selezionato il preset *Avanzato*.\n" \
                           "I ruoli in questa partita sono casuali!\n" \
                           "Inoltre, ogni mifioso può uccidere una persona diversa ogni giorno...\n"

# Partita in cui i Mifiosi hanno un grande vantaggio (<-30)
balance_mifia_big = "_La mifia ha un grande vantaggio in questa partita.\n" \
                    "Buona fortuna, Royal Games, ne avrete bisogno!_"

# Partita in cui i Royal hanno un grande vantaggio (>+30)
balance_royal_big = "_La Royal Games ha un grande vantaggio in questa partita.\n" \
                    "State attenti, Mifiosi!_"

# Partita in cui i Mifiosi hanno un leggero vantaggio (>-30)
balance_mifia_small = "_La mifia è leggermente avvantaggiata in questa partita._"

# Partita in cui i Royal hanno un leggero vantaggio (<+30)
balance_royal_small = "_La Royal Games è leggermente avvantaggiata in questa partita._"

# Partita bilanciata (-5<x<5)
balance_perfect = "_La partita sembra bilanciata per entrambe le squadre, nessuno sembra avere un grosso vantaggio.\n" \
                  "Buona fortuna a tutti!_"

# Preset con uno di tutti
preset_oneofall = "Round Robin"

# Preset con uno di tutti selezionato
preset_oneofall_selected = "Selezionato il preset *Round Robin*.\n" \
                           "In questa partita saranno presenti lo stesso numero di tutti i ruoli.\n" \
			               "Se sono presenti giocatori in eccesso, verrà assegnato loro un ruolo casuale."

# Preset selezionato
preset_selected = "Preset selezionato: {selected}"

# Nome gruppo
group_name = "{phase} - Mifia {name}"

# Giorno
day = "Day {day}"
