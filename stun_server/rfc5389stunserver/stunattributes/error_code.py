from rfc5389stunserver.constants import AttrType, ErrorCodeType
from rfc5389stunserver.stun_attribute import STUNAttribute


class ErrorCode(STUNAttribute):
    def __init__(self, error_code):
        self.type = AttrType.ERROR_CODE
        self.error_code = error_code  # ErrorCodeClass.SERVER_ERROR

    @property
    def error_class(self):
        return self.error_code // 100

    @property
    def error_number(self):
        return self.error_code % 100

    @property
    def reason_phrase(self):
        if self.error_code == ErrorCodeType.TRY_ALTERNATE:
            return 'Try Alternate'
        elif self.error_code == ErrorCodeType.BAD_REQUEST:
            return 'Bad Request'
        elif self.error_code == ErrorCodeType.UNAUTHORIZED:
            return 'Unauthorized'
        elif self.error_code == ErrorCodeType.UNKNOWN_ATTRIBUTE:
            return 'Unknown Attribute'
        elif self.error_code == ErrorCodeType.STALE_NONCE:
            return 'Stable Nonce'
        elif self.error_code == ErrorCodeType.SERVER_ERROR:
            return 'Server Error'

    @property
    def value(self):
        return ((0).to_bytes(2, 'big') + self.error_class.to_bytes(1, 'big') +
                self.error_number.to_bytes(1, 'big') +
                self.reason_phrase.encode('utf-8'))

    @property
    def length(self):
        return 4 + len(self.reason_phrase)
