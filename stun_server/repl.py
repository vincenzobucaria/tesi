import ipaddress
import logging
import hashlib
import hmac
import socket

from rfc5389stunserver.saslprep import SASLprep
from rfc5389stunserver.stunattributes.mapped_address import MappedAddress
from rfc5389stunserver.stunattributes.xor_mapped_address import XorMappedAddress
from rfc5389stunserver.stunattributes.unknown_attributes import UnknownAttributes
from rfc5389stunserver.stun_attribute import STUNAttribute
from rfc5389stunserver.stun_header import STUNHeader, MsgClass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    s = STUNHeader()
    # print(s.magic_cookie + s.transaction_id)
    # print(socket.htonl(0x2112A442))
    # print(socket.ntohl(0x2112A442))
    # print(MsgClass.SUCCESS_RESPONSE + 7)
    # print(s.message_method + 0)
    print(s.create_msg_type().hex())
    print(s.bin.hex())

    sa = STUNAttribute()
    print(sa.bin.hex())

    ma = MappedAddress(32767, 0xabcdef01)
    print(len(ma.value))
    print(ma.bin.hex())
    xma = XorMappedAddress(32767, 0xabcdef01)
    print(len(xma.value))
    print(xma.bin.hex())

    print(SASLprep.saslprep('Hello, world!　こんにちは世界ー'))
    print(hashlib.md5('Hello world!'.encode('utf-8')).hexdigest())
    print(hmac.new('key'.encode('utf-8'),
                   'Hello world!'.encode('utf-8'), 'sha1').hexdigest())

    print(len(ipaddress.ip_address('3.3.3.3').packed))

    print(len('こんにちは世界'))
    print(len('こんにちは世界'.encode('utf-8')))

    ua = UnknownAttributes([5, 3, 0xabc])
    print(ua.length)
    print(ua.value.hex())
