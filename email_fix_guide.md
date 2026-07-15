# 🔧 Fix Email Delivery Issue - Gmail App Password Setup

## Problem Identified
The error `5.7.8 Username and Password not accepted` indicates that Gmail is rejecting the login attempt because you're using your regular Gmail password instead of an **App Password**.

## Solution: Generate Gmail App Password

### Step 1: Enable 2-Factor Authentication (2FA)
1. Go to your Google Account settings: https://myaccount.google.com/
2. Click on **Security** in the left sidebar
3. Under "Signing in to Google", click **2-Step Verification**
4. Follow the prompts to enable 2FA (if not already enabled)

### Step 2: Generate App Password
1. After enabling 2FA, go back to **Security** settings
2. Under "Signing in to Google", click **App passwords**
3. At the bottom, click **Select app** → Choose **Mail**
4. Click **Select device** → Choose **Other (Custom name)**
5. Enter name: `E-Waste Management System`
6. Click **Generate**
7. Copy the 16-character password (it looks like: `abcd efgh ijkl mnop`)

### Step 3: Update Your .env File
Replace your current email password in `backend/.env`:

```bash
# Current (incorrect):
MAIL_PASSWORD=yrwffcrldffebpvr

# Replace with your new 16-character app password:
MAIL_PASSWORD=abcd efgh ijkl mnop  # Use your actual app password
```

### Step 4: Restart the Application
```bash
# Stop the current server (Ctrl+C)
# Then restart:
cd c:\Users\HP\OneDrive\Desktop\e-waste\backend
python run.py
```

## Alternative Solutions (If Gmail App Password Doesn't Work)

### Option 1: Use a Test Email Service (Development)
For development/testing, you can use a temporary email service:

```bash
# Update .env with a test email service
MAIL_SERVER=smtp.mailtrap.io
MAIL_PORT=2525
MAIL_USERNAME=your_mailtrap_username
MAIL_PASSWORD=your_mailtrap_password
MAIL_USE_TLS=true
```

### Option 2: Check Email Logs
The application logs OTP codes for testing purposes. Check your backend logs:

```bash
# Look for this message in the logs:
"OTP generated but email failed for [email]"
"OTP for [email]: [6-digit-code]"
```

### Option 3: Use Console Logging (Development Only)
For development, you can disable email sending and use console logging:

```bash
# In .env, leave email credentials empty:
MAIL_USERNAME=
MAIL_PASSWORD=
```

The app will then log OTP codes to the console for testing.

## Test Your Fix
After updating the app password, test the registration:

1. Go to http://localhost:5000/register
2. Enter your email and click "Send OTP"
3. Check your email for the 6-digit code
4. Enter the code in the registration form

## Need Help?
If you continue to have issues:
1. Double-check the app password is copied correctly (no spaces when pasting)
2. Ensure 2FA is properly enabled on your Google account
3. Try generating a new app password
4. Check Gmail's security settings for any blocks