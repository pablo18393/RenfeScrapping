# Generated by Selenium IDE
import pytest
import time
import json
import smtplib
import random
import datetime
import sys
import socket

from string import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium import webdriver

#trainLine with available trains:
trainLineAvailableURL = 'https://www.thetrainline.com/book/results?origin=a0893c38dcb9222abe36edec6a51a1ac&destination=4e139b1c9606fb723c6c91f5ab282209&outwardDate=2019-12-04T01%3A00%3A00&outwardDateType=departAfter&journeySearchType=single&passengers%5B%5D=1993-09-11%7C2fcaf264-e164-4475-a700-14125cc95137&lang=es&selectedOutward=Iqx1tvxG54s%3D%3Aq3TP9vc0GnA%3D%3AStandard'
#trainLine to check available trains:
trainLineCheckAvailableURL = 'https://www.thetrainline.com/book/results?origin=a0893c38dcb9222abe36edec6a51a1ac&destination=4e139b1c9606fb723c6c91f5ab282209&outwardDate=2020-01-15T01%3A00%3A00&outwardDateType=departAfter&journeySearchType=single&passengers%5B%5D=1993-09-11%7C2fcaf264-e164-4475-a700-14125cc95137&lang=es'
#logicTravel with available trains:
logicTravelAvailableURL = 'https://www.logitravel.com/transportstransactional/AvailabilityMaterial?ProductType=Train&hashRooms=30A0D&LineOfBusiness=Trains&DestinationType=EST&OriginAirportCode=0YH&DestinationCode=1GO&DepartureDateStr=04/12/2019&DepartureHourStr=06:00'
#logicTravel to check available trains:
logicTravelCheckAvailableURL = 'https://www.logitravel.com/transportstransactional/AvailabilityMaterial?ProductType=Train&hashRooms=30A0D&LineOfBusiness=Trains&DestinationType=EST&OriginAirportCode=0YH&DestinationCode=1GO&DepartureDateStr=04/01/2020&DepartureHourStr=06:00'

MY_ADDRESS = 'renfeticketsavailable@gmail.com'
PASSWORD = '*CRS*lunes17'

REQUESTDELAY = 0
REQUESTDELAYMIN = 3 #in mins 
REQUESTDELAYMAX = 7 #in mins 
PRIORITYDELAY = 20 #in mins

previousFailNotified = 0

def get_contacts(filename):
    """
    Return two lists names, emails containing names and email addresses
    read from a file specified by filename.
    """
    
    names = []
    emails = []
    with open(filename, mode='r', encoding='utf-8') as contacts_file:
        for a_contact in contacts_file:
            if ((len(a_contact.split())-1) > 0):
                names.append(a_contact.split()[0])
                emails.append(a_contact.split()[len(a_contact.split())-1])
    return names, emails

def read_template(filename):
    """
    Returns a Template object comprising the contents of the 
    file specified by filename.
    """
    
    with open(filename, 'r', encoding='utf-8') as template_file:
        template_file_content = template_file.read()
    return Template(template_file_content)

def sendEmails(emailList, emailSubject, messageToSend):
    names, emails = get_contacts(emailList) # read contacts
    message_template = read_template(messageToSend)

    # set up the SMTP server
    s = smtplib.SMTP('smtp.gmail.com' , 587)
    s.starttls()
    s.login(MY_ADDRESS, PASSWORD)

    # For each contact, send the email:
    for name, email in zip(names, emails):
        msg = MIMEMultipart()       # create a message

        # add in the actual person name to the message template
        message = message_template.substitute(PERSON_NAME=name.title())

        # Prints out the message body for our sake
        #log(message, 'newLine')
        log("Sending email to: ", 'beginLine')
        log(email, 'endLine')
        # setup the parameters of the message
        msg['From']=MY_ADDRESS
        msg['To']=email
        msg['Subject']=emailSubject
        
        # add in the message body
        msg.attach(MIMEText(message, 'plain'))
        
        # send the message via the server set up earlier.
        s.send_message(msg)
        del msg
        
    # Terminate the SMTP session and close the connection
    s.quit()

