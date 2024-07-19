import cv2
import pytesseract
import re
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from Adafruit_IO import Client, Feed, RequestError

pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

img = cv2.imread('S1.jpeg')
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

text = pytesseract.image_to_string(img)

# Extracting manufacturing date and expiry date using regular expressions
mfg_date_pattern = re.compile(r'(mfg).*?(\d{2}/)?\d{2}/\d{4}', re.IGNORECASE)
mfg_date_match = re.search(mfg_date_pattern, text)

exp_date_pattern = re.compile(r'(exp).*?(\d{2}/)?\d{2}/\d{4}', re.IGNORECASE)
exp_date_match = re.search(exp_date_pattern, text)

quantity_match = re.search(r'Quantity:(\d+)', text)
id_match = re.search(r'ID:(\d+)', text)

quantity = quantity_match.group(1) if quantity_match else 'Not found'
medicine_id = id_match.group(1) if id_match else 'Not found'

print('Quantity:', quantity)
print('ID:', medicine_id)


print('Manufacturing Date:', mfg_date_match.group(0) if mfg_date_match else 'Not found')
print('Expiry Date:', exp_date_match.group(0) if exp_date_match else 'Not found')

# Extract day, month, and year components from the expiry date
expiry_date = exp_date_match.group(0) if exp_date_match else None
if expiry_date:
    day, month, year = expiry_date.split('/')
    year2 = int(year)
    month2 = int(month)

    # Get the current date
    current_date = datetime.now()

    # Extract day, month, and year components
    day1 = current_date.day
    month1 = current_date.month
    year1 = current_date.year

    # Print the extracted components
    print("Current Date:", current_date.strftime('%Y-%m-%d'))

    # Check if the medicine is expired
    if year1 > year2 or (year1 == year2 and month1 > month2):
        print("Alert: Medicine is Expired")


    else:
        print("You can use the medicine")

# Display the image
cv2.imshow('Result', img)
cv2.waitKey(0)


def send_email(subject, body):
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    sender_email = ''
    sender_password = ''
    recipient_email = '' 

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(sender_email, sender_password)


    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = recipient_email
 
    server.sendmail(sender_email, [recipient_email], msg.as_string())

    server.quit()
send_email('Medicine Expiry Alert','The medicine is expired. Manufactured on: {} and Expires on: {}. Quantity: {} and ID: {}'
           .format(mfg_date_match.group(0) if mfg_date_match else 'Not found',
                   expiry_date, quantity, medicine_id))


ADAFRUIT_IO_KEY = ''
ADAFRUIT_IO_USERNAME = ''

aio = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

try:
    feed = aio.feeds('medicine_expiry')  
except RequestError:
    # If the feed doesn't exist, create it
    feed = Feed(name='medicine_expiry')  
    feed = aio.create_feed(feed)

# Create a message with all the data
data_message = f'Manufacturing Date: {mfg_date_match.group(0)}, Expiry Date: {expiry_date}, Quantity: {quantity}, ID: {medicine_id}'

# Send the data message to the feed
aio.send_data(feed.key, data_message)