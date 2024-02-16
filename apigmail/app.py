from flask import Flask,redirect, url_for, request
from Google import Create_Service
from flask_migrate import Migrate
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from bs4 import BeautifulSoup
from playsound import playsound
import pyttsx3
import os
import speech_recognition as sr
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase            
from email import encoders

#gmailapi

CLIENT_SECRET_FILE = 'abcc.json'
API_NAME = 'gmail'
API_VERSION = 'v1'
SCOPES = ['https://mail.google.com/', 'https://www.googleapis.com/auth/gmail.readonly']



#database

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///my_database.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username


#speech to text
    
def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()



#texttospeech
    
def listen_and_execute():
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("Listening...")
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=10)
            print("Recognizing...")
            command = recognizer.recognize_google(audio).lower()
            speak("You said:")
            speak(command)
            return command
    except sr.WaitTimeoutError:
        print("Timeout. No speech detected.")
    except sr.UnknownValueError:
        print("Could not understand audio")
    except sr.RequestError as e:
        print("Could not request results; {0}".format(e))



def listen_fast():
    recognizer = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            print("Listening...")
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=30)
            print("Recognizing...")
            command = recognizer.recognize_google(audio).lower()
            speak("You said:")
            speak(command)
            speak("do you wanna edit at any parts if yes or no ") 
            flag= listen_and_execute()
            if(flag!="no"):
                speak("start word")  
                start_word  = listen_and_execute()
                speak("end word")
                end_word  = listen_and_execute()
    
                command=edit_msg(command,start_word,end_word)
                return command
            return command

            
    except sr.WaitTimeoutError:
        print("Timeout. No speech detected.")
    except sr.UnknownValueError:
        print("Could not understand audio")
    except sr.RequestError as e:
        print("Could not request results; {0}".format(e))


def edit_msg(command, start_word, end_word):
 
    # Find the start and end indices of the substring to replace
    start_index = command.find(start_word)
    end_index = command.find(end_word, start_index + len(start_word))
    
    # If both start and end words are found
    if start_index != -1 and end_index != -1:
        replacement=listen_and_execute()
        edited_command = command[:start_index] + replacement + command[end_index + len(end_word):]
        print( edited_command)
        return edited_command
    else:
        speak("Start or end word not found in the command.")
        return command
        



def listen_slow():
    f=1
    command=listen_and_execute()
    while(f):
       
        speak(command)
        speak("do you want to add anything")
        flag=listen_and_execute()
        if(flag=="no"):
            return command
        command=command+listen_and_execute()
 

def dictate_email_body():
    while(1):
        speak("How do you want to dictate the body of the email slow or fast")
        speed = listen_and_execute()
        if speed == "fast":
            return listen_fast()
        
        elif speed == "slow":
            return listen_slow()
        else:
            print("Invalid input. Please enter 'slow' or 'fast'.")

        


def read_emails():
    """
    Retrieve emails from Gmail inbox
    """
    speak("reading mails")
    service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
    results = service.users().messages().list(userId='me', labelIds=['INBOX']).execute()
    messages = results.get('messages', [])

    if not messages:
        return 'No messages found.'
    else:
        print("Messages:")
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            message_data = msg['payload']['headers']
            for values in message_data:
                name = values['name']
               
                if name == 'From':
                    from_name = values['value']
                    speak(from_name)
                if name == 'Subject':
                    subject = values['value']
            if 'parts' in msg['payload']:        
                msg_str = base64.urlsafe_b64decode(msg['payload']['parts'][0]['body']['data'].encode('ASCII')).decode('utf-8')
                soup = BeautifulSoup(msg_str, 'html.parser')
                body = soup.get_text()
                print(f"From: {from_name}")
                print(f"Subject: {subject}")
            else:
                print("noooooo") 



