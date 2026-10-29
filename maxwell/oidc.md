# One sign-in: terminals-tech Supabase account into the Maxwell workspace

Supabase Auth on project `zkdfziipgtswwlkpkyvv` acts as the OpenID Connect provider.
The fork's own OIDC client (`processcraft/directory/oidc.py`) talks to it unchanged.

## Why this path

- Issuer `https://zkdfziipgtswwlkpkyvv.supabase.co/auth/v1` already serves
  `/.well-known/openid-configuration` (issuer matches, authorize, token, jwks, userinfo,
  PKCE S256) and a JWKS with one ES256 key. Read 2026-10-29 with curl.
- `auth.oauth_clients` already holds two clients ("terminals OS", "Tin Market"), and
  `/oauth/authorize` answers `oauth_client_not_found` for an unknown id, so the OAuth 2.1
  server is on.
- The ID token carries `sub`, `aud` = client id, `nonce`, `email`, `email_verified` (Supabase
  docs, OAuth 2.1 Flows). The fork requires exactly issuer, aud, sub, exp, nonce and an
  asymmetric alg (`processcraft/directory/jose.py`).
- The three accounts are email/password users (`raw_app_meta_data.providers = ["email"]`),
  not Google identities, and terminals.tech has no MX record, so Google cannot be the issuer.

## What `maxwell/oidc.py` sets

| field | value |
|---|---|
| issuer | `https://zkdfziipgtswwlkpkyvv.supabase.co/auth/v1` |
| scopes | `openid email profile` |
| username_claim | `email` |
| groups_claim | `sub` (one rule per auth.users id is the allowlist) |
| rules | tej `23006b19-4317-487b-a969-9bdab0edcd15` admin, nick `7523c6de-60e1-4e59-8868-cc593eee27d8` editor, raul `3609e836-ba9b-4459-b37a-6bf7a0f9476e` editor |
| unmatched | `deny` (the project has 40 users; the other 37 are refused) |
| identity binding | `set_identity(<seat>, "oidc", <sub>)`, so the callback finds `tej`, `nick`, `raul` by sub |

The binding clears the seat's password hash in the users table (`processcraft/auth/users.py`
`set_identity`). Tej keeps the installation password from `PLANTCRAFT_BASIC_AUTH_PASSWORD_FILE`
as the way in when Supabase is down. Nick and Raul then sign in only through Supabase.

## Live steps that need operator approval

1. Supabase dashboard, project terminals-tech, Authentication > OAuth Apps > Add a new client:
   - name `Maxwell Plant`
   - type `Confidential`, token auth `client_secret_basic`
   - redirect URIs: `http://127.0.0.1:8765/api/sso/oidc/callback` and
     `<PUBLIC_URL>/api/sso/oidc/callback` for the address Nick and Raul open
     (`serve.sh` binds loopback; that address is not set anywhere in this repo).
   Record the client id; save the secret (shown once) to
   `~/.local/share/maxwell-plant/seats/supabase-oidc.secret`, mode 600.
2. Confirm Authentication > OAuth Server > Authorization Path plus Site URL lands on the
   consent page (source: `terminals-os-corpus/app/(app)/oauth/consent/page.tsx`, which sends
   a signed-out user to `/auth/login`). Not verified live: terminals.tech answered 429.
3. Apply to the live workspace (writes `workspace.sqlite3` and `directory-secrets.json`):
   ```
   cd /var/home/zero/maxwell-plant
   .venv/bin/python -m maxwell.seats --scenario scenarios/maxwell.json
   .venv/bin/python -m maxwell.oidc --client-id <CLIENT_ID> \
     --client-secret-file ~/.local/share/maxwell-plant/seats/supabase-oidc.secret \
     --public-url <PUBLIC_URL>
   ```
   No restart: the settings row is read on each request.
4. Settings page "Test" (or `GET /api/sso/methods` shows `"oidc": true`), then each person
   clicks "Sign in with terminals.tech".

Rollback: Settings > corporate sign-in > OIDC off; `users.set_identity(<seat>, "local", None)`
and `python -m maxwell.seats` after deleting `seats/<name>.password` to issue new passwords.

## Check

`.venv/bin/python -m pytest tests/test_maxwell_oidc.py -q -p no:cacheprovider` drives the
fork's real `/api/sso/oidc/start` and `/callback` routes against a stub with the live
discovery shape and an ES256 key.
