import os, base64
with open('COOKEY.key', 'w') as w:
    w.write(base64.b64encode(os.urandom(48)).decode('utf-8'))