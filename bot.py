import logging

from telegram.ext import CommandHandler, ConversationHandler, Filters, MessageHandler, \
    RegexHandler, Updater, CallbackQueryHandler
from telegram.ext import messagequeue as mq

from handlers import * # импотирует лишнее
import settings


logging.basicConfig(format='%(name)s - %(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    handlers=[logging.FileHandler('bot.log', 'w', 'utf-8')]
                    )


#######################################################
#  ИГРА В ГОРОДА - явно куча лишнего кода и всё неоптимально
new_city_list=[]
with open('cities.csv', 'r', encoding='utf-8') as f:
    new_city_list = f.read()
    new_city_list = new_city_list.split(';')

city_list = new_city_list.copy()
last_letter = ''

def cities (bot, update, args):  

    global city_list
    global last_letter

    print('new', new_city_list[:20])
    print('1',city_list[:20])
   
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
        update.message.reply_text('Слово должно начинаться на букву '+ last_letter.capitalize() 
                                    + ', а не ' + city[0])
        return

    print('2',city_list[:20])
    print('new2', new_city_list[:20])

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
            print('3',city_list[:20])
            update.message.reply_text(city_chk+', вам на букву '+last_letter.capitalize())
            return
    
    update.message.reply_text('Вы победили')
    city_list = new_city_list
    last_letter = ''
    print('4', city_list[:20])
    
########################################################


subscribers = set()


def my_test(bot, job):
    print("Test", job.interval)
    bot.sendMessage(chat_id=478005391, text="Spam_bot!")
    job.interval += 5
    if job.interval > 15:
        bot.sendMessage(chat_id=478005391, text="Пока!")
        job.schedule_removal() # удаляет задачу из очереди задач


def main():
    mybot = Updater(settings.API_KEY, request_kwargs=settings.PROXY)
    mybot.bot._msg_queue = mq.MessageQueue()
    mybot.bot._is_messages_queued_default = True
    
    logging.info('Старт бота')  

    dp = mybot.dispatcher

    mybot.job_queue.run_repeating(my_test, interval=5)
    mybot.job_queue.run_repeating(send_updates, interval=5)

    anketa = ConversationHandler(
        entry_points=[RegexHandler('^(Заполнить анкету)$', anketa_start, pass_user_data=True)],
        states={
            "name": [MessageHandler(Filters.text, anketa_get_name, pass_user_data=True)],
            "rating": [RegexHandler('^(1|2|3|4|5)$', anketa_rating, pass_user_data=True)],
            "comment": [MessageHandler(Filters.text, anketa_comment, pass_user_data=True),
                        CommandHandler('cancel', anketa_skip_comment, pass_user_data=True)]
        },
        fallbacks=[MessageHandler(
            Filters.text | Filters.video | Filters.photo | Filters.document,
            dontknow,
            pass_user_data=True
        )]
    )
        
    dp.add_handler(CommandHandler('start', greet_user, pass_user_data=True))

    dp.add_handler(anketa)    

    dp.add_handler(CommandHandler('planet', planet_chk, pass_args=True)) # вытягивание аргумента
    dp.add_handler(CommandHandler('wordcount', wordcount))
    dp.add_handler(CommandHandler('next_full_moon', next_full_moon, pass_args=True))
    dp.add_handler(CommandHandler('cities', cities, pass_args=True))
    dp.add_handler(CommandHandler('cat', send_cat_picture, pass_user_data=True))
    dp.add_handler(RegexHandler('^(Хочу кота!)$', send_cat_picture, pass_user_data=True))
    dp.add_handler(RegexHandler('^(Сменить аву)$', change_avatar, pass_user_data=True))
    dp.add_handler(CallbackQueryHandler(inline_button_pressed))    
    dp.add_handler(MessageHandler(Filters.contact, get_contact, pass_user_data=True))
    dp.add_handler(MessageHandler(Filters.location, get_location, pass_user_data=True))
    dp.add_handler(MessageHandler(Filters.photo, check_user_photo, pass_user_data=True))

    dp.add_handler(CommandHandler("subscribe", subscribe))
    dp.add_handler(CommandHandler("unsubscribe", unsubscribe))

    dp.add_handler(CommandHandler("alarm", set_alarm, pass_args=True, pass_job_queue=True))

    dp.add_handler(MessageHandler(Filters.text, talk_to_me, pass_user_data=True)) # этого нет в задании
    
    mybot.start_polling()
    mybot.idle()

if __name__ == "__main__":
    main()