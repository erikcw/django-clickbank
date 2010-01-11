#!/usr/bin/env python

import httplib

KEY = ''
CLERK = ''

conn = httplib.HTTPSConnection('api.clickbank.com')
conn.putrequest('GET', '/api/1.1/orders/list')
conn.putheader("Accept", 'application/xml')
conn.putheader("Authorization", '%s:%s' % (KEY, CLERK))
conn.endheaders()
response = conn.getresponse()

print "%d - %s" % (response.status, response.reason)
print response.read()
