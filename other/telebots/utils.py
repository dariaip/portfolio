# -*- coding: utf-8 -*-
from telebot import types

def generate_markup(list_of_elements):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for item in list_of_elements:
        markup.add(item)
    return markup