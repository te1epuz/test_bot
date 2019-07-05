from clarifai.rest import ClarifaiApp
from telegram import ReplyKeyboardMarkup, KeyboardButton

import settings


def get_keyboard():
    contact_button = KeyboardButton('Прислать контакт', request_contact=True)
    location_button = KeyboardButton('Прислать координаты', request_location=True)
    my_keyboard = ReplyKeyboardMarkup([
                                        ['Хочу кота!', 'Сменить аву'],
                                        [contact_button, location_button],
                                        ['Заполнить анкету']
                                       ], resize_keyboard=True
                                      )
    return my_keyboard


def is_cat(file_name):
    image_has_cat = False
    app = ClarifaiApp(api_key=settings.CLARIFAI_API_KEY)
    model = app.public_models.general_model
    response = model.predict_by_filename(file_name, max_concepts=5)
    #import pprint # временный импорт внутри кода, чтобы удобно просмотреть большой список 
    #pp = pprint.PrettyPrinter(indent=4)
    #pp.pprint(response)
    if response['status']['code'] == 10000:
        for concept in response['outputs'][0]['data']['concepts']:
            if concept['name'] == 'cat':
                image_has_cat = True
    return image_has_cat


if __name__ == "__main__":
    print(is_cat('images/cat (1).jpg'))