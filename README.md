# t-t-t
Tic Tactical Toe. Grid-based game with Django.

# manage.py Commands
All commands are preceeded by `python manage.py`
| Purpose | Command |
| ------- | ------- |
| Reset games DB | `migrate game zero`
| Reload/restore DB | `migrate`
| Run server | `runserver`

# Local Insecure Dev/Test Run Instructions
Recommended to create a python virtual environment with:
```sh
python3 -m venv ttt
```

Activate the venv and install dependencies:
```sh
pip install -r requirements.txt
```

DB Setup:
```sh
python3 manage.py makemigrations
python3 manage.py migrate
```

To start the Django server:
```sh
python manage.py runserver
```

## Generating Self-Signed Certs

```sh
openssl req -x509 -out localhost-TEST.crt -keyout localhost-TEST.key \
  -newkey rsa:2048 -nodes -sha256 \
  -subj '/CN=localhost' -extensions EXT -config <( \
   printf "[dn]\nCN=localhost\n[req]\ndistinguished_name = dn\n[EXT]\nsubjectAltName=DNS:localhost\nkeyUsage=digitalSignature\nextendedKeyUsage=serverAuth")
```

# Test Secure Deployment
## Build the Docker
This requires the files `localhost-TEST.crt` and `localhost-TEST.key` to exist locally.

### Build With Django Generated Secret Key
This requires Django to be installed outside of the docker. If you don't want to do that, see the next option.
```sh
docker build --build-arg DJANGO_SECRET_KEY=`python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'` --tag ttt:latest .
```

### Build With Your Own Secret Key (Less Secure)
Insert your own key below in place of YOURSECRETKEY. You may use the debug secret key for testing purposes: `django-insecure-9!i$^80-ivi7kml_a2t%_7qve&tk8kbsy=l+)1y!1t42-i^f%i`

```sh
docker build --build-arg DJANGO_SECRET_KEY=YOURSECRETKEY --tag ttt:latest .
```

### Running the Docker
```sh
docker run -it -d --name ttt -p 4443:443 ttt
```

Navigate to `https://localhost:4443`. Recommended browser: Chrome (accepts self signed root certs)

# Credits
 * https://learndjango.com/tutorials/
 * https://channels.readthedocs.io/
 * https://github.com/codyparker/channels-obstruction
