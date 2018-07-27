# -*- coding: utf-8 -*-
#import libraries
import config
import utils
import telebot
import openpyxl
import pandas as pd

#creat a bot
bot = telebot.TeleBot(config.token)

#upload a tree of questions/reactions from a MS Excel file (depth = 4 levels)
data = openpyxl.load_workbook(filename = 'tree.xlsx')
sheet = data['tree']
transfer = sheet.values
df = pd.DataFrame(transfer)
df.columns = df.ix[0,:]
df.drop([0], inplace = True)

#bot's reaction on /start and /help commands
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    #returns a text from the tree
    bot.send_message(message.chat.id, df.Start)

#this and further decorators describe bot's reactions on chosen commands (we have 4 options that's why there are 4 decorators)
@bot.message_handler(commands=[u'{}'.format(list(set(df.Options1[df.Options1.isnull() == False]))[0])], content_types=["text"])
def answer11(message):
    #gotten command as text without '/'
    global var_answer11
    var_answer11 = message.text.split('/')[1]
    #return next options to choose as a list of buttons (a specific keybouard)
    keys = list(set(df.Options2[df.Options1 == var_answer11][df.Question2.isnull() == False]))
    markup = utils.generate_markup(keys)
    bot.send_message(message.chat.id, df.Question1[df.Options1 == var_answer11], reply_markup=markup)
    #swich the user's reaction to 'answer12' function
    bot.register_next_step_handler(message, answer12)

def answer12(message):
    global var_answer12
    var_answer12 = message.text
    #check whether there is further layer of options or this is an end of a branch
    part = list(set(df.Options2[df.Options1 == var_answer11][df.Question2.isnull() == False]))
    #if it isn't the end then display next options and transfer the reaction to the 'answer13' function
    if len(part) != 0:
        keys = list(set(df.Options3[df.Options1 == var_answer11][df.Options2 == var_answer12][df.Question3.isnull() == False]))
        markup = utils.generate_markup(keys)
        bot.send_message(message.chat.id, df.Question2[df.Options1 == var_answer11][df.Options2 == var_answer12], reply_markup=markup)
        if len(list(set(df.Options3[df.Options1 == var_answer11][df.Options2 == var_answer12][df.Question3.isnull() == False]))) != 0:
            bot.register_next_step_handler(message, answer13)

#the same logic as for the 'answer12' function
def answer13(message):
    global var_answer13
    var_answer13 = message.text
    part = list(set(df.Options3[df.Options1 == var_answer11][df.Options2 == var_answer12][df.Question3.isnull() == False]))
    if len(part) != 0:
        keys = list(set(df.Options4[df.Options1 == var_answer11][df.Options2 == var_answer12][df.Options3 == var_answer13][df.Question4.isnull() == False]))
        markup = utils.generate_markup(keys)
        bot.send_message(message.chat.id, df.Question3[df.Options1 == var_answer11][df.Options2 == var_answer12][df.Options3 == var_answer13], reply_markup=markup)
        if len(list(set(df.Options4[df.Options1 == var_answer11][df.Options2 == var_answer12][df.Options3 == var_answer13][df.Question4.isnull() == False]))) != 0:
            bot.register_next_step_handler(message, answer14)
        
def answer14(message):
    global var_answer14
    var_answer14 = message.text
    part = list(set(df.Options4[df.Options1 == var_answer11][df.Options2 == var_answer12][df.Options3 == var_answer13][df.Question4.isnull() == False]))
    #check that there is an answer for the chosen option
    if (len(part) != 0) and (var_answer14 in part):
        bot.send_message(message.chat.id, df.Question4[df.Options1 == var_answer11][df.Options2 == var_answer12][df.Options3 == var_answer13][df.Options4 == var_answer14])

