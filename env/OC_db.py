import hashlib, secrets, requests, time
from base64 import b64encode, b64decode
from Crypto.Util import Padding
from Crypto.Cipher import AES
from Crypto import Random

'''
Encrypts a string of text with a given password using AES-256 encryption
'''
def encrypt(raw, password):
    private_key = hashlib.sha256(password.encode("utf-8")).digest()
    raw = Padding.pad(raw.encode('utf-8'), AES.block_size)
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(private_key, AES.MODE_CBC, iv)
    return b64encode(iv + cipher.encrypt(raw)).decode("utf-8")

# Fake Data
id_num = '1524743'
password = 'E@gleM0BileP@ss'

# Generate Request
token = encrypt(id_num + '-' + str(time.time()), password)
request_URL = 'https://account.oc.edu/mobilepass/details/' + id_num + '?token=' + token

# Request
r = requests.get(request_URL)
data = r.json()

if r.status_code == 200:
    print('200 - OK')
    print(data)
else:
    print(str(r.status_code) + '- ERROR')