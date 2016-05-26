#!/usr/bin/env python

from app import app
context = ('domain.crt', 'domain.key')
app.run(debug=True, ssl_context=context)