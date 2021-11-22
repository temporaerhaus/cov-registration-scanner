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

countFile = open('countFile.json', 'r')
countJson = countFile.readlines()[0]
countFile.close()
countDict = json.loads(countJson)
h = datetime.date.today().isoformat()
if(h not in countDict):
    countDict[h] = {}
if("successfulParse" not in countDict[h]):
    countDict[h]["successfulParse"] = 0
    countDict[h]["unsuccessfulParse"] = 0
    countDict[h]["empty"] = 0
    countDict[h]["vacCertParse"] = 0

vcard = " ".join(sys.argv[1:])
print(vcard)

getMatch = lambda x : (lambda m : m[1] if (m is not None) else "")(re.search(x, vcard))

vcname = getMatch("FN:(.+?)BDAY:")
vcmail = getMatch("EMAIL;TYPE=home:(.*?)TEL;")
vctel = getMatch("TEL;TYPE=.+?:(.*?)ADR;")
vcaddr = (lambda m : "{}, {} {}".format(m[3], m[6], m[4]) if (m is not None) else "")(re.search("ADR;TYPE=home:(.*?);(.*?);(.*?);(.*?);(.*?);(.*?)REV:", vcard))

now = datetime.datetime.now()

p.set()                # reset font size
p.text("\x1b\x61\x00")  # align left

if (vctel == "") and (vcmail == ""):
    printtext = "Es muss entweder eine Telefonnummer oder eine E-Mail Adresse angegeben werden.\n\n{}\n\n__________________________________\nTelefon\n\n{}".format(vcname, vcaddr)
    countDict[h]["unsuccessfulParse"] += 1
elif (vcname != "") and (vcaddr != ""):
    printtext = ("{0}\n{1}\n{3}" if (vctel == "") else ("{0}\n{2}\n{3}" if (vcmail == "") else "{}\n{} {}\n{}")).format(vcname, vcmail, vctel, vcaddr)
    countDict[h]["successfulParse"] += 1
elif vcard.startswith("HC1:"):
    decodeAndVerify.decodeVacCert(vcard)
    printtext = vacdata[-260][1]["dob"] + "\n" + vacdata[-260][1]["nam"]["gn"] + " " + vacdata[-260][1]["nam"]["fn"] + \
        "\n\n__________________________________\nTelefon\n\n__________________________________\nStrasse\n\n__________________________________\nOrt"
    countDict[h]["vacCertParse"] += 1
elif vcard == "stats":
    printtext = json.dumps(countDict, sort_keys=True, indent=4)
elif len(vcard) > 3:
    countDict[h]["unsuccessfulParse"] += 1
    printtext = "\n\n__________________________________\nName\n\n__________________________________\nTelefon\n\n__________________________________\nStrasse\n\n__________________________________\nOrt"
else:
    # printtext = vcard
    printtext = "\n\n__________________________________\nName\n\n__________________________________\nTelefon\n\n__________________________________\nStrasse\n\n__________________________________\nOrt"
    countDict[h]["empty"] += 1

printtext.replace("Ä", "Ae")
printtext.replace("Ö", "Öe")
printtext.replace("Ü", "Üe")
printtext.replace("ẞ", "SS")
printtext.replace("ä", "ae")
printtext.replace("ö", "oe")
printtext.replace("ü", "ue")
printtext.replace("ß", "ss")

p.text(str(now))
p.text("\n")
p.text(printtext)
# p.text("\n\n__________________________________\nCheckout Uhrzeit")
p.cut()

p.text("\x1b\x40\x1b\x61\x01")  # initialize, align center
p.image("logo.gif", 'false', 'false', 'bitImageColumn', 20000000)

p.set(height=2, width=2)
p.text("Anwesenheitsregistrierung\n\n")

countFile = open('countFile.json', 'w')
countFile.write(json.dumps(countDict))
countFile.close()
