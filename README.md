# t-t-t
Tic Tactical Toe. Grid-based game with Django.

# Setup/Install Instructions
TODO. Should probably release as docker.

# Run Instructions
Make sure dependencies are installed:
`pip install -r requirements.txt`

To start the Django server using self-signed keys:
`python manage.py runsslserver --certificate /path/to/certificate.crt --key /path/to/key.key localhost:8000`

## Generating Self-Signed Certs

```sh
openssl req -x509 -out localhost.crt -keyout localhost.key \
  -newkey rsa:2048 -nodes -sha256 \
  -subj '/CN=localhost' -extensions EXT -config <( \
   printf "[dn]\nCN=localhost\n[req]\ndistinguished_name = dn\n[EXT]\nsubjectAltName=DNS:localhost\nkeyUsage=digitalSignature\nextendedKeyUsage=serverAuth")
```
