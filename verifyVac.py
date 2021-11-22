import cbor2
from cose.headers import KID
from cose.messages import CoseMessage
from base45 import b45decode as b45d
from base64 import b64encode as b64e
import zlib

def verify (cert):
	cose = CoseMessage.decode(zlib.decompress(b45d(cert[4:])))
	kid = b64e(cose.phdr.get(KID) or cose.uhdr[KID])
	vacdata = cbor2.loads(cose.payload)
	return False
