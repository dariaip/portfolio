# -*- coding: utf-8 -*-
#import libraries
import config
import utils
import telebot
from telebot import types
import pandas as pd
import numpy as np
from datetime import datetime
import datetime as dtm
import time as time_module

#create a bot
bot = telebot.TeleBot(config.token)

#start counter to escape a mistake with activating the bot several times
a = 0
#the bot could be activated by any text message
@bot.message_handler(content_types=["text"])
def saving_text(message):
    #if the text is '/start' the bot will check whether the user used the bot before and saved a list of activity types
    if message.text == '/start':
        active = pd.read_csv('activities.csv', sep=',', index_col=0)
        active_user = active.activity[active.user_id == message.from_user.id]
        #if the user didn't use it will offer to create such a list and will transfer the answer to an "activities_next_empty" function
        if len(active_user) == 0:
            bot.send_message(message.chat.id, 'Before we start, type the main aspects of your life one by one. When you finish, type "Done". Further you are going to classify your actions by these categories. Thank you!')
            bot.register_next_step_handler(message, activities_next_empty)
        #but if the user did it will show previously saved list and offer to change it. The answer will be transfered to an "activities_next_full" function
        else:
            bot.send_message(message.chat.id, 'These are you activities. If you want to delete some of them, type "Delete <title>". If you want to add new activities, type "Add <title>". Type only one title in line. You can change your list untill you type "Done". If you do not want to change anything, type "Done" as well.')
            bot.send_message(message.chat.id, '\n'.join(list(active_user.values)))
            bot.register_next_step_handler(message, activities_next_full)
    #if the user sent 'start'/'Start'/'START'/etc. the process of sending regular messages to the user will launch
    elif message.text.lower() == 'start':
        bot.send_message(message.chat.id, 'Good choice! You will get push-messages asking you about your actions and energy levels. Please, follow the instructions.')
        #the bot should know that the bot is working for the user, so a should be bigger than 0.
        global a
        a += 1
        #if it has already launched the user will get a message about the mistake
        if a > 1:
            bot.send_message(message.chat.id, 'Process was started several times. Please, type "Stop" and "Start" again. Thank you!')
        #but if it didn't work till now it will ask the user about his/her recent activities every 30 minutes and process the answers by an "appropriate_time" function
        while a == 1:
            if (datetime.now().minute == 0) and (datetime.now().second == 0) and (datetime.now().microsecond <= 999999):
                bot.send_message(message.chat.id, 'What did you do last 30 minutes? If you want to stop tracking, type "Stop".')
                bot.register_next_step_handler(message, appropriate_time)
                #it's needed because the bot processes the answer quicker then 1 sec and otherwise can send the same question just after handling the previous answer
                time_module.sleep(1)
            elif (datetime.now().minute == 30) and (datetime.now().second == 0) and (datetime.now().microsecond <= 999999):
                bot.send_message(message.chat.id, 'What did you do last 30 minutes? If you want to stop tracking, type "Stop".')
                bot.register_next_step_handler(message, appropriate_time)
                time_module.sleep(1)
            #at 0:05 a.m. the bot collects statistics about the previous day and send it to the user. If the bot didn't register answers for some periods of time it will refer them to "Other" category
            elif (datetime.now().hour == 0) and (datetime.now().minute == 5) and (datetime.now().second == 0):
                data_prev = pd.read_csv('doing_energy.csv', sep=';', index_col = 0)
                timing = dtm.date.today()-dtm.timedelta(1)
                data_day = data_prev[data_prev.year == timing.year][data_prev.month == timing.month][data_prev.day == timing.day]
                time_distr = data_day.category.value_counts()/48*100
                time_distr_ind = time_distr.index.tolist()
                time_distr = map(lambda x: round(x, 1), time_distr)
                if 'Other' not in time_distr_ind:
                    time_distr_ind.append('Other')
                    time_distr.append(round(100 - np.sum(time_distr), 1))
                else:
                    ind = time_distr_ind.index('Other')
                    time_distr[ind] = time_distr[ind] + time_distr.append(round(100 - np.sum(time_distr), 1))
                hours_distr = map(lambda x: round(x*48/100, 1)*0.5, time_distr)
                to_show = ''
                for i in range(len(time_distr_ind)):
                    to_show = to_show + str(time_distr_ind[i]) + ': ' + str(time_distr[i]) + '% or ' + str(hours_distr[i]) + ' hours' + '\n'
                to_show = to_show + '\nTotal amount of working hours: ' + str(list(data_prev.category).count('Working')/2) + '\n'
                energy_level = np.mean(map(lambda x: int(x), data_day.energy[data_day.energy != 'Empty'].values))
                to_show = to_show + '\nAverage energy level: ' + str(round(energy_level, 2)) + ' from 10'
                bot.send_message(message.chat.id, to_show)
                time_module.sleep(1)
            else:
                time_module.sleep(1)
    #if the user type 'stop' he/she wants to stop getting messages. So the user will get a message and the counter will become equal to 0 (it leads to stopping of messages' flow)
    elif message.text.lower() == 'stop':
        bot.send_message(message.chat.id, 'Thank you for talking to me. To restart tracking you can type "Start" at any time. Bye!')
        a = 0

