import hashlib
import hmac

from rfc5389stunserver.constants import AttrType
from rfc5389stunserver.saslprep import SASLprep
from rfc5389stunserver.stun_attribute import STUNAttribute

'''
The MESSAGE-INTEGRITY attribute contains an HMAC-SHA1 [RFC2104]
of the STUN message.
'''


class MessageIntegrity(STUNAttribute):
    def __init__(self, text, term_type, password, username=None, realm=None):
        self.type = AttrType.MESSEAGE_INTEGRITY
        self.length = 20
        if term_type == 'short-term':  # tmp
            # username/realm/password 引用符と後ろのNULLを取り除く
            key = hashlib.md5(f'{username}:{realm}:{password}').digest()
        elif term_type == 'long-term':
            key = SASLprep.saslprep(password)  # .encode('utf-8')
        # textはこの属性より前のヘッダも含んだ全て
        # 長さはこの属性までになるように検証時に調整が必要
        self.value = hmac.new(key, text, 'sha1').digest()

    @property
    def len(self):
        return len(self.value)