def delete_last_message_from_sender(sender_name):
    """
    Retrieve emails from Gmail inbox and delete the last message from a specific sender
    """
    service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
    results = service.users().messages().list(userId='me', labelIds=['INBOX']).execute()
    messages = results.get('messages', [])

    if not messages:
        return 'No messages found.'

    last_message_id = None
    flag=1
    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id']).execute()
        message_data = msg['payload']['headers']
        for values in message_data:
            name = values['name']
          
            if name == 'From':
                from_name = values['value']
                print(from_name)
                if sender_name in from_name:

                    last_message_id = message['id']
                    flag=0
                    break
        if(flag==0):
            break        
    if last_message_id:
        service.users().messages().delete(userId='me', id=last_message_id).execute()
        return f"Last message from {sender_name} deleted successfully!"
    else:
        return f"No messages found from {sender_name}."



def search_email(sender_name):
    
    service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
    results = service.users().messages().list(userId='me', labelIds=['INBOX']).execute()
    messages = results.get('messages', [])

    if not messages:
        return 'No messages found.'
    flag=1
    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id']).execute()
        message_data = msg['payload']['headers']
        for values in message_data:
            name = values['name']
          
            if name == 'From':
                from_name = values['value']
              
                if sender_name in from_name:
                    flag=0
                    break
        if(flag==0):
            break    
    if(flag==0):
        speak("yes there is") 
    else:
        speak("no message")   




def send_email_att():

    """fl= listen_and_executee()
    print(fl)"""
    filename=listen_and_execute()
    file_path = os.path.join(r'C:\Users\AJEES\Documents', filename)
    if os.path.exists(file_path):  # Check if the file exists
            print("yes")
    else:
            print(f"File  not found. Please enter a valid filename.")

   
   
    service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

    # Your email content
    emailMsg = 'Here is your attachment.'
    mimeMessage = MIMEMultipart()
    mimeMessage['to'] = 'asna030502@gmail.com'
    mimeMessage['subject'] = 'Email with Attachment'
    mimeMessage.attach(MIMEText(emailMsg, 'plain'))
    with open(file_path, 'rb') as file:
        attachment = MIMEBase('application', 'octet-stream')
        attachment.set_payload(file.read())

    # Encode file in base64
    encoders.encode_base64(attachment)

    # Add headers to attachment
    attachment.add_header(
        'Content-Disposition',
        f'attachment; filename= {os.path.basename(file_path)}'
    )

    # Attach the attachment to the email message
    mimeMessage.attach(attachment)

    # Convert message to string and encode as base64
    raw_string = base64.urlsafe_b64encode(mimeMessage.as_bytes()).decode()

    # Send the email
    message = service.users().messages().send(userId='me', body={'raw': raw_string}).execute()

    return 'Email sent successfully!'





def create_draft_email():
    """
    Create a draft email using Gmail API
    """
    service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

    emailMsg = 'This is a draft email.'
    mimeMessage = MIMEMultipart()
    mimeMessage['to'] = 'aanittantony@gmail.com'
    mimeMessage['subject'] = 'Draft Email'
    mimeMessage.attach(MIMEText(emailMsg, 'plain'))
    raw_string = base64.urlsafe_b64encode(mimeMessage.as_bytes()).decode()

    draft = {
        'message': {
            'raw': raw_string
        }
    }

    draft = service.users().drafts().create(userId='me', body=draft).execute()
    return 'Draft email created successfully!' 



#apptoutesssssssssssssss

@app.route('/')
def send_email():
    """
    Send email using Gmail API
    """
    service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

    emailMsg = dictate_email_body()
    mimeMessage = MIMEMultipart()
    mimeMessage['to'] = 'vmail456345@gmail.com'
    mimeMessage['subject'] = 'You weree'
    mimeMessage.attach(MIMEText(emailMsg, 'plain'))
    raw_string = base64.urlsafe_b64encode(mimeMessage.as_bytes()).decode()

    message = service.users().messages().send(userId='me', body={'raw': raw_string}).execute()
    return 'Email sent successfully!'

@app.route('/read')

def read():
    read_emails()


@app.route('/att')
def att():
    result =send_email_att()
    return result
  

@app.route('/delete')      
def delete():
    sender_name = "vmail456345@gmail.com"
    result = delete_last_message_from_sender(sender_name)
    return result

@app.route('/search')      
def search():
    sender_name = "noreply@jobalertshub.com"
    search_email(sender_name)


@app.route('/draft')
def draftemail():
    result = create_draft_email()
    return result
    

if __name__ == '__main__':
    app.run()
