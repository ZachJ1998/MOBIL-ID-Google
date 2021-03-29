import config
import time
from config import DatabaseAccess as db
# for jwt signing. see https://google-auth.readthedocs.io/en/latest/reference/google.auth.jwt.html#module-google.auth.jwt
from google.auth import crypt as cryptGoogle
from google.auth import jwt as jwtGoogle
import hashlib, secrets, requests
import base64
from base64 import b64encode, b64decode
from Crypto.Util import Padding
from Crypto.Cipher import AES
from Crypto import Random

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

import math
from io import BytesIO

import mimetypes
import os
import sys
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
  PDF417 = 'PDF_417'
  Aztec = 'AZTEC'
  QR = 'QR_CODE'
  Code128 = 'CODE_128'
 

class Field(object):
  def __init__(self, key, value, label, changeMessage):
    self.key = key  # Required. The key must be unique within the scope
    self.value = value  # Required. Value of the field. For example, 42
    if label:
      self.label = label  # Optional. Label text for the field.
    if changeMessage:
      self.changeMessage = changeMessage

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
    self.heroImage = []
    self.locations = []
  

  def addTextModuleData(self, key, value, label='', changeMessage=None):
    self.textModulesData.append(Field(key, value, label, changeMessage))

  def addInfoModuleData(self, key, value, label='', changeMessage=None):
    self.infoModuleData.append(Field(key, value, label, changeMessage))

  def addBarcodeData(self, key, value, label='', changeMessage=None):
    altText = ''
    barcode = Barcode(value, BarcodeType, altText, messageEncoding='iso-8859-1')
    self.barcode.append(Field(key, value, label, changeMessage))
  
  def addHeroImageData(self, key, value, label ='', changeMessage=None):
    self.heroImage.append(Field(key, value, label, changeMessage))

  def addLocationsData(self, latitude, longitude, altitude=0.0, relevantText=None, maxDistance=None):
    self.locations.append(Location(latitude, longitude, altitude=0.0, relevantText=None, maxDistance=None))

