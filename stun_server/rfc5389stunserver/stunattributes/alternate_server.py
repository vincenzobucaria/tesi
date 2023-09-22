from rfc5389stunserver.constants import AttrType
from rfc5389stunserver.stunattributes.mapped_address import MappedAddress


class AlternateServer(MappedAddress):
    def __init__(self, port: int, ipaddr: str):
        super().__init__(port, ipaddr)
        self.type = AttrType.ALTERNATE_SERVER
