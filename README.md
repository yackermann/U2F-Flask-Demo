DISCONTINUED! PLEASE MOVE TO WEBAUTHN! https://medium.com/@herrjemand/introduction-to-webauthn-api-5fd1fb46c285
===

## How to cook it?

Initialize virtual environment

```
virtualenv venv
source ./venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Initialize Database

```bash
python create_db.py
```

Generate private key and certificate for SSL

```bash
openssl req -newkey rsa:2048 -nodes -keyout domain.key -x509 -days 365 -out domain.crt
```

Generate new cookie master key

```bash
python reset_cookie_key.py
```

Run application

```bash
./run.py
```

## TODO

 - [ ] Write API docs
 - [x] Implement facets support
 - [x] Documentation
 - [ ] Unit tests

## License

[MIT](https://github.com/herrjemand/U2F-Flask-Demo/blob/master/LICENSE.md) © [Yuriy Ackermann](https://jeman.de/)
