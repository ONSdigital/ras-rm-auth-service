INSERT INTO auth.user(id, username, hashed_password, account_verified, account_locked, failed_logins, last_login_date)
SELECT id, email, password, account_is_verified, account_is_locked, failed_logins, last_login_date
FROM public.credentials_oauthuser;