def activities_next_full(message):
    #open a file to write down activities
    data_prev = pd.read_csv('activities.csv', index_col = 0)
    text_split_space = message.text.split(' ', 1)
    
    #if the user typed 'done' the process of changing activities' list is over
    if message.text.lower() == 'done':
        bot.send_message(message.chat.id, 'To start tracking, type "Start".')
    #if the user wrote "add" at the beginning of his/her message the second part of it should be saved to the file
    elif text_split_space[0].lower() == 'add':
        activities_list = []
        user_id = message.from_user.id
        activities_list.append([user_id, text_split_space[1]])
        activities = pd.DataFrame(activities_list, columns = ['user_id', 'activity'])
        data_new = np.vstack((data_prev, activities))
        data_new = pd.DataFrame(data_new, columns = ['user_id', 'activity'])
        data_new.to_csv('activities.csv')
        #the user will have the opportunity to add one more activity after saving the previous one
        bot.register_next_step_handler(message, activities_next_full)
    #if the user wrote "delete" at the beginning of his/her message the second part of it should be deleted from the file
    elif text_split_space[0].lower() == 'delete':
        data_prev.drop(data_prev[data_prev.user_id == message.from_user.id][data_prev.activity == text_split_space[1]].index, 
                       axis = 0, inplace = True)
        data_prev.to_csv('activities.csv')
        #the user will have the opportunity to change activities' list after that
        bot.register_next_step_handler(message, activities_next_full)
    #if the message doesn't start with "done", "add" or "delete" the user will get a message about a mistake
    else:
        bot.send_message(message.chat.id, 'It is something wrong with your text. Try again.')          
        #and the user will be able to try again
        bot.register_next_step_handler(message, activities_next_full)

def activities_next_empty(message):
    #the user should write down titles of his/her regular activities one by one and all messages will be saved to an activities' list until a "done" message
    if message.text.lower() != 'done':
        activities_list = []
        user_id = message.from_user.id
        activities_list.append([user_id, message.text])
        activities = pd.DataFrame(activities_list, columns = ['user_id', 'activity'])
        data_prev = pd.read_csv('activities.csv', index_col = 0)
        data_new = np.vstack((data_prev, activities))
        data_new = pd.DataFrame(data_new, columns = ['user_id', 'activity'])
        data_new.to_csv('activities.csv')
        bot.register_next_step_handler(message, activities_next_empty)
    else:
        bot.send_message(message.chat.id, 'To start tracking, type "Start".')                

