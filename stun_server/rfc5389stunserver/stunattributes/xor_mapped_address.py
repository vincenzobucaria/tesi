import ipaddress
import logging

from rfc5389stunserver.constants import AttrType
from rfc5389stunserver.stunattributes.mapped_address import MappedAddress

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class XorMappedAddress(MappedAddress):
    def __init__(self, port: int, ipaddr: str, transaction_id: bytes = None):
        self.type = AttrType.XOR_MAPPED_ADDRESS
        self.port = port ^ 0x2112
        # v6の場合transactionIDも入る
        self.isIPv6 = ipaddress.ip_address(ipaddr).ipv4_mapped is None
        if self.isIPv6:
            xor_value = (0x2112A442 << 96) + \
                int.from_bytes(transaction_id, 'big')
            ip_value = int(ipaddress.ip_address(ipaddr))
        else:
            xor_value = 0x2112A442
            ip_value = int(ipaddress.ip_address(ipaddr).ipv4_mapped)
        self.ipaddr = ipaddress.ip_address(ip_value ^ xor_value)
