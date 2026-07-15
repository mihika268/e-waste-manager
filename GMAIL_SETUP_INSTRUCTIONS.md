# 📧 Gmail Email Setup Instructions

Follow these steps to configure email for OTP delivery in the E-Waste Management System.

## Step 1: Enable 2-Factor Authentication

1. Go to your **Google Account**: https://myaccount.google.com/security
2. Scroll down to **"2-Step Verification"**
3. Click **"Turn on"**
4. Follow the setup wizard to verify your phone number
5. Complete the verification process

## Step 2: Generate an App Password

1. Go to **App Passwords**: https://myaccount.google.com/apppasswords
   - Or navigate: Google Account → Security → 2-Step Verification → App Passwords
2. You may be asked to sign in again
3. Select **"Mail"** from the **"Select app"** dropdown
4. Select **"Windows Computer"** from the **"Select device"** dropdown
5. Click **"Generate"**
6. You'll see a 16-character password (formatted as: `xxxx xxxx xxxx xxxx`)
7. **Copy this password** (you can remove the spaces or keep them)

## Step 3: Configure in Project

### Option A: Run Setup Script (Recommended)

```bash
python setup_email.py
```

This interactive script will:
- Guide you through the process
- Create the `.env` file automatically
- Save your credentials securely

### Option B: Manual Setup

1. Navigate to the `backend` directory
2. Create a file named `.env`
3. Add the following content:

```env
# Flask Configuration
SECRET_KEY=ewaste-management-secret-key-2024-dev
JWT_SECRET_KEY=jwt-secret-string-development-key

# Email Configuration (for OTP)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-16-char-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com

# OTP Configuration
OTP_EXPIRY_MINUTES=10
OTP_LENGTH=6

# File Upload Configuration
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216
```

4. Replace `your-email@gmail.com` with your actual Gmail address
5. Replace `your-16-char-app-password` with your generated app password

## Step 4: Restart the Server

After configuring email, restart the Flask server:

```bash
# Stop the current server (Ctrl+C)
# Then start it again
python start.py
```

## Step 5: Test Email Delivery

1. Open browser to: http://localhost:5000/register
2. Fill in the registration form with your email
3. Click "Create Account"
4. Check your email inbox for the OTP code
5. Enter the OTP code to verify your account

## Troubleshooting

### "Username and Password not accepted"
- ✅ Make sure you're using an **App Password**, not your regular Gmail password
- ✅ Check that 2-Factor Authentication is enabled
- ✅ Verify the app password was generated for "Mail" and "Windows Computer"

### "Less secure app access" error
- ✅ Google has deprecated less secure apps
- ✅ You MUST use an App Password instead
- ✅ Follow Step 2 again to generate a new app password

### Email not received
- ✅ Check your spam folder
- ✅ Verify the email address in the `.env` file
- ✅ Check console logs for error messages
- ✅ Make sure `.env` file is in the `backend` directory

### Email credentials not loaded
- ✅ Make sure `.env` file is in the `backend` directory
- ✅ Restart the server after creating `.env`
- ✅ Check that there are no typos in the configuration

## Alternative: Use Other Email Providers

If you don't want to use Gmail, you can use other SMTP providers:

### Outlook/Hotmail
```env
MAIL_SERVER=smtp-mail.outlook.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@outlook.com
MAIL_PASSWORD=your-password
```

### SendGrid (requires account)
```env
MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USERNAME=apikey
MAIL_PASSWORD=your-api-key
```

### Mailgun (requires account)
```env
MAIL_SERVER=smtp.mailgun.org
MAIL_PORT=587
MAIL_USERNAME=your-mailgun-username
MAIL_PASSWORD=your-mailgun-password
```

## Security Notes

⚠️ **Important:**
- Never commit `.env` file to version control
- The `.env` file is already in `.gitignore`
- Keep your app password secure
- Don't share your app password with others

## Quick Reference

- **Setup script**: `python setup_email.py`
- **Config file**: `backend/.env`
- **Test registration**: http://localhost:5000/register
- **App password generator**: https://myaccount.google.com/apppasswords

Happy emailing! 📧✨


