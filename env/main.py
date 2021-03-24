import config # contains constants
import services
import uuid # std library for unique identifier generation
from jwt import User

SAVE_LINK = "https://pay.google.com/gp/v/save/" # Save link that uses JWT. See https://developers.google.com/pay/passes/guides/get-started/implementing-the-api/save-to-google-pay#add-link-to-email
verticalType = services.VerticalType.LOYALTY
enteredId = "1524743"
user = User(enteredId)
user.create()


# your classUid should be a hash based off of pass metadata, for the demo we will use pass-type_class_uniqueid
# classUid = str(verticalType).split('.')[1] + '_CLASS_'+ str(uuid.uuid4()) # CHANGEME
# check Reference API for format of "id" (https://developers.google.com/pay/passes/reference/v1/o).
# must be alphanumeric characters, '.', '_', or '-'.
classId = "3388000000009088928.LOYALTY_CLASS_d8d0d3d9-bda9-4f2a-8736-abb391b3f63a"
#'%s.%s' % (config.ISSUER_ID,classUid)

# your objectUid should be a hash based off of pass metadata, for the demo we will use pass-type_object_uniqueid
objectUid = str(verticalType).split('.')[1] + '_OBJECT_'+ str(uuid.uuid4()) # CHANGEME
# check Reference API for format of "id" (https://developers.google.com/pay/passes/reference/v1/).
# Must be alphanumeric characters, '.', '_', or '-'.
objectId = '%s.%s' % (config.ISSUER_ID,objectUid)

def makePass(verticalType ,classId, objectId):
  objectJwt = services.makeSkinnyJwt(verticalType, classId, objectId, user)
  if objectJwt is not None:
    print('Here is pass:\n%s%s' % (SAVE_LINK, objectJwt.decode('UTF-8')))

  return

makePass(verticalType, classId, objectId)
