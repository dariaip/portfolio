#import libraries
import mechanize
import time
from selenium import webdriver
import pandas as pd
from selenium.webdriver.common.keys import Keys
import calendar

#this approach is slow but appropriate in cases when the only way to get the information is to fill the form (to reproduce user's sequence of actions)

def get_flights_info(airport_from_code, airport_to_code, date_year, date_month, date_day, number_adults, number_children, number_babies, direction):
    #initialize a browser
    br = mechanize.Browser()
    br.set_handle_robots(False)
    br.set_handle_refresh(False)
    br.addheaders = [('User-agent', 'Chrome')]

    browser = webdriver.Chrome("\selenium\chromedriver.exe") #a local way to a driver
    browser.get('https://www.tickets.com/') #url is intentionally changed
    time.sleep(5) #pause for waiting of browser opening

    #change language
    elem = browser.find_element_by_xpath('//*[@id="languageDropDownButton"]').click() #find the element on the page and click on it
    time.sleep(2) #this time break and furthers are needed for browser's reactions on an action made just before it
    browser.find_element_by_xpath('//*[@id="language_option_en-GB"]').click()
    time.sleep(2)
    
    #choose one way ticket (direction)
    browser.find_element_by_xpath('//*[@id="radiosBuscador"]/div/div/fieldset[2]/label/span').click()
    
    #choose airport that you're going to travel from
    elem = browser.find_element_by_xpath('//*[@id="AvailabilitySearchInputSearchView_TextBoxMarketOrigin1"]').clear() #find the element on the page and clear it
    elem = browser.find_element_by_xpath('//*[@id="AvailabilitySearchInputSearchView_TextBoxMarketOrigin1"]') #pick the same element
    time.sleep(2)
    elem.send_keys(airport_from_code) #type an airport_from_code to the element
    time.sleep(2)
    elem.send_keys(Keys.TAB) #submit the value pushing Tab button
    
    #choose airport that you're going to travel to
    elem = browser.find_element_by_xpath('//*[@id="AvailabilitySearchInputSearchView_TextBoxMarketDestination1"]').clear()
    elem = browser.find_element_by_xpath('//*[@id="AvailabilitySearchInputSearchView_TextBoxMarketDestination1"]')
    time.sleep(2)
    elem.send_keys(airport_to_code)
    time.sleep(2)
    elem.send_keys(Keys.RETURN)
    
    #choose date of flight
    time.sleep(3)
    elem_month = browser.find_element_by_xpath('//*[@id="datePickerContainer"]/div[1]/div/div/span[1]').text #check the text on the element
    elem_year = browser.find_element_by_xpath('//*[@id="datePickerContainer"]/div[1]/div/div/span[2]').text
    while (elem_month != calendar.month_name[int(date_month)]) or (elem_year != date_year):
        browser.find_element_by_xpath('//*[@id="datePickerContainer"]/div[2]/div/div').click() #click on the element until numbers of month and year are correct
        time.sleep(2)
        elem_month = browser.find_element_by_xpath('//*[@id="datePickerContainer"]/div[1]/div/div/span[1]').text
        elem_year = browser.find_element_by_xpath('//*[@id="datePickerContainer"]/div[1]/div/div/span[2]').text
    #choose needed day
    mark = 0
    while mark == 0:
        try:
            browser.find_element_by_xpath('//td[contains(@data-month="'+str(int(date_month)-1)+'", @data-year="'+date_year+'")]/a/text()[contains(., "'+date_day+'")]/..').click()
            mark = 1
        #deal with exceptions (when you can't make +1 day and get a correct date)
        except:
            date_day = str(int(date_day) + 1)
            month_len = calendar.monthrange(int(date_year), int(date_month))
            if int(date_day) > month_len:
                date_day = str(int(date_day) - month_len)
                date_month = str(int(date_month) + 1)
                if int(date_month) > 12:
                    date_month = str(int(date_month) - 12)
                    date_year = str(int(date_year) + 1)
    time.sleep(1)
    
    #choose number of passengers
    #adults
    browser.find_element_by_xpath('//*[@id="DropDownListPassengerType_ADT_PLUS"]').click()
    time.sleep(1)
    elem = browser.find_element_by_xpath('//*[@id="adtSelectorDropdown"]/option['+str(number_adults+1)+']').click()
    #children
    browser.find_element_by_xpath('//*[@id="AvailabilitySearchInputSearchView_DropDownListPassengerType_CHD"]').click()
    time.sleep(1)
    elem = browser.find_element_by_xpath('//*[@id="AvailabilitySearchInputSearchView_DropDownListPassengerType_CHD"]/option['+str(number_children+1)+']').click()
    #babies
    browser.find_element_by_xpath('//*[@id="AvailabilitySearchInputSearchView_DropDownListPassengerType_INFANT"]').click()
    time.sleep(1)
    elem = browser.find_element_by_xpath('//*[@id="AvailabilitySearchInputSearchView_DropDownListPassengerType_INFANT"]/option['+str(number_babies+1)+']').click()
    time.sleep(2)
    
    #go to search results (submit all information)
    elem = browser.find_element_by_xpath('//*[@id="AvailabilitySearchInputSearchView_btnClickToSearchNormal"]')
    elem.send_keys(Keys.RETURN)
    
    #get information about flights and save it to the dictionary "results"
    results = []
    #deal with a new page (contain flights schedule and prices)
    for i in range(10): #10 is an approximate number (there usually are less flights then 10)
        try:
            #get the line of a flight data and separate it
            flight = browser.find_element_by_xpath('//*[@id="availabilityTable0"]/tbody/tr[{}]/td[1]/div[2]/div[1]/div'.format(i)).text.split('\n') #get the line of a flight data
            basic_str = [jj for jj in browser.find_element_by_xpath('//*[@id="availabilityTable0"]/tbody/tr[{}]/td[2]'.format(i)).text.split('\n')[0].split(' ') if jj != ''][0]
            basic = [float(basic_str.split(',')[-1]) + int(basic_str.split(',')[-2]) if len(basic_str.split(',')) == 2 else float(basic_str)][0]
            optima_str = [jj for jj in browser.find_element_by_xpath('//*[@id="availabilityTable0"]/tbody/tr[{}]/td[3]'.format(i)).text.split('\n')[0].split(' ') if jj != ''][0]
            optima = [float(optima_str.split(',')[-1]) + int(optima_str.split(',')[-2]) if len(optima_str.split(',')) == 2 else float(optima_str)][0]
            excellence_str = [jj for jj in browser.find_element_by_xpath('//*[@id="availabilityTable0"]/tbody/tr[{}]/td[4]'.format(i)).text.split('\n')[0].split(' ') if jj != ''][0]
            excellence = [float(excellence_str.split(',')[-1]) + int(excellence_str.split(',')[-2]) if len(excellence_str.split(',')) == 2 else float(excellence_str)][0]

            if int(flight[1][3:].split(':')[0]) < int(flight[0].split(':')[0]):
                duration = (int(flight[1][3:].split(':')[0]) + 24 - int(flight[0].split(':')[0]))*60 + int(flight[1][3:].split(':')[1]) - int(flight[0].split(':')[1])
            else:
                duration = (int(flight[1][3:].split(':')[0]) - int(flight[0].split(':')[0]))*60 + int(flight[1][3:].split(':')[1]) - int(flight[0].split(':')[1])
            if flight[3][0] != 'D':
                duration = duration + ([int([i for i in flight[4].split(' ') if i != ''][0][:-1])*60 + 
                                        int([i for i in flight[4].split(' ') if i != ''][1][:-3]) 
                                        if len([i for i in flight[4].split(' ') if i != '']) == 2 
                                        else int([i for i in flight[4].split(' ') if i != ''][0][:-1])*60][0])

            results.append({'departure_local_time': flight[0],
                            'departure_airport': flight[1][:3],
                            'transfering': flight[3],
                            'arrival_local_time': flight[1][3:],
                            'arrival_airport': flight[2],
                            'prices': [basic, optima, excellence],
                            'currency': 'EUR',
                            'duration_mins': duration})
        except:
            pass
    #all needed information has gotten and the brouser could be closed
    browser.close()
    
    #transform the dictionary to a DataFrame
    results = pd.DataFrame(results)
    
    #return the DataFrame with information about flights
    return results
