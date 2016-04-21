# -*- coding: utf-8 -*-
import requests
import filemanager
import time

# Per far funzionare questa libreria serve un file "lastid.txt" contenente l'update ID dell'ultimo messaggio non letto e
# un file "telegramapi.txt" contenente il token di accesso del bot assegnato da @BotFather.
telegramtoken = filemanager.readfile('telegramapi.txt')


def getme() -> dict():
    """Visualizza dati sul bot."""
    # Manda la richiesta
    data = requests.get("https://api.telegram.org/bot" + telegramtoken + "/getMe")
    return data


def getupdates() -> dict():
    """Ricevi gli ultimi aggiornamenti dal server di Telegram e restituisci l'ultimo messaggio non letto."""
    while True:
        parametri = {
            'offset': filemanager.readfile("lastid.txt"),  # Update ID del messaggio da leggere
            'limit': 1,  # Numero di messaggi da ricevere alla volta, lasciare 1
            'timeout': 1500,  # Secondi da mantenere attiva la richiesta se non c'e' nessun messaggio
        }
        data = requests.get("https://api.telegram.org/bot" + telegramtoken + "/getUpdates", params=parametri)
        if data.status_code == 200:
            data = data.json()
            if data['ok']:
                if data['result']:
                    filemanager.writefile("lastid.txt", str(data['result'][0]['update_id'] + 1))
                    # Controlla che la risposta sia effettivamente un messaggio e non una notifica di servizio
                    if 'message' in data['result'][0]:
                        return data['result'][0]['message']
        else:
            # Non vogliamo DDoSsare telegram, vero?
            time.sleep(2)


def sendmessage(content, to, reply=None) -> None:
    """Manda un messaggio a una chat.
    :param content: Testo del messaggio
    :param to: Destinatario del messaggio
    :param reply: Messaggio a cui rispondere
    """
    # Parametri del messaggio
    parametri = {
        'chat_id': to,
        'text': content,
        'parse_mode': 'Markdown',  # Formattare il messaggio?
        'reply_to_message_id': reply
    }
    # Manda il messaggio
    requests.get("https://api.telegram.org/bot" + telegramtoken + "/sendMessage", params=parametri)


def forwardmessage(msg, sentby, to) -> None:
    """Inoltra un messaggio mandato in un'altra chat.
    :param msg: ID del messaggio
    :param sentby: Persona da cui è stato mandato il messaggio
    :param to: Destinatario del messaggio inoltrato
    """
    parametri = {
        'chat_id': to,
        'from_chat_id': sentby,
        'message_id': msg,
    }
    # Manda la richiesta ai server di Telegram.
    requests.get("https://api.telegram.org/bot" + telegramtoken + "/forwardMessage", params=parametri)


def sendphoto(pic, text, to) -> None:
    """Manda una foto compressa a una chat.
    :param pic: ID della foto da inviare
    :param text: Testo della foto da inviare
    :param to: Destinatario della foto
    """
    parametri = {
        'chat_id': to,
        'photo': pic,
        'caption': text,
    }
    # Manda la richiesta ai server di Telegram.
    requests.get("https://api.telegram.org/bot" + telegramtoken + "/sendPhoto", params=parametri)


def sendaudio(aud, to) -> None:
    """Manda un file audio .mp3 a una chat.
    :param aud: ID del file audio
    :param to: Destinatario dell'audio
    """
    parametri = {
        'chat_id': to,
        'audio': aud,
    }
    # Manda la richiesta ai server di Telegram.
    requests.get("https://api.telegram.org/bot" + telegramtoken + "/sendAudio", params=parametri)


def senddocument(doc, to, reply=None) -> None:
    """Manda un file a una chat.
    :param reply: ID del messaggio a cui rispondere
    :param doc: ID del documento
    :param to: Destinatario del documento
    """
    parametri = {
        'chat_id': to,
        'document': doc,
        'reply_to_message_id': reply
    }
    # Manda la richiesta ai server di Telegram.
    requests.get("https://api.telegram.org/bot" + telegramtoken + "/sendDocument", params=parametri)


def sendsticker(stk, to) -> None:
    """Manda uno sticker a una chat.
    :param stk: ID dello sticker
    :param to: Destinatario dello sticker
    """
    parametri = {
        'chat_id': to,
        'sticker': stk,
    }
    # Manda la richiesta ai server di Telegram.
    requests.get("https://api.telegram.org/bot" + telegramtoken + "/sendSticker", params=parametri)


def sendvideo(vid, to) -> None:
    """Manda un video .mp4 a una chat.
    :param vid: ID del video
    :param to: Destinatario del video
    """
    parametri = {
        'chat_id': to,
        'video': vid,
    }
    # Manda la richiesta ai server di Telegram.
    requests.get("https://api.telegram.org/bot" + telegramtoken + "/sendVideo", params=parametri)


def sendvoice(aud, to) -> None:
    """Manda un file audio .ogg con OPUS a una chat come se fosse un messaggio vocale.
    :param aud: ID dell'audio
    :param to: Destinatario dell'audio
    """
    parametri = {
        'chat_id': to,
        'voice': aud,
    }
    # Manda la richiesta ai server di Telegram.
    requests.get("https://api.telegram.org/bot" + telegramtoken + "/sendVoice", params=parametri)


def sendlocation(lat, long, to) -> None:
    """Manda una posizione sulla mappa.
    :param lat: Latitudine
    :param long: Longitudine
    :param to: Destinatario della posizione
    """
    # Parametri del messaggio
    parametri = {
        'chat_id': to,
        'latitude': lat,
        'longitude': long,
    }
    # Manda la richiesta ai server di Telegram.
    requests.get("https://api.telegram.org/bot" + telegramtoken + "/sendLocation", params=parametri)


def sendchataction(to, action='typing') -> None:
    """Visualizza lo stato "sta scrivendo" del bot.
    :param to: Chat in cui visualizzare lo stato
    :param action: Tipo di stato da visualizzare
    """
    # Parametri del messaggio
    parametri = {
        'chat_id': to,
        'action': action,
    }
    # Manda la richiesta ai server di Telegram.
    requests.get("https://api.telegram.org/bot" + telegramtoken + "/sendChatAction", params=parametri)
