#!/bin/bash
curl "https://de.dscg.ubirch.com/trustList/DSC/" -Ssl | tail -qn1 > DSCs.json
