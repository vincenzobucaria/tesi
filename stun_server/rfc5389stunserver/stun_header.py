import logging

from rfc5389stunserver.constants import MsgClass, MethodType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class STUNHeader:
    def __init__(self, transaction_id=bytes(96),
                 msg_class=MsgClass.FAILURE_RESPONSE,
                 method_type=MethodType.BINDING):
        self.message_class = msg_class
        self.message_method = method_type
        self.message_length = 0
        self.magic_cookie = bytes.fromhex('2112A442')
        # self.magic_cookie = socket.htonl(0x2112A442).to_bytes(4, 'big')
        self.transaction_id = transaction_id

    def create_msg_type(self):
        method_high = self.message_method & ~((1 << 7) - 1)
        method_mid = self.message_method & ((1 << 7) - 1) & ~((1 << 4) - 1)
        method_low = self.message_method & ((1 << 4) - 1)
        class_high = self.message_class & 2
        class_low = self.message_class & 1
        return ((method_high << 2) + (method_mid << 1) + method_low +
                (class_high << 7) + (class_low << 4)).to_bytes(2, 'big')

    @property
    def isRfc3489(self):
        return self.magic_cookie != bytes.fromhex('2112A442')

    @property
    def bin(self):
        return (self.create_msg_type() +
                self.message_length.to_bytes(2, 'big') +
                self.magic_cookie + self.transaction_id)

    @staticmethod
    def fromBin(data: bytes):
        stun_header = STUNHeader()
        stun_header.message_length = int.from_bytes(data[2:2+2], 'big')
        stun_header.magic_cookie = data[4:4+4]
        stun_header.transaction_id = data[8:8+12]
        return stun_header
