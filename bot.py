import datetime
import ephem

import settings

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

def greet_user(bot, update):
    text = 'Вызван /start'
    print(text)
    update.message.reply_text(text)

def wordcount(bot, update):
    user_text = update.message.text
    print(user_text)

    replacements = ',.!?:;"()<>[]#$=-/'
    for r in replacements:
        user_text = user_text.replace(r, ' ')
    words = user_text.split()
    del words[0]
    if words == []:
        text = 'Нечего считать'
    else:
        text = f'Количество слов: {len(words)}'
    update.message.reply_text(text)

def next_full_moon(bot,update, args):
    if args == []:
        curr_date = datetime.datetime.now()
        print(type(curr_date))
        text = ephem.next_full_moon(curr_date)
    else:
        try:
            args = args[0]+' 08:00:00'
            text = ephem.next_full_moon(args)
        except:
            print ('Неизвестный формат даты, укажите гггг/мм/дд')
    
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


#######################################################
#  ИГРА В ГОРОДА - явно куча лишнего кода и всё неоптимально
new_city_list = ['Москва', 'Астрахань', 'Казань', 'Нальчик'] # не нашёл нормальный список городов
city_list = new_city_list.copy()
last_letter = ''

def cities (bot, update, args):  
    global new_city_list
    global city_list
    global last_letter

    print('new', new_city_list)
    print('1',city_list)
   
    if args[0] == 'reset':
        city_list = new_city_list
        last_letter = ''
        update.message.reply_text('city list reset')
        return

    city = args[0].capitalize()

    if (city[0] == last_letter.capitalize()) or (last_letter == ''):
        try: # пробует удалить город из списка
            city_list.remove(city)
        except:
            update.message.reply_text('нет такого города или уже называли')
            return
    else:
        update.message.reply_text('Слово должно начинаться на букву '+ last_letter.capitalize() + ', а не ' + city[0])
        return

    print('2',city_list)
    print('new2', new_city_list)

    if city[-1] == 'ь':
        user_last_letter = city[-2].capitalize()
    else:
        user_last_letter = city[-1].capitalize()

    for city_chk in city_list:
        if city_chk[0] == user_last_letter:
            city_list.remove(city_chk)
            
            last_letter = city_chk[-1]
            if last_letter == 'ь':
                last_letter = city_chk[-2]
            print('3',city_list)
            update.message.reply_text(city_chk+', вам на букву '+last_letter)
            return
    
    update.message.reply_text('Вы победили')
    city_list = new_city_list
    last_letter = ''
    print('4', city_list)
    
########################################################


def main():
    mybot = Updater(settings.API_KEY, request_kwargs=settings.PROXY)
    
    dp = mybot.dispatcher
    dp.add_handler(CommandHandler('start', greet_user))
    dp.add_handler(CommandHandler('planet', planet_chk, pass_args=True)) # вытягивание аргумента
    dp.add_handler(CommandHandler('wordcount', wordcount))
    dp.add_handler(CommandHandler('next_full_moon', next_full_moon, pass_args=True))
    dp.add_handler(CommandHandler('cities', cities, pass_args=True))

    dp.add_handler(MessageHandler(Filters.text, talk_to_me)) # этого нет в задании
    
    mybot.start_polling()
    mybot.idle()

main()