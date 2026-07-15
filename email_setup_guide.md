# Email Setup Guide for OTP Sending

## Current Status
✅ Email service is implemented and integrated  
✅ Backend routes are configured  
✅ OTP service uses email notifications  
⚠️ Gmail authentication issue detected

## The Issue
The system is trying to send emails but Gmail is rejecting the authentication. This is happening because:

**Error**: `Username and Password not accepted`

## Solution Steps

### 1. Enable 2-Factor Authentication (2FA)
1. Go to your Google Account settings
2. Navigate to Security → 2-Step Verification
3. Enable 2FA (you'll need to verify your phone number)

### 2. Generate App Password
1. Go to: https://myaccount.google.com/apppasswords
2. Click "Select app" → "Mail" 
3. Click "Select device" → "Windows Computer"
4. Click "Generate"
5. Copy the 16-character password (it looks like: xxxx xxxx xxxx xxxx)

### 3. Update Configuration
1. Open `backend/.env`
2. Replace the `MAIL_PASSWORD` value with your new app password
3. Save the file
4. Restart the backend server

### 4. Test the Setup
Run the test script again:
```bash
python test_email_sending.py
```

## How It Works
- When a user registers, they enter their email
- The system generates a 6-digit OTP
- An email is sent to the user with the OTP code
- The user enters the OTP to complete registration
- The system verifies the OTP and creates the account

## Current Email Template
The system sends emails with this format:
- **Subject**: "Your E-Waste Management OTP Code"
- **Content**: Personalized message with the OTP code and expiry time

## Next Steps
Once you fix the Gmail authentication, the OTP emails will be sent automatically when users register on the platform.