#!/usr/bin/env python

from app import app
# context = ('domain.crt', 'domain.key')

HOST = '0.0.0.0'
DEBUG = True
if __name__ == "__main__":
    app.run(debug = DEBUG, 
            host  = HOST)