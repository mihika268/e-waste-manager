import smtplib
import logging

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

from flask import current_app


logger = logging.getLogger(__name__)


class EmailService:

    def __init__(self):
        """Load Gmail SMTP configuration from Flask config."""

        self.smtp_server = current_app.config.get(
            'MAIL_SERVER'
        )

        self.smtp_port = current_app.config.get(
            'MAIL_PORT',
            587
        )

        self.use_tls = current_app.config.get(
            'MAIL_USE_TLS',
            True
        )

        self.username = current_app.config.get(
            'MAIL_USERNAME'
        )

        self.password = current_app.config.get(
            'MAIL_PASSWORD'
        )

        self.default_sender = current_app.config.get(
            'MAIL_DEFAULT_SENDER'
        ) or self.username

    # ============================================================
    # VALIDATE EMAIL CONFIGURATION
    # ============================================================

    def _validate_config(self):
        """Validate Gmail SMTP configuration."""

        missing = []

        if not self.smtp_server:
            missing.append('MAIL_SERVER')

        if not self.smtp_port:
            missing.append('MAIL_PORT')

        if not self.username:
            missing.append('MAIL_USERNAME')

        if not self.password:
            missing.append('MAIL_PASSWORD')

        if not self.default_sender:
            missing.append('MAIL_DEFAULT_SENDER')

        if missing:
            logger.error(
                'Missing email configuration: %s',
                ', '.join(missing)
            )

            return False

        return True

    # ============================================================
    # CREATE SMTP CONNECTION
    # ============================================================

    def _connect(self):
        """Connect and authenticate with Gmail SMTP."""

        server = smtplib.SMTP(
            self.smtp_server,
            int(self.smtp_port),
            timeout=30
        )

        server.ehlo()

        if self.use_tls:
            server.starttls()
            server.ehlo()

        server.login(
            self.username,
            self.password
        )

        return server

    # ============================================================
    # SEND EMAIL
    # ============================================================

    def _send_email(
        self,
        to_email,
        subject,
        text_body,
        html_body
    ):
        """Send an email using Gmail SMTP."""

        server = None

        try:

            # ----------------------------------------------------
            # Validate configuration
            # ----------------------------------------------------

            if not self._validate_config():

                logger.error(
                    'Email cannot be sent because '
                    'SMTP configuration is incomplete.'
                )

                return False

            # ----------------------------------------------------
            # Create email message
            # ----------------------------------------------------

            message = MIMEMultipart(
                'alternative'
            )

            message['From'] = formataddr(
                (
                    'E-Waste Management System',
                    self.default_sender
                )
            )

            message['To'] = to_email

            message['Subject'] = subject

            # ----------------------------------------------------
            # Attach plain text
            # ----------------------------------------------------

            message.attach(
                MIMEText(
                    text_body,
                    'plain',
                    'utf-8'
                )
            )

            # ----------------------------------------------------
            # Attach HTML
            # ----------------------------------------------------

            message.attach(
                MIMEText(
                    html_body,
                    'html',
                    'utf-8'
                )
            )

            # ----------------------------------------------------
            # Connect to Gmail
            # ----------------------------------------------------

            logger.info(
                'Connecting to SMTP server %s:%s',
                self.smtp_server,
                self.smtp_port
            )

            server = self._connect()

            # ----------------------------------------------------
            # Send email
            # ----------------------------------------------------

            server.sendmail(
                self.default_sender,
                [to_email],
                message.as_string()
            )

            logger.info(
                'Email sent successfully to %s',
                to_email
            )

            return True

        except smtplib.SMTPAuthenticationError:

            logger.error(
                'Gmail SMTP authentication failed. '
                'Make sure MAIL_USERNAME is correct and '
                'MAIL_PASSWORD contains a valid Gmail App Password.'
            )

            return False

        except smtplib.SMTPConnectError:

            logger.error(
                'Could not connect to Gmail SMTP server.'
            )

            return False

        except smtplib.SMTPServerDisconnected:

            logger.error(
                'Gmail SMTP server disconnected unexpectedly.'
            )

            return False

        except smtplib.SMTPException as e:

            logger.error(
                'SMTP error while sending email: %s',
                str(e)
            )

            return False

        except Exception as e:

            logger.exception(
                'Unexpected error while sending email: %s',
                str(e)
            )

            return False

        finally:

            if server:

                try:
                    server.quit()

                except Exception:
                    pass

    # ============================================================
    # SEND OTP EMAIL
    # ============================================================

    def send_otp_email(
        self,
        to_email,
        otp_code,
        purpose='registration'
    ):
        """Send OTP verification email."""

        subject = (
            'E-Waste Management System - '
            f'{purpose.title()} Verification Code'
        )

        # --------------------------------------------------------
        # Plain text email
        # --------------------------------------------------------

        text_body = f"""
E-Waste Management System

Your verification code is:

{otp_code}

This verification code will expire in 10 minutes.

If you did not request this code, please ignore this email.

Do not share this verification code with anyone.
"""

        # --------------------------------------------------------
        # HTML email
        # --------------------------------------------------------

        html_body = f"""
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <title>
        Email Verification
    </title>
</head>

<body
    style="
        margin: 0;
        padding: 0;
        background-color: #f4f7f5;
        font-family: Arial, Helvetica, sans-serif;
    "
>

    <div
        style="
            max-width: 600px;
            margin: 40px auto;
            background-color: #ffffff;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        "
    >

        <!-- Header -->

        <div
            style="
                background-color: #28a745;
                padding: 25px;
                text-align: center;
            "
        >

            <h1
                style="
                    color: #ffffff;
                    margin: 0;
                    font-size: 24px;
                "
            >
                🌱 E-Waste Management
            </h1>

        </div>

        <!-- Content -->

        <div
            style="
                padding: 35px;
                text-align: center;
            "
        >

            <h2
                style="
                    color: #333333;
                    margin-top: 0;
                "
            >
                Email Verification
            </h2>

            <p
                style="
                    color: #666666;
                    font-size: 16px;
                    line-height: 1.6;
                "
            >
                Thank you for registering with the
                E-Waste Management System.
            </p>

            <p
                style="
                    color: #666666;
                    font-size: 16px;
                    line-height: 1.6;
                "
            >
                Please use the verification code below
                to complete your registration.
            </p>

            <!-- OTP -->

            <div
                style="
                    margin: 30px auto;
                    padding: 20px;
                    background-color: #f8fff9;
                    border: 2px solid #28a745;
                    border-radius: 10px;
                    max-width: 250px;
                "
            >

                <div
                    style="
                        color: #28a745;
                        font-size: 36px;
                        font-weight: bold;
                        letter-spacing: 8px;
                    "
                >
                    {otp_code}
                </div>

            </div>

            <p
                style="
                    color: #666666;
                    font-size: 14px;
                "
            >
                This code will expire in
                <strong>10 minutes</strong>.
            </p>

            <p
                style="
                    color: #999999;
                    font-size: 13px;
                    margin-top: 25px;
                "
            >
                If you did not request this verification
                code, you can safely ignore this email.
            </p>

            <p
                style="
                    color: #dc3545;
                    font-size: 13px;
                    font-weight: bold;
                "
            >
                Never share your verification code with anyone.
            </p>

        </div>

        <!-- Footer -->

        <div
            style="
                padding: 20px;
                background-color: #f8f9fa;
                text-align: center;
            "
        >

            <p
                style="
                    color: #999999;
                    font-size: 12px;
                    margin: 0;
                "
            >
                This is an automated email from
                E-Waste Management System.
            </p>

        </div>

    </div>

</body>

</html>
"""

        return self._send_email(
            to_email,
            subject,
            text_body,
            html_body
        )

    # ============================================================
    # SEND WELCOME EMAIL
    # ============================================================

    def send_welcome_email(
        self,
        to_email,
        username
    ):
        """Send welcome email after successful registration."""

        subject = (
            'Welcome to E-Waste Management System!'
        )

        # --------------------------------------------------------
        # Plain text
        # --------------------------------------------------------

        text_body = f"""
Welcome to E-Waste Management System!

Hi {username},

Your account has been successfully verified
and activated.

You can now:

- Add your e-waste items
- Schedule collection pickups
- Use the AI scanner
- Connect with the community
- Track your environmental impact

Start your eco-friendly journey today!

🌱♻️
"""

        # --------------------------------------------------------
        # HTML
        # --------------------------------------------------------

        html_body = f"""
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <title>
        Welcome
    </title>
</head>

<body
    style="
        margin: 0;
        padding: 30px;
        background-color: #f4f7f5;
        font-family: Arial, Helvetica, sans-serif;
    "
>

    <div
        style="
            max-width: 600px;
            margin: auto;
            background-color: #ffffff;
            padding: 35px;
            border-radius: 12px;
        "
    >

        <h1
            style="
                color: #28a745;
                text-align: center;
            "
        >
            🌱 Welcome to E-Waste Management!
        </h1>

        <p
            style="
                color: #333333;
                font-size: 16px;
            "
        >
            Hi {username},
        </p>

        <p
            style="
                color: #666666;
                font-size: 15px;
                line-height: 1.6;
            "
        >
            Your account has been successfully
            verified and activated.
        </p>

        <h3
            style="
                color: #28a745;
            "
        >
            What you can do now:
        </h3>

        <ul
            style="
                color: #666666;
                line-height: 1.8;
            "
        >
            <li>Add your e-waste items</li>
            <li>Schedule collection pickups</li>
            <li>Use the AI scanner</li>
            <li>Connect with the community</li>
            <li>Track your environmental impact</li>
        </ul>

        <p
            style="
                color: #666666;
                text-align: center;
                margin-top: 30px;
            "
        >
            Start your eco-friendly journey today!
            🌱♻️
        </p>

    </div>

</body>

</html>
"""

        return self._send_email(
            to_email,
            subject,
            text_body,
            html_body
        )