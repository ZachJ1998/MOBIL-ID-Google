import config # contains constants
import services
import uuid # std library for unique identifier generation
from jwt import User, Location
import restMethods
import requests

SAVE_LINK = "https://pay.google.com/gp/v/save/" # Save link that uses JWT. See https://developers.google.com/pay/passes/guides/get-started/implementing-the-api/save-to-google-pay#add-link-to-email
verticalType = services.VerticalType.LOYALTY
enteredId = "1524743"
loc = Location(0.0, 0.0)
user = User(enteredId, loc)
user.create()


# your classUid should be a hash based off of pass metadata, for the demo we will use pass-type_class_uniqueid
#classUid = str(verticalType).split('.')[1] + '_CLASS_'+ str(uuid.uuid4()) # CHANGEME
# check Reference API for format of "id" (https://developers.google.com/pay/passes/reference/v1/o).
# must be alphanumeric characters, '.', '_', or '-'.
classId = "3388000000009088928.LOYALTY_CLASS_d8a36821-33d1-4371-bdeb-e0da0d0fbe0b"
#'%s.%s' % (config.ISSUER_ID,classUid)

# your objectUid should be a hash based off of pass metadata, for the demo we will use pass-type_object_uniqueid
# objectUid = str(verticalType).split('.')[1] + '_OBJECT_'+ str(uuid.uuid4()) # CHANGEME
# # check Reference API for format of "id" (https://developers.google.com/pay/passes/reference/v1/).
# # Must be alphanumeric characters, '.', '_', or '-'.
# objectId = "3388000000009088928.LOYALTY_OBJECT_88b04c7c-bf87-476a-aae3-97d3d818a7af"
#'%s.%s' % (config.ISSUER_ID,objectUid)
# object ID for mobiletest = "3388000000009088928.LOYALTY_OBJECT_88b04c7c-bf87-476a-aae3-97d3d818a7af"
# object ID for andrew = "3388000000009088928.LOYALTY_OBJECT_05b05925-1cf6-4fe8-9522-3a922336c252"

def getobjectfromID(enteredID):
  objectUid = str(verticalType).split('.')[1] + '_OBJECT_'+ str(enteredId) # CHANGEME
  # check Reference API for format of "id" (https://developers.google.com/pay/passes/reference/v1/).
  # Must be alphanumeric characters, '.', '_', or '-'.
  objectId = '%s.%s' % (config.ISSUER_ID,objectUid)

  return objectId

linkedID = getobjectfromID(enteredId)

def makePass(verticalType ,classId, linkedID): # This makes the pass based on the type, class ID and Object ID
  objectJwt = services.makeSkinnyJwt(verticalType, classId, linkedID, user, loc)
  if objectJwt is not None:
    print('Here is pass:\n%s%s' % (SAVE_LINK, objectJwt.decode('UTF-8')))

  return

makePass(verticalType, classId, linkedID) # This implements the function above
