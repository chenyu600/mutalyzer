#!/usr/bin/env python

from mutalyzer.util import monkey_patch_suds; monkey_patch_suds()

import sys
from suds.client import Client
from suds import WebFault

URL = 'http://localhost/mutalyzer/services/?wsdl'

if len(sys.argv) < 2:
    print 'Please provide a gene symbol'
    sys.exit(1)

c = Client(URL, cache=None)
o = c.service

print 'Slicing chromosome for gene ' + sys.argv[1] + ' (Human, 5000 upstream, 2000 downstream) ...'

try:
    r = o.sliceChromosomeByGene(sys.argv[1], 'Human', 5000, 2000)
    print r
except WebFault as message:
    print message
