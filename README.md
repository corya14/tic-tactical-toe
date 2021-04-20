# t-t-t
Tic Tactical Toe. Grid-based game with Django.

# Setup/Install Instructions
TODO. Should probably release as docker.

# Local Insecure Dev/Test Run Instructions
Recommended to create a python virtual environment with:
`python3 -m venv ttt`

Activate the venv and install dependencies:
`pip install -r requirements.txt`

To start the Django server:
`python manage.py runserver`

## Generating Self-Signed Certs

```sh
openssl req -x509 -out localhost-TEST.crt -keyout localhost-TEST.key \
  -newkey rsa:2048 -nodes -sha256 \
  -subj '/CN=localhost' -extensions EXT -config <( \
   printf "[dn]\nCN=localhost\n[req]\ndistinguished_name = dn\n[EXT]\nsubjectAltName=DNS:localhost\nkeyUsage=digitalSignature\nextendedKeyUsage=serverAuth")
```

# Test Secure Deployment
This requires the files `localhost-TEST.crt` and `localhost-TEST.key` to exist locally.
`docker build --tag ttt:latest .`
`docker run -it -d --name ttt -p 4443:443 ttt`

Navigate to `https://localhost:4443`. Recommended browser: Chrome (accepts self signed root certs)

# Credits
 * https://learndjango.com/tutorials/
 * https://channels.readthedocs.io/
