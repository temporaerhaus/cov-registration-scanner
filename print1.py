# coding=<utf-8>

import sys
import re
import datetime
import cbor2
import base45
import zlib
import json
from escpos.printer import *
# from escpos.constants import *

p = Serial('/dev/ttyUSB0', 19200)


vcard = " ".join(sys.argv[1:])
regex = r"BEGIN:VCARDVERSION:4\.0N:.+;.+;.+FN:(.+?)BDAY:.*EMAIL;TYPE=home:(.*?)TEL;TYPE=.+?:(.+?)ADR;TYPE=home:(.*?);(.*?);(.*?);(.*?);(.*?);(.*?)REV:.*"
subst = "\\1\\n\\2\\n\\3\\n\\6, \\9 \\7"

now = datetime.datetime.now()

p.set()                # reset font size
p.text("\x1b\x61\x00")  # align left

match = re.search(regex, vcard)

if match:
    printtext = re.sub(regex, subst, vcard)
elif vcard.startswith("HC1:"):
    vd = cbor2.loads(zlib.decompress(
        base45.b45decode(vcard.replace("HC1:", ""))))
    vacdata = cbor2.loads(vd.value[2])
    print(vacdata)
    print(vacdata[-260][1]["v"]["dob"] + "\n" + vacdata[-260][1]["v"]
          ["nam"]["gn"] + " " + vacdata[-260][1]["v"]["nam"]["fn"])
else:
    # printtext = vcard
    printtext = "\n\n__________________________________\nName\n\n__________________________________\nTelefon\n\n__________________________________\nStrasse\n\n__________________________________\nOrt"
p.text(str(now))
p.text("\n")
p.text(printtext)
# p.text("\n\n__________________________________\nCheckout Uhrzeit")
p.cut()

p.text("\x1b\x40\x1b\x61\x01")  # initialize, align center
p.image("logo.gif", 'false', 'false', 'bitImageColumn', 20000000)

p.set(height=2, width=2)
p.text("Anwesenheitsregistrierung\n\n")
