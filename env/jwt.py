import config
import time
from config import DatabaseAccess as db
# for jwt signing. see https://google-auth.readthedocs.io/en/latest/reference/google.auth.jwt.html#module-google.auth.jwt
from google.auth import crypt as cryptGoogle
from google.auth import jwt as jwtGoogle
import hashlib, secrets, requests, time
from base64 import b64encode, b64decode
from Crypto.Util import Padding
from Crypto.Cipher import AES
from Crypto import Random


#############################
#
# class that defines JWT format for a Google Pay Pass.
#
# to check the JWT protocol for Google Pay Passes, check:
# https://developers.google.com/pay/passes/reference/s2w-reference#google-pay-api-for-passes-jwt
#
# also demonstrates RSA-SHA256 signing implementation to make the signed JWT used
# in links and buttons. Learn more:
# https://developers.google.com/pay/passes/guides/get-started/implementing-the-api/save-to-google-pay
#
#############################

class BarcodeType:
  PDF417 = 'pdf417'
  Aztec = 'aztec'
  QR = 'qrCode'
  Code128 = 'code128'
 

class Field(object):
  def __init__(self, key, value, label):
    self.key = key  # Required. The key must be unique within the scope
    self.value = value  # Required. Value of the field. For example, 42
    self.label = label  # Optional. Label text for the field.

class Barcode(object):
  def __init__(self, message, format=BarcodeType.PDF417, altText='', messageEncoding='iso-8859-1'):
    self.format = format
    self.message = message  # Required. Message or payload to be displayed as a barcode
    self.messageEncoding = messageEncoding  # Required. Text encoding that is used to convert the message
    if altText:
      self.altText = altText  # Optional. Text displayed near the barcode

class PassInformation(object):
  def __init__(self):

    self.textModulesData = []
    self.infoModuleData = []
    self.loyaltyPoints = []
    self.barcode = []
  

  def addTextModuleData(self, key, value, label=''):
    self.textModulesData.append(Field(key, value, label))

  def addInfoModuleData(self, key, value, label=''):
    self.infoModuleData.append(Field(key, value, label))

  def addBarcodeData(self, key, value, label=''):
    altText = ''
    barcode = Barcode(value, BarcodeType, altText, messageEncoding='iso-8859-1')
    self.barcode.append(Field(key, value, label))



class User():
      def __init__(self, entered_id: str, entered_pin: str = None):
        self.valid = True

        self.id_num = entered_id
        #id_num = "1524743"
        password = 'E@gleM0BileP@ss'
        
        # Generate Request
        token = db.encrypt(self.id_num + '-' + str(time.time()), password)
        request_URL = 'https://account.oc.edu/mobilepass/details/' + self.id_num + '?token=' + token
        # Request
        r = requests.get(request_URL)
        data = r.json()
         
        r = requests.get(request_URL, timeout=5)
        try:
            # try to parse request body
            self.data = r.json()
        except:
            # if bad response from OC,
            # invalidate user
            print("error")

      '''
      User is valid, store data in python object
      '''
      def create(self):
          
          self.idNum = self.id_num
          self.name = self.data['FullName']
          try:
            self.eagle_bucks = self.data['EagleBucks']
          except:
            self.eagle_bucks = "None"

          self.meals_remaining = self.data['MealsRemaining']
          try:
            self.kudos_earned = str(self.data['KudosEarned'])
            self.kudos_required = str(self.data['KudosRequired'])
          except:
            self.kudos_earned = "Exempt"
            self.kudos_required = "Exempt"

          self.id_pin = self.data['IDPin']
          try:
            self.print_balance = self.data['PrintBalance']
          except:
            self.print_balance = "None"
          try:
            self.mailbox = self.data['Mailbox']
          except:
            self.mailbox = "None"

          self.barcodeType = BarcodeType.QR

class googlePassJwt:
  def __init__(self):
    self.audience = config.AUDIENCE
    self.type = config.JWT_TYPE
    self.iss = config.SERVICE_ACCOUNT_EMAIL_ADDRESS
    self.origins = config.ORIGINS
    self.iat = int(time.time())
    self.payload = {}
    
    # signer for RSA-SHA256. Uses same private key used in OAuth2.0
    self.signer = cryptGoogle.RSASigner.from_service_account_file(config.SERVICE_ACCOUNT_FILE)


  def addLoyaltyClass(self, resourcePayload):
    self.payload.setdefault('loyaltyClasses',[])
    self.payload['loyaltyClasses'].append(resourcePayload)

  def addLoyaltyObject(self, resourcePayload, user):
    passInformation = PassInformation()
    user.create()
    self.payload.setdefault('loyaltyObjects',[])
    self.payload['loyaltyObjects'].append(resourcePayload)
    passInformation.accountName = user.name
    passInformation.accountId = user.idNum
    passInformation.addInfoModuleData('pin',user.id_pin, 'ID Pin')
    passInformation.addInfoModuleData('print', user.print_balance, 'Print Balance')
    passInformation.addInfoModuleData('boxnumber', user.mailbox, 'Mailbox Number') # use rest API function to get object and determine if user has
    # mailbox after passing in object ID
    passInformation.addTextModuleData('cash', "$" + user.eagle_bucks, 'Eagle Bucks')
    passInformation.addTextModuleData('meals',  user.meals_remaining, 'Meals Remaining')
    passInformation.addTextModuleData('ethos', user.kudos_earned + "/" + user.kudos_required, 'Kudos')
    passInformation.addBarcodeData('code', user.barcodeType, 'Barcode')


  def generateUnsignedJwt(self):
    unsignedJwt = {}
    unsignedJwt['iss'] = self.iss
    unsignedJwt['aud'] = self.audience
    unsignedJwt['typ'] = self.type
    unsignedJwt['iat'] = self.iat
    unsignedJwt['payload'] = self.payload
    unsignedJwt['origins'] = self.origins

    return unsignedJwt

  def generateSignedJwt(self):
    jwtToSign = self.generateUnsignedJwt()
    signedJwt = jwtGoogle.encode(self.signer, jwtToSign)

    return signedJwt