#the same logic as for the previous decorator and block of functions
@bot.message_handler(commands=[u'{}'.format(list(set(df.Options1[df.Options1.isnull() == False]))[1])], content_types=["text"])
def answer21(message):
    global var_answer21
    var_answer21 = message.text.split('/')[1]
    keys = list(set(df.Options2[df.Options1 == var_answer21][df.Question2.isnull() == False]))
    markup = utils.generate_markup(keys)
    bot.send_message(message.chat.id, df.Question1[df.Options1 == var_answer21], reply_markup=markup)
    bot.register_next_step_handler(message, answer22)

def answer22(message):
    global var_answer22
    var_answer22 = message.text
    part = list(set(df.Options2[df.Options1 == var_answer21][df.Question2.isnull() == False]))
    if len(part) != 0:
        if var_answer22 in part:
            keys = list(set(df.Options3[df.Options1 == var_answer21][df.Options2 == var_answer22][df.Question3.isnull() == False]))
            markup = utils.generate_markup(keys)
            bot.send_message(message.chat.id, df.Question2[df.Options1 == var_answer21][df.Options2 == var_answer22], reply_markup=markup)
            if len(list(set(df.Options3[df.Options1 == var_answer21][df.Options2 == var_answer22][df.Question3.isnull() == False]))) != 0:
                bot.register_next_step_handler(message, answer23)
                
def answer23(message):
    global var_answer23
    var_answer23 = message.text
    part = list(set(df.Options3[df.Options1 == var_answer21][df.Options2 == var_answer22][df.Question3.isnull() == False]))
    if len(part) != 0:
        if var_answer23 in part:
            keys = list(set(df.Options4[df.Options1 == var_answer21][df.Options2 == var_answer22][df.Options3 == var_answer23][df.Question4.isnull() == False]))
            markup = utils.generate_markup(keys)
            bot.send_message(message.chat.id, df.Question3[df.Options1 == var_answer21][df.Options2 == var_answer22][df.Options3 == var_answer23], reply_markup=markup)
            if len(list(set(df.Options4[df.Options1 == var_answer21][df.Options2 == var_answer22][df.Options3 == var_answer23][df.Question4.isnull() == False]))) != 0:
                bot.register_next_step_handler(message, answer24)
    
def answer24(message):
    global var_answer24
    var_answer24 = message.text
    part = list(set(df.Options4[df.Options1 == var_answer21][df.Options2 == var_answer22][df.Options3 == var_answer23][df.Question4.isnull() == False]))
    if (len(part) != 0) and (var_answer24 in part):
        bot.send_message(message.chat.id, df.Question4[df.Options1 == var_answer21][df.Options2 == var_answer22][df.Options3 == var_answer23][df.Options4 == var_answer24])

@bot.message_handler(commands=[u'{}'.format(list(set(df.Options1[df.Options1.isnull() == False]))[2])], content_types=["text"])
def answer31(message):
    global var_answer31
    var_answer31 = message.text.split('/')[1]
    keys = list(set(df.Options2[df.Options1 == var_answer31][df.Question2.isnull() == False]))
    markup = utils.generate_markup(keys)
    bot.send_message(message.chat.id, df.Question1[df.Options1 == var_answer31], reply_markup=markup)
    bot.register_next_step_handler(message, answer32)

def answer32(message):
    global var_answer32
    var_answer32 = message.text
    part = list(set(df.Options2[df.Options1 == var_answer31][df.Question2.isnull() == False]))
    if len(part) != 0:
        if var_answer32 in part:
            keys = list(set(df.Options3[df.Options1 == var_answer31][df.Options2 == var_answer32][df.Question3.isnull() == False]))
            markup = utils.generate_markup(keys)
            bot.send_message(message.chat.id, df.Question2[df.Options1 == var_answer31][df.Options2 == var_answer32], reply_markup=markup)
            if len(list(set(df.Options3[df.Options1 == var_answer31][df.Options2 == var_answer32][df.Question3.isnull() == False]))) != 0:
                bot.register_next_step_handler(message, answer33)
                
