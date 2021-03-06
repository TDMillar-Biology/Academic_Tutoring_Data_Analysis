## This analysis was written by Trevor D. Millar
## 10/08/2021 -- 10/09/2021

## This is an exporatory analysis into the SI attendance data. These same data could be used to run the statistics on the SI program performance. 

## Standard Data-Science Libraries
import pdb
import numpy
import matplotlib
import time 
import os
import datetime


## We need a web scraper for this project because I'm not about to download all the data manually. 
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup as bs

## Lets get our login credentials for the scraper
login = input('Login: ')
password = input('Password: ')
startdate = '01042021'
enddate = '05062021'
DownloadsFilePath = '/home/tmillar/Downloads/Export.CSV'

def database_scrape():
    ## This function will scrape all of the data and feed the scraped data file into the clean_data function
    ## before we start to scrape, lets make sure we remove any artefacts of other files that will interfere
    if os.path.exists(DownloadsFilePath):
        os.remove(DownloadsFilePath)

    driver = webdriver.Chrome()
    driver.get("https://ais-que.uvu.edu/que/si/reports/advisorReport.php")
    username_box = driver.find_element_by_id('username')
    username_box.clear()
    username_box.send_keys(login)
    password_box = driver.find_element_by_id('password')
    password_box.clear()
    password_box.send_keys(password)
    submit_button = driver.find_element_by_xpath('/html/body/center/center/fieldset/form/center/input')
    submit_button.click()
    visits_report = driver.find_element_by_xpath('/html/body/div/div[1]/ul[2]/li[1]/a')
    visits_report.click()
    
    
    selecter = driver.find_element_by_id('center_select')
    time.sleep(5)
    options = [x for x in selecter.find_elements_by_tag_name('option')]
    selecter = Select(selecter)

    for course in options:
        if course.text != '--Select From Below':
            ## select the course, set the start and end date
            selecter.select_by_visible_text(course.text)
            driver.find_element_by_id('start_date').clear()
            driver.find_element_by_id('start_date').send_keys(startdate)
            driver.find_element_by_id('end_date').clear()
            driver.find_element_by_id('end_date').send_keys(enddate)
            driver.find_element_by_id('update_bttn').click()
            ## wait for page
            time.sleep(10)

            ## click to download the page
            driver.find_element_by_id('convert').click()
            time.sleep(10)
            ## clean the data and append it to the growing list
            clean_data('/home/tmillar/Downloads/Export.CSV')

    ## I need to click through the dropdown options and download the data for each file still. 
    
    driver.close()

def clean_data(filename):
    ## this function takes a file name and returns cleaned data
    out_file = open('Clean_data.csv', 'a') # Open outfile

    with open(filename, 'r') as in_file:
        data = in_file.readlines() # read in the outfile 

    for sign_in in data:    
        ## string manipulation     
        sign_in = sign_in.split(',')
        date = sign_in[0]
        in_time = convert24(sign_in[1].strip('"'))
        uvid = sign_in[5]
        course_and_prof = sign_in[7].strip('"').split(' - ')
        course = course_and_prof[0]
        try:
            professor = course_and_prof[1]
        except:
            professor = 'No Professor Listed'
        month, day, year = date.split('/')[0], date.split('/')[1], date.split('/')[2]
        weekday = get_weekday(date)
        outstring = uvid + ',' + date + ',' + weekday  + ',' + course + ',' + professor + ',' + month + ',' + day + ',' + year + ',' + in_time + '\n'
        
        out_file.write(outstring) # Write cleaned data

    in_file.close()
    out_file.close()
    os.remove(filename)

def get_weekday(date):
    ## take a date and return which day of the week it was
    weekDays = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    month, day, year = int(date.split('/')[0]), int(date.split('/')[1]), int(date.split('/')[2])
    weekday = weekDays[datetime.datetime(year, month, day).weekday()]

    return weekday

def filter_data():
    ## lets take a different approach from before and do this in pandas
    df = pd.read_csv('')

