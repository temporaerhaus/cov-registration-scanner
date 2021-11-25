import cbor2
from cose.headers import KID
from cose.messages import CoseMessage
from base45 import b45decode as b45d
from base64 import b64encode as b64e
from zlib import decompress as unz
import json

def verify (cert):
	try:
		cose = CoseMessage.decode(unz(b45d(cert[4:])))
		kid = b64e(cose.phdr.get(KID) or cose.uhdr[KID]).decode()
		vacdata = cbor2.loads(cose.payload)
		cert = vacdata[-260][1]

		certs = json.load(open("DSCs.json", "r"))
		
		thisCert = None

		for c in certs["certificates"]:
			if c["kid"] == kid:
				thisCert = c
				break

		if (thisCert is None):
			return {"valid": False, "data": "No matching certificate was found"}

		name = cert["nam"]["gn"] + " " + cert["nam"]["fn"]
		return {"valid": True, "data": {"name": name}}
	except Exception as e:
		return {"valid": False, "data": e}

if (__name__ == "__main__"):
	exit