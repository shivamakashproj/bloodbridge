# Forgot Password Feature Documentation

## Overview
The *Forgot Password* feature allows any user (admin, hoster, donor) to reset their account password securely when they have forgotten it.

## How It Works
1. **User clicks “Forgot password?”** on the login page.
2. The user is taken to **`/reset_password`** where they enter their registered email address.
3. The server validates the email format. If a matching user exists, a **signed, time‑limited token** is generated using `itsdangerous.URLSafeTimedSerializer` with the application `SECRET_KEY`.
4. In this demo the reset link is shown via a flash message; in production you would email the link to the user.
5. The user follows the link to **`/reset_password/<token>`**.
6. The token is verified (signature + expiry – 1 hour). If the token is invalid or expired, the user is redirected back to the request page.
7. Upon successful verification a form to **set a new password** is displayed.
8. The user submits a new password that meets the password policy (`is_valid_password`).
9. The password hash in the `User` model (`password_hash`) is updated with `generate_password_hash` and the change is committed to the database.
10. The user is notified that the password was reset and can now log in with the new credentials.

## Key Files
| File | Purpose |
|------|---------|
| `app.py` | Added imports (`itsdangerous`), routes `/reset_password` and `/reset_password/<token>` and integrated them after the logout view. |
| `templates/login.html` | Added a “Forgot password?” link that points to `/reset_password`. |
| `templates/reset_password_request.html` | Form where the user supplies their email address. |
| `templates/reset_password.html` | Form for entering the new password after token verification. |

## Security Details
- **Token Generation**: `URLSafeTimedSerializer(app.config['SECRET_KEY']).dumps(email, salt='password-reset-salt')`.
- **Token Verification**: `loads(..., max_age=3600)` – token is valid for **1 hour** only.
- **Signature**: Uses the app’s `SECRET_KEY` and a dedicated salt, preventing token reuse across different purposes.
- **Password Policy**: Re‑uses the same regex (`is_valid_password`) as registration/login, enforcing a strong password.
- **No Role Check**: The flow does not depend on the user's role, making it universal for all accounts.

## Usage
1. Navigate to the login page (e.g., `http://localhost:5000/login?role=donor`).
2. Click **Forgot password?**.
3. Enter your email and submit.
4. Copy the reset link shown in the flash message (or, in production, click the link from your email).
5. Set a new password that satisfies the policy.
6. Log in with the new password.

## Extending to Real Email Delivery
Replace the flash‑message part in `reset_password_request` with an email‑sending routine, e.g. using **Flask‑Mail**:
```python
msg = Message('Password Reset', recipients=[user.email])
msg.body = f'Click the link to reset your password: {reset_link}'
mail.send(msg)
```

## Reference
- Routes are defined in **`app.py`** around line 418‑473.
- Templates are located under `templates/`.
- Token handling uses `itsdangerous` which is already imported.

---
*Generated automatically by Antigravity on 2026‑10‑23.*
