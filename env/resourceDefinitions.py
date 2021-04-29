import datetime
from google.oauth2 import service_account # pip install google-auth
import jwt
import json

def makeLoyaltyClassResource(classId):
  # Define the resource representation of the Class
  # values should be from your DB/services; here we hardcode information

  payload = {}

  # below defines an Loyalty class. For more properties, check:
  # https://developers.google.com/pay/passes/reference/v1/loyaltyclass/insert
  # https://developers.google.com/pay/passes/guides/pass-verticals/loyalty/design

  payload = {
    # required fields
    "id": classId,
    "hexBackgroundColor" : "#801429",
    "issuerName": "Oklahoma Christian University",
    "programName": "Mobile Pass",
    "reviewStatus": "underReview",
    # optional
    "programLogo": {
        "kind": "walletobjects#image",
        "sourceUri": {
            "kind": "walletobjects#uri",
            "uri": "https://i.imgur.com/bLZrZIl.png"
        }
    },
    "classTemplateInfo": {
        "cardTemplateOverride": {
            "cardRowTemplateInfos": [{
                "threeItems": {
                    "startItem": {
                        "firstValue": {
                            "fields": [{
                                "fieldPath": "object.textModulesData['myfield1']"
                            }]
                        }
                    },
                    "middleItem": {
                        "firstValue": {
                            "fields": [{
                                "fieldPath": "object.textModulesData['myfield2']"
                            }]
                        }
                    },
                    "endItem": {
                        "firstValue": {
                            "fields": [{
                                "fieldPath": "object.textModulesData['myfield3']"
                            }]
                        }
                    },
                }
            }],
        }
    },
    "locations": [{
        "kind": "walletobjects#latLongPoint",
        "latitude": 35.613306,
        "longitude": -97.467825,
        "label" : "lab"
      },    
      {
        "kind": "walletobjects#latLongPoint",
        "latitude": 35.611219,
        "longitude": -97.467255,
        "label" : "garvey"
      },
      {
        "kind": "walletobjects#latLongPoint",
        "latitude": 35.61201,
        "longitude": -97.46850,
        "label" : "brew"
      },
      {
        "kind": "walletobjects#latLongPoint",
        "latitude": 35.6115,
        "longitude":-97.4695,
        "label" : "branch"
    }] 
  }
 
  return payload


