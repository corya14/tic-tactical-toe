# t-t-t
Tic Tactical Toe. Grid-based game with Django.

# Setup/Install Instructions
TODO. Should probably release as docker.

# Run Instructions
Recommended to create a python virtual environment with:
`python3 -m venv ttt`

Activate the venv and install dependencies:
`pip install -r requirements.txt`

To start the Django server:
`python manage.py runserver`

## Generating Self-Signed Certs

```sh
openssl req -x509 -out localhost.crt -keyout localhost.key \
  -newkey rsa:2048 -nodes -sha256 \
  -subj '/CN=localhost' -extensions EXT -config <( \
   printf "[dn]\nCN=localhost\n[req]\ndistinguished_name = dn\n[EXT]\nsubjectAltName=DNS:localhost\nkeyUsage=digitalSignature\nextendedKeyUsage=serverAuth")
```

# Credits
https://learndjango.com/tutorials/
https://github.com/teddziuba/django-sslserver