class Location(object):
    def __init__(self, latitude, longitude, altitude=0.0, relevantText=None, maxDistance=None):
        # Required. Latitude, in degrees, of the location.
        try:
            self.latitude = float(latitude)
        except (ValueError, TypeError):
            self.latitude = 0.0
        # Required. Longitude, in degrees, of the location.
        try:
            self.longitude = float(longitude)
        except (ValueError, TypeError):
            self.longitude = 0.0
        # Optional. Altitude, in meters, of the location.
        try:
            self.altitude = float(altitude)
        except (ValueError, TypeError):
            self.altitude = 0.0
        # Optional. Text displayed on the lock screen when
        # the pass is currently near the location
        self.relevantText = relevantText
        # Optional. Notification distance
        self.maxDistance = maxDistance


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

          self.StudentPhoto = self.data['PhotoURL']

          self.barcodeType = BarcodeType.QR
          # self.locations.latitude = 35.647388
          # self.locations.longitude = -97.453438
          self.latitude = 35.647388
          self.longitude = -97.453438

          # try:
          #   resp = requests.get(self.StudentPhoto, stream=True).raw

          # except requests.exceptions.RequestException as e:  
          #     print("error")

          # try:
          #     StudentPhoto = Image.open(resp)
              

          # except IOError:
          #     print("Unable to open image")

          #img.save('test.jpg', 'jpg')        
          #img_path = "idPhoto.jpeg"
          #name = ("Jacob","Button")
          #User.create_hero_image(name, StudentPhoto, img_path)

          

      '''
      Create the Hero Image object that will dynamically change the name and image to each student/member
      '''
      def img_placement(image_size, canvas_size, width_ref, height_ref, text_wrap):


        if width_ref == "M":
            w = int(math.floor(canvas_size[0]/2 - image_size[0]/2))
        elif width_ref[0] == "L":
            w = width_ref[1]
        elif width_ref[0] == "R":
            w = canvas_size[0] - width_ref[1] - image_size[0]

        if height_ref == "M":
            l = int(math.floor(canvas_size[1]/2 - image_size[1]/2))
        elif height_ref[0] == "T":
            l = height_ref[1]
        elif height_ref[0] == "B":
            l = canvas_size[1] - height_ref[1] - image_size[1]
        if text_wrap == True:
            l = l - image_size[1]/2

        return (w,l)

      def to_wrap(name, font, max_length):

          if (font.getsize(name[0] + " " + name[1])[1] > max_length):
              name_txt = name[0] + '\n' + name[1]
              wrap = True
          else:
              name_txt = name[0] + " " + name[1]
              wrap = False
        
          return (name_txt,wrap)


      def create_hero_image(name, ID_pic: Image, new_image_path):
          canvas_size = (600,200)
          background_color = (128, 20, 41)

          width_ref_pic = ("R",40)
          length_ref_pic = ("M")

          width_ref_txt = ("L",50)
          length_ref_txt = ("M")

          maxfont_length = 250
          font_size = 34

          im = Image.open(ID_pic)

          baseheight = 125
          hpercent = (baseheight/float(im.size[1]))
          wsize = int((float(im.size[0])*float(hpercent)))
          im = im.resize((wsize,baseheight), Image.ANTIALIAS)
          mode = im.mode
          hero_image = Image.new(mode, canvas_size, background_color)

          place_pic = User.img_placement(im.size, hero_image.size, width_ref_pic, length_ref_pic, False)
          hero_image.paste(im, place_pic)


          draw = ImageDraw.Draw(hero_image)
          font = ImageFont.truetype("Roboto-Regular.ttf", font_size)

          name_txt = User.to_wrap(name, font, maxfont_length)
          place_txt = User.img_placement(font.getsize(name_txt[0]), hero_image.size, width_ref_txt, length_ref_txt, name_txt[1])
          draw.text(place_txt,name_txt[0],(255,255,255),font=font)

          hero_image.save(new_image_path)

          return hero_image

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
    
    img_path = "idPhoto.jpg"
    id_path = "uneditedIDPhoto.jpg"
    name = ("Jacob","Button")

    self.payload.setdefault('loyaltyObjects',[])
    self.payload['loyaltyObjects'].append(resourcePayload)
    passInformation.accountName = user.name
    passInformation.accountId = user.idNum
    passInformation.addInfoModuleData('pin',user.id_pin, 'ID Pin')
    passInformation.addInfoModuleData('print', user.print_balance, 'Print Balance','Your print balance is now %@.')
    passInformation.addInfoModuleData('boxnumber', user.mailbox, 'Mailbox Number') # use rest API function to get object and determine if user has
    # mailbox after passing in object ID
    passInformation.addTextModuleData('cash', '$' + user.eagle_bucks, 'Eagle Bucks','You have %@ Eagle Bucks remaining.')
    passInformation.addTextModuleData('meals',  user.meals_remaining, 'Meals Remaining','You have %@ meal swipes remaining.')
    passInformation.addTextModuleData('ethos', user.kudos_earned + "/" + user.kudos_required, 'Kudos','You have %@ Kudos of your Semester Goal.')
    passInformation.addBarcodeData('code', user.barcodeType, 'Barcode')
    user.StudentPhoto = "https://i.imgur.com/I6p54as.png"
    passInformation.addHeroImageData('image', user.StudentPhoto, 'heroImg')
    #user.StudentPhoto = User.create_hero_image(name, "uneditedIDPhoto.jpg", "idPhoto.jpg")
    #img_to_data("idPhoto.jpg")
    #user.StudentPhoto = Image.save("idPhoto.jpg", format="uri")
    passInformation.addLocationsData(35.611219, -97.467255, relevantText='Welcome to Garvey! Tap to scan your ID.', maxDistance=20)
    passInformation.addLocationsData(35.6115, -97.4695, relevantText='Welcome to the Branch! Tap to scan your ID.', maxDistance=20)
    passInformation.addLocationsData(35.61201, -97.46850, relevantText='Welcome to the Brew! Tap to scan your ID.', maxDistance=20)
    passInformation.addLocationsData(35.647388, -97.453438, relevantText='Welcome to the Lab! Tap to scan your ID.', maxDistance=20)

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