import os
import smtplib
import time
import imaplib
import email
import sys
import datetime
import daemon

from string import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

LOG_ADDRESS = "Pablo Sanchez Bergasa pablosanchez18393@hotmail.com"
MY_ADDRESS = 'renfeticketsavailable@gmail.com'
PASSWORD = '*CRS*lunes17'
SMTP_SERVER = "imap.gmail.com"
SUBJECTSUBSCRIPTION = "AVISAMEMADPAM"
SUBJECTUNSUBSCRIPTION = "DESINSCRIBIR"
PREVIOUSLYNOTIFIED = 0
CHECKSCRIPTFREQUENCY = 30 #in minutes, check if script is still working
CHECKEMAILFREQUENCY = 5 #in seconds, frequency to check new emails

# -------------------------------------------------
#
# Utility to read email from Gmail Using Python
#
# ------------------------------------------------

def read_template(filename):
    """
    Returns a Template object comprising the contents of the 
    file specified by filename.
    """
    
    with open(filename, 'r', encoding='utf-8') as template_file:
        template_file_content = template_file.read()
    return Template(template_file_content)

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

def checkRepeatedEmail(forwardEmail):
    with open('nonPriorityContacts.txt') as file:
        lineNumber = 0
        repeated_email = 0
        for line in file:
            if forwardEmail in line:
                repeated_email=1
                log ("Repeated email", 'beginLine')
                log (str(lineNumber), 'endLine')
                file.close()
                return (lineNumber)
            lineNumber += 1
    log ("New Email", 'newLine')
    file.close()
    return (-1)
    

def subscribeEmail(forwardEmail):
    log ("Subscribing email...", 'newLine')
    if checkRepeatedEmail(forwardEmail) < 0:
        file= open("nonPriorityContacts.txt","a")
        file.write(forwardEmail)
        file.write("\r\n")
        file.close()
        log("New mail subscription: ", 'beginLine')
        log(forwardEmail,'endLine')
        sendEmail (forwardEmail, "AvisameRenfe: subcripcion", 'subscription.txt')

def unsubscribeEmail(forwardEmail):
    log ("Unsubscribing ", 'beginLine')
    log (forwardEmail, 'endLine')
    with open("nonPriorityContacts.txt", "r") as f:
        lines = f.readlines()
    with open("nonPriorityContacts.txt", "w") as f:
        for line in lines:
            if line.strip("\n") != forwardEmail:
                f.write(line)
    sendEmail (forwardEmail, "AvisameRenfe: desubscripcion", 'unsubscription.txt')


def sendEmail(forwardEmail,emailSubject, messageToSend):
    message_template = read_template(messageToSend)
    # set up the SMTP server
    s = smtplib.SMTP('smtp.gmail.com' , 587)
    s.starttls()
    s.login(MY_ADDRESS, PASSWORD)

    # For each contact, send the email:
    msg = MIMEMultipart()

    # add in the actual person name to the message template
    message = message_template.substitute(PERSON_NAME=forwardEmail.split()[0])

    # Prints out the message body for our sake
    log(message, 'newLine')

    # setup the parameters of the message
    msg['From']=MY_ADDRESS
    msg['To']=forwardEmail.split()[len(forwardEmail.split())-1]
    msg['Subject']=emailSubject
        
    # add in the message body
    msg.attach(MIMEText(message, 'plain'))
        
    # send the message via the server set up earlier.
    s.send_message(msg)
    del msg
        
    # Terminate the SMTP session and close the connection
    s.quit()

def log(logToSave, line):
    now = datetime.datetime.now()    
    file= open("emailLoggerlogs.txt","a")
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

def read_email_from_gmail():
    try:
        mail = imaplib.IMAP4_SSL(SMTP_SERVER)
        mail.login(MY_ADDRESS,PASSWORD)
        mail.select('inbox')

        type, data = mail.search(None, 'UnSeen')
        mail_ids = data[0]
        id_list = mail_ids.split()
        for i in reversed(id_list):
            typ, data = mail.fetch(i, '(RFC822)' )

            for response_part in data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_string(response_part[1].decode('utf-8'))
                    email_subject = msg['subject']
                    email_from = msg['from']
                    if(SUBJECTSUBSCRIPTION == email_subject):
                        subscribeEmail(email_from)
                    elif SUBJECTUNSUBSCRIPTION == email_subject:
                        if checkRepeatedEmail(email_from) > 0:
                            unsubscribeEmail(email_from)
                        else:
                            log ("no email to unsubscribe", 'newLine')
                    else:
                        log ("Received email with non matching subject", 'newLine')                        
                    
    except Exception as e:
        log(str(e), 'newLine')

def main():
    while True:
        count = 0
        prevLogLines = 0
        for line in open('RenfeScriptLog.txt'): prevLogLines += 1
        numLines = 0
        while count < 60*CHECKSCRIPTFREQUENCY/CHECKEMAILFREQUENCY:
            read_email_from_gmail()
            time.sleep(CHECKEMAILFREQUENCY)
            count += 1
        for line in open('RenfeScriptLog.txt'): numLines += 1
        if(prevLogLines == numLines):
            global PREVIOUSLYNOTIFIED
            if(PREVIOUSLYNOTIFIED == 0):
                log ("Renfe script stopped working", 'newLine')
                sendEmail (LOG_ADDRESS, "AvisameRenfe: script ha dejado de funcionar", 'scriptStoppedWorking.txt') 
                PREVIOUSLYNOTIFIED = 1

if __name__ == "__main__":
    main()

    

