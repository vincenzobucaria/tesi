import logging
import socket

from rfc5389stunserver.constants import MsgClass, MethodType, AttrType
from rfc5389stunserver.stunattributes.mapped_address import MappedAddress
from rfc5389stunserver.stunattributes.xor_mapped_address import XorMappedAddress
from rfc5389stunserver.stun_header import STUNHeader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Parser:
    @staticmethod
    def parse(header: bytes, payload: bytes, address: tuple):
        req_stun_header = STUNHeader.fromBin(header)
        print(f'Header is {header.hex()}')
        print(f'Address is {address}')
        logger.info(f'Header length is {req_stun_header.message_length}')
        logger.info(f'Maggic cookie is {req_stun_header.magic_cookie.hex()}')
        logger.info(
            f'Transaction ID is {req_stun_header.transaction_id.hex()}')

        if req_stun_header.isRfc3489:
            mapped_address = MappedAddress(address[1], address[0])
        else:
            mapped_address = XorMappedAddress(
                address[1], address[0], req_stun_header.transaction_id)

        res_stun_header = STUNHeader(req_stun_header.transaction_id,
                                     MsgClass.SUCCESS_RESPONSE,
                                     MethodType.BINDING)
        res_stun_header.message_length = 4 + mapped_address.length

        if len(payload) > 0:
            index = 0
            while index < len(payload):
                logger.info('---STUN Attr---')
                attr_type = int.from_bytes(payload[index:index+2], 'big')
                attr_len = int.from_bytes(payload[index+2:index+4], 'big')
                try:
                    logger.info(f'AttrType: {AttrType(attr_type).name}')
                except ValueError:
                    logger.error(
                        f'AttrType: Unknown ({attr_type} ({hex(attr_type)}))')
                logger.info(f'Length: {attr_len}')
                print()
                index += 4 + attr_len + (4 - attr_len % 4) % 4
        print()

        return [res_stun_header, mapped_address]
