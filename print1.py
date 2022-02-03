# coding=<utf-8>

from escpos.printer import *
import sys
import re
import datetime
import json
import argparse
# from escpos.constants import *
from verifyVac import verify as verifyVac


def getMatch(x, vcard): return (lambda m: m[1] if (
    m is not None) else "")(re.search(x, vcard))


def main(vcard):
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

    #
    print(vcard)

    vcname = getMatch("FN:(.+?)BDAY:", vcard)
    vcmail = getMatch("EMAIL;TYPE=home:(.*?)TEL;", vcard)
    vctel = getMatch("TEL;TYPE=.+?:(.*?)ADR;", vcard)
    vcaddr = (lambda m: "{}, {} {}".format(m[3], m[6], m[4]) if (m is not None) else "")(
        re.search("ADR;TYPE=home:(.*?);(.*?);(.*?);(.*?);(.*?);(.*?)REV:", vcard))

    now = datetime.datetime.now()

    p.set()                # reset font size
    p.text("\x1b\x61\x00")  # align left

    if vcard.startswith("stats"):
        printtext = ''
        from matplotlib import pyplot as plt

        parser = argparse.ArgumentParser(
            description='decides, what and how many stats are printed')
        parser.add_argument(
            '-d', '--daily', help='print the daily stats', action='store_true')
        parser.add_argument(
            '-w', '--weekly', help='print the weekly stats', action='store_true')
        parser.add_argument('-m', '--monthly',
                            help='print the monthly stats', action='store_true')
        parser.add_argument(
            '-a', '--all', help='print all stats (very large)', action='store_true')
        args = parser.parse_args([vcard[6:]])
        if args.all:
            printtext += json.dumps(countDict, sort_keys=True, indent=4)
        if args.daily:
            printtext += ("\n" + h + "\n")
            printtext += json.dumps(countDict[h], sort_keys=True, indent=4)
        if args.weekly:
            printtext += ("\nKW: " +
                          str(datetime.date.today().isocalendar()[1]) + "\n")
            for day in countDict.keys():
                if datetime.date.fromisoformat(day).isocalendar()[1] == datetime.date.today().isocalendar()[1]:
                    s = 0
                    for i in (countDict[day]).values():
                        s += i
                    printtext += day + ": " + str(s) + "\n"
        if args.monthly:
            people = {}
            for day in countDict.keys():
                if datetime.date.fromisoformat(day).month == datetime.date.today().month:
                    s = 0
                    for i in (countDict[day]).values():
                        s += i
                    people[datetime.date.fromisoformat(day).day] = s
            plt.bar(people.keys(), people.values())
            plt.savefig('chart.png')
            p.image("chart.png", 'false', 'false', 'bitImageColumn', 20000000)
    elif vcard.startswith("HC1:"):
        vac = verifyVac(vcard)
        if vac["valid"]:
            printtext = vac["data"]["name"] + \
                "\n\n__________________________________\nTelefon\n\n__________________________________\nStrasse\n\n__________________________________\nOrt"
            countDict[h]["vacCertParse"] += 1
        else:
            printtext = vac["data"] + "\n\n__________________________________\nName\n\n__________________________________\nTelefon\n\n__________________________________\nStrasse\n\n__________________________________\nOrt"
            countDict[h]["unsuccessfulParse"] += 1
    elif (vctel == "") and (vcmail == "") and (vcard != ""):
        printtext = "Es muss entweder eine Telefonnummer oder eine E-Mail Adresse angegeben werden.\n\n{}\n\n__________________________________\nTelefon\n\n{}".format(
            vcname, vcaddr)
        countDict[h]["unsuccessfulParse"] += 1
    elif (vcname != "") and (vcaddr != ""):
        printtext = ("{0}\n{1}\n{3}" if (vctel == "") else ("{0}\n{2}\n{3}" if (
            vcmail == "") else "{}\n{} {}\n{}")).format(vcname, vcmail, vctel, vcaddr)
        countDict[h]["successfulParse"] += 1
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
    print(printtext)

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


if __name__ == "__main__":
    main(" ".join(sys.argv[1:]))
