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
objectUid = str(verticalType).split('.')[1] + '_OBJECT_'+ str(uuid.uuid4()) # CHANGEME
# check Reference API for format of "id" (https://developers.google.com/pay/passes/reference/v1/).
# Must be alphanumeric characters, '.', '_', or '-'.
objectId = "3388000000009088928.LOYALTY_OBJECT_f829ef5d-7f6a-4234-9d93-17fbf4da021a"
# '%s.%s' % (config.ISSUER_ID,objectUid)


def makePass(verticalType ,classId, objectId): # This makes the pass based on the type, class ID and Object ID
  objectJwt = services.makeSkinnyJwt(verticalType, classId, objectId, user, loc)
  if objectJwt is not None:
    print('Here is pass:\n%s%s' % (SAVE_LINK, objectJwt.decode('UTF-8')))

  return

makePass(verticalType, classId, objectId) # This implements the function above