def duplicate_filter():
    in_file = open('Clean_data.csv', 'r')
    data = in_file.readlines()
    sign_in_dictionary = {}
    dupeCount = 0
    index = 0
    timepattern = '%H:%M'

    if os.path.exists('Dupes.txt'):
        os.remove('Dupes.txt')

    duplicates = open('Dupes.txt' , 'a')
    duplicates.write('I IDed these as duplicates and auto-removed them \n')
    for sign_in in data:
        sign_in = sign_in.split(',')
        key = sign_in[0] + ", " + sign_in[1] + ", " + sign_in[2] + ", " + sign_in[3] + ", " + sign_in[4]
        if key in sign_in_dictionary.keys():
            dupeCount = dupeCount + 1
            
            t1 = datetime.datetime.strptime(sign_in_dictionary[key].strip(), timepattern)
            t2 = datetime.datetime.strptime(sign_in[-1].strip(), timepattern)
            
            delta = t2 - t1
            delta = delta.total_seconds()
            if  delta == 0: ## if the sign_ins occur at the same time just delete the second
                duplicates.write(key)
                duplicates.write(sign_in_dictionary[key] + sign_in[-1])
            elif delta <= 300: ## if the sign_ins occur within 5 minutes of one another, just delete the second
                duplicates.write(key)
                duplicates.write(sign_in_dictionary[key] + sign_in[-1])
            else: ## if not, give the user the chance to look over them and delete them if they decide they are dupes. 
                print(key)
                print(sign_in_dictionary[key] + sign_in[-1])
                repeat = input('Is this a duplicate sign in?: [y or n]')
                if repeat.lower().strip() == 'y':
                    duplicates.write(key)
                    duplicates.write(sign_in_dictionary[key] + sign_in[-1])

                elif repeat.lower().strip() == 'n':
                    print('Okay ill figure it out') 
                    ## UNIMPLEMENTED CODE
                    ## I NEED TO WRITE THIS TO THE OUTFILE
                    
                else:
                    print(key)
                    print(sign_in_dictionary[key] + sign_in[-1])
                    repeat = input('Is this a duplicate sign in?: (only accepts [y or n])')
        else:
            sign_in_dictionary[key] = sign_in[-1]
    duplicates.close()

def SIL_filter(sign_in, SILS):
    ## This function checks a sign in to see if that sign in is an SIL, and if so, if they signed into their own class. 
    pass

def read_SILS():
    ## this function checks for the SIL data in SIL_data.csv and loads it up. 
    SILS_in = open('SIL_data.csv', 'r')
    SILS = SILS_in.readlines()

    return SILS

def convert24(str1):
    ## I got this from https://www.geeksforgeeks.org/python-program-convert-time-12-hour-24-hour-format/ to save time
    ## Modified to my needs
    # Checking if last two elements of time
    # is AM and first two elements are 12
    if str1[-2:] == "am" and str1[:2] == "12":
        return "00" + str1[2:-2]
          
    # remove the AM    
    elif str1[-2:] == "am":
        return str1[:-2]
      
    # Checking if last two elements of time
    # is PM and first two elements are 12   
    elif str1[-2:] == "pm" and str1[:2] == "12":
        return str1[:-2]
          
    else:
          
        # add 12 to hours and remove PM
        return str(int(str1[:2]) + 12) + str1[2:5]

def add_course_details():
    
    in_file = open('Clean_data.csv', 'r')
    clean = in_file.readlines()
    out_file = open('Clean_data_withcourse.csv', 'w')
    course_details = open('course_details.csv', 'r')
    student_info = course_details.readlines()
    for student in student_info:
        student = student.split(',')
        student[1] = Section_number_adjust(student[1])
        
        pdb.set_trace()
    
    ## UVID is column 2 in student, column 5 in clean data. If student[2] == clean[5]: append to clean student list the section number 

    in_file.close()
    out_file.close()
    course_details.close()

def Section_number_adjust(sectionnum):
    ## adds 00 in front of section numbers if its just one number
    sectionnum = str(sectionnum)
    while len(sectionnum) < 3:
        sectionnum = '0' + sectionnum

    return sectionnum

def all_student_data():
    in_file = open('All_students_SPRING21.csv', 'r')
    all_studnets = in_file.readlines()
    student_dictionary = {}
    for student in all_students:
        ## UVID = Name, 
        course = student[0]
        section = Section_number_adjust(student[1])
       
        UVID = student[5]
        name = student[7]

        major = student[9]
        

def main():
    #SILS = read_SILS()
    #database_scrape()
    #clean_data('/home/tmillar/Downloads/Export.CSV') ## This is for debugging purposes
    #add_course_details()
    duplicate_filter()
    
if __name__ == "__main__":
    main()