def makeLoyaltyObjectResource(classId, objectId, user: jwt.User):
    print("Entering RD")
    payload = {}
    passinfo = jwt.PassInformation()

    passinfo.addAccountName(user.name)
    passinfo.addtextModulesData(header="Eagle Bucks", id="myfield1",body=('$' + user.eagle_bucks))
    passinfo.addtextModulesData(header='Meals Remaining',  body=user.meals_remaining,id='myfield2')
    passinfo.addtextModulesData(header='Kudos',  body=user.kudos_earned + '/' + user.kudos_required,id='myfield3')
    passinfo.addinfoModulesData(value=user.id_pin, label='ID Pin')
    passinfo.addAccountID(user.id_num)
    bcType = jwt.BarcodeType.QR
    # message, format=BarcodeType.PDF417, altText='', messageEncoding='iso-8859-1'
    #bc = Barcode(message='123456789abcdefghijklmnop', format=barcodeType, altText=str(accID))
    passinfo.barcode.append(jwt.Barcode(value=user.id_num, type= user.barcodeType, alternateText=str(user.id_num))) #this message will eventually be pass_hash
    #passinfo.addBarcodeData(value=user.id_num, type='QR_CODE', alternateText=str(user.id_num))
    passinfo.locations.append(jwt.Location(kind="walletobjects#latLongPoint",latitude=35.611219,longitude=-97.467255, label="garvey"))
    passinfo.locations.append(jwt.Location(kind="walletobjects#latLongPoint",latitude=35.6115,longitude= -97.4695, label="brew"))
    passinfo.locations.append(jwt.Location(kind="walletobjects#latLongPoint",latitude=35.61201,longitude= -97.46850, label="branch"))
    passinfo.heroImage.append(jwt.HeroImage(image="asdasdas", uri="https://i.imgur.com/I6p54as.png", label="heroImg"))

    if user.print_balance:   
        passinfo.addinfoModulesData(value=user.print_balance, label='Print Balance')
    if user.mailbox:
        passinfo.addinfoModulesData(value=user.mailbox,label='Mailbox Number')

    print("Added to passinfo")
    if passinfo.accountId:
        payload.update({'id': objectId, 'classId': "3388000000009088928.LOYALTY_CLASS_d8a36821-33d1-4371-bdeb-e0da0d0fbe0b", 'state': 'active', 'accountId': user.id_num})
        print("Added accountId")
    if passinfo.accountName:
        payload.update({'accountName': user.name})
        print("Added accountName")
    if passinfo.barcode:
        payload.update({'barcode': f.json_dict() for f in passinfo.barcode})
        print("Added barcode")
    if passinfo.heroImage:
        payload.update({"heroImage": { "kind" : "walletobjects#image","sourceUri" : {"uri" : "https://i.imgur.com/I6p54as.png","image": "asdsad", "label" : "heroImg"}}})
        print("Added heroImage")
    if passinfo.textModulesData:
        payload.update({'textModulesData' :[f.json_dict() for f in passinfo.textModulesData]})
        print("Added textModulesData")
    if passinfo.infoModulesData:
        payload.update({'infoModulesData': {'labelValueRows': [{'columns' : [f.json_dict() for f in passinfo.infoModulesData]}], 'showLastUpdateTime': 'true'}})
        print("Added info modules")
    if passinfo.locations:
        payload.update({'locations': [f.json_dict() for f in passinfo.locations]})
        print("Added locations")
        
    print("Done with updating")
    print(json.dumps(payload))

    with open('data.txt', 'w') as outfile:
        json.dump(payload, outfile)  
    
    try:
        return payload
        print("returned from RD")

    except:
        print("Cannot return payload from json_dict")

      

  # Define the resource representation of the Object
  # values should be from your DB/services; here we hardcode information

  # below defines an loyalty object. For more properties, check:
  # https://developers.google.com/pay/passes/reference/v1/loyaltyobject/insert
  # https://developers.google.com/pay/passes/guides/pass-verticals/loyalty/design
    
    #with open('data.txt', 'w') as outfile:
    #    json.dump(json_dict(), outfile)

#   payload = {
#     # required fields
#     "id" : objectId,
#     "classId" : classId,
#     "state" : "active",
#     # optional
#     "accountId": user.idNum,
#     "accountName": user.name,
#     "barcode": {
#         "alternateText": user.idNum,
#         "type": user.barcodeType,
#         "value": user.idNum
#     },
#         "heroImage": {
#             "kind": "walletobjects#image",
#             "sourceUri": {
#                 "uri": "https://i.imgur.com/I6p54as.png",
#                 "image":  user.StudentPhoto,
#                 "label": "heroImg"
#             }
#         },
    
#     "textModulesData": [
#         {
#             "header": "Eagle Bucks",
#             "body": "$" + user.eagle_bucks,
#             "id": "myfield1"
#         },
#         {
#             "header": "Meals Remaining",
#             "body": user.meals_remaining,
#             "id": "myfield2"
#         },
#         {
#             "header": "Kudos",
#             "body": user.kudos_earned + "/" + user.kudos_required,
#             "id": "myfield3"
#         }
#     ],  
#     "infoModuleData": {
    #     "labelValueRows": [
    #     {
    #         "columns": [{
    #             "label": "ID Pin",
    #             "value": user.id_pin
    #         }, 
    #         {
    #             "label": "Print Balance",
    #             "value": user.print_balance
    #         },
         
    #         {
    #             "label": "Mailbox Number",
    #             "value": user.mailbox
    #         }
    #     ],
    #     "showLastUpdateTime": "true"
    # },
    
#     "locations": [{
#         "kind": "walletobjects#latLongPoint",
#         "latitude": 35.613306,
#         "longitude": -97.467825,
#         "label" : "lab"
#       },    
#       {
#         "kind": "walletobjects#latLongPoint",
#         "latitude": 35.611219,
#         "longitude": -97.467255,
#         "label" : "garvey"
#       },
#       {
#         "kind": "walletobjects#latLongPoint",
#         "latitude": 35.61201,
#         "longitude": -97.46850,
#         "label" : "brew"
#       },
#       {
#         "kind": "walletobjects#latLongPoint",
#         "latitude": 35.6115,
#         "longitude":-97.4695,
#         "label" : "branch"
#     }
#   ]      
#  }

    