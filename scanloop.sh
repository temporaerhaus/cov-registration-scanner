#!/bin/bash

while true
do
  read vcard
  echo "$vcard"
  python3 print1.py "$vcard"
  clear
done