def answer33(message):
    global var_answer33
    var_answer33 = message.text
    part = list(set(df.Options3[df.Options1 == var_answer31][df.Options2 == var_answer32][df.Question3.isnull() == False]))
    if len(part) != 0:
        if var_answer33 in part:
            keys = list(set(df.Options4[df.Options1 == var_answer31][df.Options2 == var_answer32][df.Options3 == var_answer33][df.Question4.isnull() == False]))
            markup = utils.generate_markup(keys)
            bot.send_message(message.chat.id, df.Question3[df.Options1 == var_answer31][df.Options2 == var_answer32][df.Options3 == var_answer33], reply_markup=markup)
            if len(list(set(df.Options4[df.Options1 == var_answer31][df.Options2 == var_answer32][df.Options3 == var_answer33][df.Question4.isnull() == False]))) != 0:
                bot.register_next_step_handler(message, answer34)
    
def answer34(message):
    global var_answer34
    var_answer34 = message.text
    part = list(set(df.Options4[df.Options1 == var_answer31][df.Options2 == var_answer32][df.Options3 == var_answer33][df.Question4.isnull() == False]))
    if (len(part) != 0) and (var_answer34 in part):
        bot.send_message(message.chat.id, df.Question4[df.Options1 == var_answer31][df.Options2 == var_answer32][df.Options3 == var_answer33][df.Options4 == var_answer34])
        
@bot.message_handler(commands=[u'{}'.format(list(set(df.Options1[df.Options1.isnull() == False]))[3])], content_types=["text"])
def answer41(message):
    global var_answer41
    var_answer41 = message.text.split('/')[1]
    keys = list(set(df.Options2[df.Options1 == var_answer41][df.Question2.isnull() == False]))
    markup = utils.generate_markup(keys)
    bot.send_message(message.chat.id, df.Question1[df.Options1 == var_answer41], reply_markup=markup)
    bot.register_next_step_handler(message, answer42)

def answer42(message):
    global var_answer42
    var_answer42 = message.text
    part = list(set(df.Options2[df.Options1 == var_answer41][df.Question2.isnull() == False]))
    if len(part) != 0:
        if var_answer42 in part:
            keys = list(set(df.Options3[df.Options1 == var_answer41][df.Options2 == var_answer42][df.Question3.isnull() == False]))
            markup = utils.generate_markup(keys)
            bot.send_message(message.chat.id, df.Question2[df.Options1 == var_answer41][df.Options2 == var_answer42], reply_markup=markup)
            if len(list(set(df.Options3[df.Options1 == var_answer41][df.Options2 == var_answer42][df.Question3.isnull() == False]))) != 0:
                bot.register_next_step_handler(message, answer43)
                
def answer43(message):
    global var_answer43
    var_answer43 = message.text
    part = list(set(df.Options3[df.Options1 == var_answer41][df.Options2 == var_answer42][df.Question3.isnull() == False]))
    if len(part) != 0:
        if var_answer43 in part:
            keys = list(set(df.Options4[df.Options1 == var_answer41][df.Options2 == var_answer42][df.Options3 == var_answer43][df.Question4.isnull() == False]))
            markup = utils.generate_markup(keys)
            bot.send_message(message.chat.id, df.Question3[df.Options1 == var_answer41][df.Options2 == var_answer42][df.Options3 == var_answer43], reply_markup=markup)
            if len(list(set(df.Options4[df.Options1 == var_answer41][df.Options2 == var_answer42][df.Options3 == var_answer43][df.Question4.isnull() == False]))) != 0:
                bot.register_next_step_handler(message, answer44)
    
def answer44(message):
    global var_answer44
    var_answer44 = message.text
    part = list(set(df.Options4[df.Options1 == var_answer41][df.Options2 == var_answer42][df.Options3 == var_answer43][df.Question4.isnull() == False]))
    if (len(part) != 0) and (var_answer44 in part):
        bot.send_message(message.chat.id, df.Question4[df.Options1 == var_answer41][df.Options2 == var_answer42][df.Options3 == var_answer43][df.Options4 == var_answer44])

#the bot is always ready for responding
if __name__ == '__main__':
    bot.polling(none_stop=True)