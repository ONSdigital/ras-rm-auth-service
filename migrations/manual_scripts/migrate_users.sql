INSERT INTO auth.user(id, username, hashed_password, account_verified, account_locked, failed_logins)
SELECT id, email, password, account_is_verified, account_is_locked, failed_logins
FROM public.credentials_oauthuser;
