# JWT Keys Directory

This directory contains JWT signing keys for the application.

## Required Files

- `private.pem` - Private key for signing JWT tokens
- `public.pem` - Public key for verifying JWT tokens

## Generating Keys

To generate new keys, run:

```bash
make generate-keys
```

Or manually:

```bash
# Generate private key
openssl genrsa -out private.pem 2048

# Generate public key
openssl rsa -in private.pem -pubout -out public.pem
```

## Security Note

- Keep private keys secure and never commit them to version control
- Use different keys for different environments
- Rotate keys regularly in production
