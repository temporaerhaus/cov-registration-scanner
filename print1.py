# coding=<utf-8>

from escpos.printer import *
import sys
import re
import datetime
import cbor2
import base45
import zlib
import json
import argparse
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
regex = r"BEGIN:VCARDVERSION:4\.0N:.+;.+;.+FN:(.+?)BDAY:.*EMAIL;TYPE=home:(.*?)TEL;TYPE=.+?:(.*?)ADR;TYPE=home:(.*?);(.*?);(.*?);(.*?);(.*?);(.*?)REV:.*"
subst = "\\1\\n\\2\\n\\3\\n\\6, \\9 \\7"

now = datetime.datetime.now()

p.set()                # reset font size
p.text("\x1b\x61\x00")  # align left

match = re.search(regex, vcard)

if match and ((match.group(2) != '') and (match.group(3) != '')):
    printtext = re.sub(regex, subst, vcard)
    countDict[h]["successfulParse"] += 1
elif vcard.startswith("HC1:"):
    decodeAndVerify.decodeVacCert(vcard)
    printtext = vacdata[-260][1]["dob"] + "\n" + vacdata[-260][1]["nam"]["gn"] + " " + vacdata[-260][1]["nam"]["fn"] + \
        "\n\n__________________________________\nTelefon\n\n__________________________________\nStrasse\n\n__________________________________\nOrt"
    countDict[h]["vacCertParse"] += 1
elif vcard.startswith("stats"):
    printtext = ''
    parser = argparse.ArgumentParser(
        description='decides, what and how many stats are printed')
    parser.add_argument('-d', '--daily', help='print the daily stats')
    parser.add_argument('-w', '--weekly', help='print the weekly stats')
    parser.add_argument('-m', '--monthly', help='print the monthly stats')
    parser.add_argument('-a', '--all', help='print all stats (very large)')
    args = parser.parse_args(vcard[6:])
    if args.all:
        printtext += json.dumps(countDict, sort_keys=True, indent=4)
    if args.daily:
        printtext += ("\n" + h + "\n")
        printtext += json.dumps(countDict[h], sort_keys=True, indent=4)
    if args.weekly:
        printtext += ("\nKW: " +
                      datetime.date.today().isocalendar().week + "\n")
        for day in countDict.keys():
            if datetime.date.fromisoformat(day).isocalendar().week == datetime.date.today().isocalendar().week:
                sum = 0
                for i in (countDict[day]).values():
                    sum += i
                printext += day + ": " + str(i) + "\n"

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
