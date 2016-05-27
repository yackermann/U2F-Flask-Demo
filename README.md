FIDO U2F Flask Demo
===

## How to cook it?

Initialize virtual environment

```
$ virtualenv venv && venv
$ source ./venv/bin/activate
```

Initialize Database

```bash
$ python create_db.py
```


Generate new cookie master key

```bash
$ python reset_cookie_key.py
```

Run application

```bash
$ python run.py
```

## TODO

 - [ ] Write API docs
 - [ ] Implement facets support
 - [ ] Documentation

## License

[MIT](https://github.com/herrniemand/U2F-Flask-Demo/blob/master/LICENSE.md) © [Yuriy Ackermann](https://nieman.de/)