def checkRenfeTrains (date):
    if(internet_connection()):
        log("Checkeando billetes en Renfe...", 'beginLine')
        success = 0
        driver = webdriver.Firefox()
    ##    driver.minimize_window()
        driver.get("http://www.renfe.com/")
        driver.find_element_by_id("IdOrigen").click()
        driver.find_element_by_id("IdOrigen").send_keys("mad")
        time.sleep(1)
        driver.find_element_by_id("IdOrigen").send_keys(Keys.ENTER)
        if(driver.page_source.find("Madrid")>0):
            log ("Renfe web working as expected", 'endLine')
        else:
            log ("Renfe web ISSUE", 'endLine')        
        driver.find_element_by_id("IdDestino").send_keys("pam")
        time.sleep(1)
        driver.find_element_by_id("IdDestino").send_keys(Keys.ENTER)
        driver.find_element_by_id("__fechaIdaVisual").click()
        driver.find_element_by_id('__fechaIdaVisual').clear()
        driver.find_element_by_id("__fechaIdaVisual").send_keys(date)
        driver.find_element_by_css_selector(".btn").click()
        if(driver.page_source.find("7.35") > 0 or driver.page_source.find("11.35") > 0 or driver.page_source.find("15.05") > 0):
            success = 1
        driver.close()
        driver.quit()
        return (success)
    
def checkDirectURLwebpage (url):
    log("Checkeando billetes en web con URL directa...", 'newLine')
    success = 0
    driver = webdriver.Firefox()
##    driver.minimize_window()
    driver.get(url)
    time.sleep(5) #wait for the browser to load page
    if(driver.page_source.find("7:35") > 0 or driver.page_source.find("11:35") > 0):
        success = 1
    driver.close()
    driver.quit()
    return (success)

def checkTrains (result, checkMode):
    if(checkMode=='verify'):
        log("verifying script funcionality...", 'beginLine')
        if (result == 1):
            log("script working as expected", 'endLine')
        else:
            log("script FAIL", 'endLine')
            global previousFailNotified
            if (previousFailNotified == 0):
                previousFailNotified=1
                sendEmails('priorityContacts.txt',"Renfe: fail script",'scriptFail.txt')          
    elif (checkMode == 'check'):
        if (result) == 1:
            log("Nuevos billetes disponibles, mandando correos de notificacion...", 'newLine')
            sendEmails('priorityContacts.txt',"Renfe: nuevos billetes",'ticketsAvailable.txt')
            time.sleep(PRIORITYDELAY*60)
            sendEmails('othersContacts.txt',"Renfe: nuevos billetes",'ticketsAvailable.txt')
            time.sleep(PRIORITYDELAY*60)
            sendEmails('othersContacts.txt',"Renfe: nuevos billetes",'ticketsAvailable.txt')
            while True:
                input("SCRIPT FINISHED")
        else:
            REQUESTDELAY = random.randrange(REQUESTDELAYMIN, REQUESTDELAYMAX)
            log("No hay billetes disponibles, siguiente consulta dentro de ", 'beginLine')
            log(str(REQUESTDELAY), 'noNewLine')
            log(" minutos",'endLine')
            time.sleep(REQUESTDELAY * 60)

def log(logToSave, line):
    now = datetime.datetime.now()    
    file= open("RenfeScriptLog.txt","a")
    if(line == 'newLine' or line == 'beginLine'):
        file.write(now.strftime("%H:%M:%S:%Y-%m-%d"))
        file.write(":")
        print(now.strftime("%H:%M:%S:%Y-%m-%d"), end = '')
        print(":", end = '')
    file.write(logToSave)
    print(logToSave, end = '')
    if(line == 'newLine' or line == 'endLine'):
        file.write("\r\n")
        print("")
    file.close()
            
def internet_connection():
    try:
        log ("checking internet connection...", 'newLine')
        host = socket.gethostbyname("www.google.com")
        s = socket.create_connection((host, 80), 2)
        s.close()
        log ('Internet connection: ON', 'newLine')
        return True

    except Exception as e:
        log (str(e), 'newLine')
        log ('Internet connection: OFF', 'newLine')
    return False

def verifyingTest():
    #checkTrains (checkDirectURLwebpage(trainLineAvailableURL), 'verify')
    #checkTrains (checkDirectURLwebpage(logicTravelAvailableURL), 'verify')
    checkTrains (checkRenfeTrains("04/12/2019"), 'verify')


def main():
    while True:
        try:
            verifyingTest()
            count = 0
            while count < 50:
                checkTrains (checkRenfeTrains("15/01/2020"), 'check')
                #checkTrains (checkDirectURLwebpage(trainLineCheckAvailableURL), 'check')
                #checkTrains (checkDirectURLwebpage(logicTravelCheckAvailableURL), 'check')
                count += 1
        except Exception as e:
            log(str(e), 'newline')
            if 'KeyboardInterrupt' in str(e):
                exit
            else:
                continue
        
if __name__ == '__main__':
    main()    
    
  
