from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import ephem
import datetime
import settings

def greet_user(bot, update):
    text = 'Вызван /start'
    print(text)
    update.message.reply_text(text)

def planet_chk(bot, update, args): # Вроооде бы проще через 1й аргумент

    user_text = update.message.text
    planet = user_text.split()[1].capitalize()
    # planet = args[0].capitalize() # Вот так через аргумент
    
    text = 'Checking planet '+ planet + '...'
    print(text)
    update.message.reply_text(text)

    curr_date = str(datetime.datetime.now()) # Вытянуть текущую дату

    if planet == 'Mars':
        planet_date = ephem.Mars(curr_date)
    if planet == 'Uranus':
        planet_date = ephem.Uranus(curr_date)
    if planet == 'Neptune':
        planet_date = ephem.Neptune(curr_date)
    if planet == 'Jupiter':
        planet_date = ephem.Jupiter(curr_date)

    try:
        const = ephem.constellation(planet_date)
        print (const)
        update.message.reply_text(f'{planet} is in {const} position') 
    except:
        print ('Неизвестная планета :(')
        update.message.reply_text('Неизвестная планета :(')    

def talk_to_me(bot, update): # этого нет в задании
    user_text = update.message.text # этого нет в задании
    update.message.reply_text(user_text) # этого нет в задании

def main():
    mybot = Updater(settings.API_KEY, request_kwargs=settings.PROXY)
    
    dp = mybot.dispatcher
    dp.add_handler(CommandHandler('start', greet_user))
    dp.add_handler(CommandHandler('planet', planet_chk, pass_args=True)) # вытягивание аргумента
    dp.add_handler(MessageHandler(Filters.text, talk_to_me)) # этого нет в задании

    mybot.start_polling()
    mybot.idle()

main()