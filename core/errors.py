
from rest_framework.exceptions import APIException

class ContentError(APIException):
    status_code = 409
    default_detail = 'Content Error.'
    default_code = 'content_error'
