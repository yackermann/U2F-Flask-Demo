#!/usr/bin/env python

# from OpenSSL import SSL
# context = SSL.Context(SSL.SSLv23_METHOD)
# context.use_privatekey_file('domain.key')
# context.use_certificate_file('domain.crt')

from app import app
context = ('domain.crt', 'domain.key')
app.run(debug=True, ssl_context=context)