def appropriate_time(message):
    #if the user type 'stop' he/she wants to stop getting messages. So the counter will become equal to 0 (it leads to stopping of messages' flow)
    if message.text.lower() == 'stop':
        bot.send_message(message.chat.id, 'Thank you for talking to me. To restart tracking you can type "Start" at any time. Bye!')
        global a
        a = 0
    #all other messages will be interpreted as action's descriptions. After getting it the bot will offer the user to refer it to one of the activities from the earier created activities' list
    else:
        #open activities' list
        data_prev = pd.read_csv('activities.csv', index_col = 0)
        data = data_prev.activity[data_prev.user_id == message.from_user.id]
        keys = list(data.values)
        nums = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
        #check whether the message is just a repetition of activity title or a number
        i = 0
        for key in keys:
            if (message.text == key) or (message.text == nums):
                i = i+1
        #if it isn't and the list of activities contains at list one line then offer the user to refer the message to one of the saved activities
        if (len(data) != 0) and (i == 0):
            global text_fo_saving
            text_fo_saving = message.text
            markup = utils.generate_markup(keys)
            bot.send_message(message.chat.id, 'Choose the main activity, related to this action.', reply_markup=markup)
            bot.register_next_step_handler(message, choose_activity)
        #if it isn't but the list of activities is empty then save the message an go to energy level estimation
        elif (len(data) == 0) and (i == 0):
            user_id = message.from_user.id
            user_name = message.from_user.username
            message_time = message.date
            time = datetime.now()
            text = message.text
            category = 'Empty'
            energy = 'Empty'
            data = []
            data.append([user_id, user_name, message_time, time.year, time.month, time.day, time.hour, time.minute, time.second, text, category, energy])
            output = pd.DataFrame(data, columns = ['user_id', 'user_name', 'message_time', 'year', 'month', 'day', 'hour', 'minute', 'second', 'text', 'category', 'energy'])
            data_prev = pd.read_csv('doing_energy.csv', sep=';', index_col = 0)
            data_new = np.vstack((data_prev, output))
            data_new = pd.DataFrame(data_new, columns = ['user_id', 'user_name', 'message_time', 'year', 'month', 'day', 'hour', 'minute', 'second', 'text', 'category', 'energy'])
            data_new.to_csv('doing_energy.csv', sep=';')
            keys = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
            markup_energy = utils.generate_markup(keys)
            bot.send_message(message.chat.id, 'Your text is saved. How do you estimate your evergy level for the previous 30 minutes?', reply_markup=markup)
            bot.register_next_step_handler(message, save_energy)
        #but if it isn't, do nothing

#the function lets to save gotten information about a recent action and reffered activity (and at the end it offers to extimate a recent energy level) 
def choose_activity(message):
    user_id = message.from_user.id
    user_name = message.from_user.username
    message_time = message.date
    time = datetime.now()
    text = text_fo_saving
    category = message.text
    energy = 'Empty'
    data = []
    data.append([user_id, user_name, message_time, time.year, time.month, time.day, time.hour, time.minute, time.second, text, category, energy])
    output = pd.DataFrame(data, columns = ['user_id', 'user_name', 'message_time', 'year', 'month', 'day', 'hour', 'minute', 'second', 'text', 'category', 'energy'])
    data_prev = pd.read_csv('doing_energy.csv', sep=';', index_col = 0)
    data_new = np.vstack((data_prev, output))
    data_new = pd.DataFrame(data_new, columns = ['user_id', 'user_name', 'message_time', 'year', 'month', 'day', 'hour', 'minute', 'second', 'text', 'category', 'energy'])
    data_new.to_csv('doing_energy.csv', sep=';')
    keys = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
    markup_energy = utils.generate_markup(keys)
    bot.send_message(message.chat.id, 'Your text is saved. How do you estimate your evergy level for the previous 30 minutes?', reply_markup=markup_energy)
    bot.register_next_step_handler(message, save_energy)

#the function saves chosen energy level
def save_energy(message):
    data_import = pd.read_csv('doing_energy.csv', sep=';', index_col = 0)
    data_import.loc[len(data_import)-1, 'energy'] = str(message.text)
    data_import.to_csv('doing_energy.csv', sep=';')
    bot.send_message(message.chat.id, 'Your text is saved.')

#the launched bot is always ready to respond, and if something happens with connections it sleeps for a second and continues to work then
if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print e
            time_module.sleep(1)