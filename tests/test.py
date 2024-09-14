from pyzbar.pyzbar import decode
from PIL import Image
import pronotepy
import json
from uuid import uuid4
from time import sleep
import datetime

img = Image.open('image.png')

decoded_objects = decode(img)
credentials={}

#print(decoded_objects)
try:
    qrcode_data=json.loads(decoded_objects[0].data.decode("utf-8"))
except Exception as e:
    print(f"Can not decode QR code: {str(e)}")
    exit()

pin="1234"
uuid=uuid4()
print(uuid)

try:
    client=pronotepy.Client.qrcode_login(qrcode_data, pin, str(uuid))
except Exception as e:
    print(f"Can not login with QR code: {str(e)}")
    exit()

credentials = {
    "url": client.pronote_url,
    "username": client.username,
    "password": client.password,
    "uuid": client.uuid,
}
print(credentials)

def renew_client():
    global credentials
    client = pronotepy.Client.token_login(
        credentials["url"],
        credentials["username"],
        credentials["password"],
        credentials["uuid"],
    )
    # save new credentials
    credentials = {
        "url": client.pronote_url,
        "username": client.username,
        "password": client.password,
        "uuid": client.uuid,
    }
    print(credentials)
    return client

while True:
    try:
        print(client.current_period.grades)
    except Exception as e:
        print(e)
        print("client renewed")
        client=renew_client()
    
    now = datetime.datetime.now()

    current_time = now.strftime("%H:%M:%S")
    print("Current Time =", current_time)
    sleep(5*60) # try every 5 minutes.

