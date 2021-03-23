import config
import time

# for jwt signing. see https://google-auth.readthedocs.io/en/latest/reference/google.auth.jwt.html#module-google.auth.jwt
from google.auth import crypt as cryptGoogle
from google.auth import jwt as jwtGoogle


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
    user = User()
    user.create()
    barcode = Barcode(user.idNum, BarcodeType, str(user.idNum),messageEncoding='iso-8859-1')
    self.barcode.append(Field(key, value, label))



class User():
    '''
    User is valid, store data in python object
    '''
    def create(self):
        self.idNum = "15"
        self.name = "Zach Jones"
        self.eagle_bucks = "$58.25"
        self.meals_remaining = "10"
        self.kudos_earned = "15"
        self.kudos_required = "20"
        self.id_pin = "3905"
        self.print_balance = "54.40"
        self.mailbox = "0738"
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

  def addLoyaltyObject(self, resourcePayload):
    user = User()
    user.create()
    passInformation = PassInformation()

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