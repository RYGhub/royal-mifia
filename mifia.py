import telegram
import filemanager

token = filemanager.readfile('telegramapi.txt')
bot = telegram.Bot(token)
