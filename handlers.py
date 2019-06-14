import datetime
from glob import glob
import logging
import os
from random import choice
from utils import get_user_emo, get_keyboard, is_cat

import ephem

import settings


def greet_user(bot, update, user_data):
    emo = get_user_emo(user_data)
    text = 'Привет, {} {}'.format(update.message.chat.first_name, emo)
    update.message.reply_text(text, reply_markup=get_keyboard())
    logging.info('{}({}): /start'.format(update.message.chat.username, update.message.chat.first_name))


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


def send_cat_picture(bot, update, user_data):
    cat_list = glob('images/cat*.jpg')
    cat_pic = choice(cat_list)
    bot.send_photo(chat_id=update.message.chat_id, photo=open(cat_pic, 'rb'), reply_markup=get_keyboard())
    logging.info('{}({}): /cat'.format(update.message.chat.username, update.message.chat.first_name))


def change_avatar(bot, update, user_data):
    if 'emo' in user_data:
        del user_data['emo']
    user_data['emo'] = get_user_emo(user_data)
    text = 'Новая аватарка -> {}'.format(user_data['emo'])
    update.message.reply_text(text, reply_markup=get_keyboard())
    logging.info('{}({}): avatar changed'.format(update.message.chat.username, update.message.chat.first_name))


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
    
    # planet_date = getattr(ephem, planet)(curr_date) #вот так можно без кучи ифов - нужно разобраться
    # planet_date = planet_date(curr_date) # или так

    try:
        const = ephem.constellation(planet_date)
        print (const)
        update.message.reply_text(f'{planet} is in {const} position') 
    except:
        print ('Неизвестная планета :(')
        update.message.reply_text('Неизвестная планета :(')    


def talk_to_me(bot, update, user_data):
    emo = get_user_emo(user_data)
    user_text = update.message.text
    text = f'{emo} {user_text}'
    update.message.reply_text(text, reply_markup=get_keyboard())
    logging.info('{}({}): wrote smth'.format(update.message.chat.username, update.message.chat.first_name))


def get_contact(bot, update, user_data):
    logging.info('{}({}): contact - {}'.format(update.message.chat.username, update.message.chat.first_name, 
                                                update.message.contact))
 

def get_location(bot, update, user_data):
    logging.info('{}({}): location - {}'.format(update.message.chat.username, update.message.chat.first_name,
                                                update.message.location))


def check_user_photo(bot, update, user_data):
    update.message.reply_text("Обрабатываю фото...")
    os.makedirs('downloads', exist_ok=True) # создает папку и не выдает ошибку, если она уже есть
    photo_file = bot.getFile(update.message.photo[-1].file_id)
    filename = os.path.join('downloads', '{}.jpg'.format(photo_file.file_id))
    photo_file.download(filename)
    if is_cat(filename):
        update.message.reply_text("Обнаружен котик, добавляю в библиотеку.")
        new_filename = os.path.join('images', 'cat_{}.jpg'.format(photo_file.file_id))
        os.rename(filename, new_filename) # перемещает в новое место, а не переименовывает!
        logging.info('{}({}): new cat uploaded to images'.format(update.message.chat.username, update.message.chat.first_name))
    else:
        os.remove(filename)
        update.message.reply_text("Кот не обнаружен.")
        logging.info('{}({}): non-cat image recieved - no action'.format(update.message.chat.username, update.message.chat.first_name))