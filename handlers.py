import datetime
from glob import glob
import logging
import os
from random import choice

import ephem
from telegram import ParseMode, ReplyKeyboardRemove, ReplyKeyboardMarkup
from telegram.ext import ConversationHandler
from telegram.ext import messagequeue as mq


from bot import subscribers
from db import db, get_or_create_user, get_user_emo, toggle_subscription, get_subscribers
from utils import  get_keyboard, is_cat
import settings


def greet_user(bot, update, user_data):
    user = get_or_create_user(db, update.effective_user, update.message)
    emo = get_user_emo(db, user)
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
    user = get_or_create_user(db, update.effective_user, update.message)
    if 'emo' in user:
        del user['emo']
    emo = get_user_emo (db, user)
    text = 'Новая аватарка -> {}'.format(emo)
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
    
 #   if planet == 'Mars':
 #       planet_date = ephem.Mars(curr_date)
 #   if planet == 'Uranus':
 #       planet_date = ephem.Uranus(curr_date)
 #   if planet == 'Neptune':
 #       planet_date = ephem.Neptune(curr_date)
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
    user = get_or_create_user(db, update.effective_user, update.message)
    emo = get_user_emo(db, user)
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

def anketa_start(bot, update, user_data):
    update.message.reply_text("Как вас зовут? Напишите имя и фамилию", reply_markup=ReplyKeyboardRemove())
    return "name"

def anketa_get_name(bot, update, user_data):
    user_name = update.message.text
    if len(user_name.split(' ')) != 2:
        update.message.reply_text('Введите имя и фамилию')
        return 'name'
    else:
        user_data['anketa_name'] = user_name
        reply_keyboard = [['1', '2', '3', '4', '5']]

        update.message.reply_text(
            'Оцените бота по шкале от 1 до 5',
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
        )
        return 'rating'

def anketa_rating(bot, update, user_data):
    user_data['anketa_rating'] = update.message.text
    update.message.reply_text('''Пожалуйста, напишите отзыв в свободной форме
или /cancel чтобы пропустить этот шаг''')
    return 'comment'

def anketa_comment(bot, update, user_data):
    user_data["anketa_comment"] = update.message.text
    user_text = """
<b>Имя Фамилия:</b> {anketa_name}
<b>Оценка:</b> {anketa_rating}
<b>Комментарий:</b> {anketa_comment}""".format(**user_data)
    update.message.reply_text(user_text, reply_markup=get_keyboard(), parse_mode=ParseMode.HTML)
    return ConversationHandler.END

def anketa_skip_comment(bot, update, user_data):
    user_text = """
<b>Имя Фамилия:</b> {anketa_name}
<b>Оценка:</b> {anketa_rating}""".format(**user_data)
    update.message.reply_text(user_text, reply_markup=get_keyboard(), parse_mode=ParseMode.HTML)
    return ConversationHandler.END

def dontknow(bot, update, user_data):
    update.message.reply_text('Не понимаю')

def subscribe(bot, update):
    user = get_or_create_user(db, update.effective_user, update.message)
    if not user.get('subscribed'):
        toggle_subscription(db, user)
    update.message.reply_text('Вы подписались, наберите /unsubscribe чтобы отписаться')

def unsubscribe(bot, update):
    user = get_or_create_user(db, update.effective_user, update.message)
    if user.get('subscribed'):
        toggle_subscription(db, user)
        update.message.reply_text("Вы отписались")
    else:
        update.message.reply_text("Вы не подписаны, нажмите /subscribe чтобы подписаться")

@mq.queuedmessage
def send_updates(bot, job):
    for user in get_subscribers(db):
        try:
            bot.sendMessage(chat_id=user['chat_id'], text="BUZZZ!")
        except error.BadRequest:
            print('Chat {} not found'.format(user['chat_id']))

def set_alarm(bot, update, args, job_queue):
    try:
        seconds = abs(int(args[0]))
        job_queue.run_once(alarm, seconds, context=update.message.chat_id)
    except (IndexError, ValueError):
        update.message.reply_text("Введите число секунд после команды /alarm")

@mq.queuedmessage
def alarm(bot, job):
    bot.send_message(chat_id=job.context, text="Сработал будильник!")