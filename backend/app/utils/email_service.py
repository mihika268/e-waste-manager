import smtplib
import logging

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr

from flask import current_app


logger = logging.getLogger(__name__)


class EmailService:

    def __init__(self):

        self.smtp_server = (
            current_app.config.get('MAIL_SERVER')
            or 'smtp.gmail.com'
        )

        self.smtp_port = int(
            current_app.config.get('MAIL_PORT')
            or 587
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

        if self.password:
            self.password = (
                self.password
                .replace(' ', '')
                .strip()
            )

        self.default_sender = (
            current_app.config.get(
                'MAIL_DEFAULT_SENDER'
            )
            or self.username
        )


    # ============================================================
    # VALIDATE CONFIGURATION
    # ============================================================

    def _validate_config(self):

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
                "Missing email configuration: %s",
                ", ".join(missing)
            )

            return False

        return True


    # ============================================================
    # CONNECT TO GMAIL
    # ============================================================

    def _connect(self):

        server = smtplib.SMTP(
            self.smtp_server,
            self.smtp_port,
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

        server = None

        try:

            if not self._validate_config():

                return False


            # ----------------------------------------------------
            # CREATE MESSAGE
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
            # ATTACH TEXT + HTML
            # ----------------------------------------------------

            message.attach(
                MIMEText(
                    text_body,
                    'plain',
                    'utf-8'
                )
            )

            message.attach(
                MIMEText(
                    html_body,
                    'html',
                    'utf-8'
                )
            )


            # ----------------------------------------------------
            # CONNECT
            # ----------------------------------------------------

            logger.info(
                "Connecting to Gmail SMTP server %s:%s",
                self.smtp_server,
                self.smtp_port
            )

            server = self._connect()


            # ----------------------------------------------------
            # SEND
            # ----------------------------------------------------

            server.sendmail(
                self.default_sender,
                [to_email],
                message.as_string()
            )


            logger.info(
                "Email successfully sent to %s",
                to_email
            )

            return True


        except smtplib.SMTPAuthenticationError:

            logger.error(
                "Gmail authentication failed. "
                "Make sure MAIL_PASSWORD contains "
                "the Google App Password."
            )

            return False


        except smtplib.SMTPConnectError:

            logger.error(
                "Could not connect to Gmail SMTP server."
            )

            return False


        except smtplib.SMTPException as e:

            logger.error(
                "Gmail SMTP error: %s",
                str(e)
            )

            return False


        except Exception as e:

            logger.exception(
                "Email sending error: %s",
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

        subject = (
            'E-Waste Management System - '
            f'{purpose.title()} Verification Code'
        )


        text_body = f"""
E-Waste Management System

Your verification code is:

{otp_code}

This verification code will expire in 10 minutes.

If you did not request this code, please ignore this email.

Do not share this verification code with anyone.
"""


        html_body = f"""
<!DOCTYPE html>

<html lang="en">

<head>

    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <title>Email Verification</title>

</head>


<body
    style="
        margin:0;
        padding:0;
        background:#f4f7f5;
        font-family:Arial,Helvetica,sans-serif;
    "
>

    <div
        style="
            max-width:600px;
            margin:40px auto;
            background:#ffffff;
            border-radius:12px;
            overflow:hidden;
        "
    >

        <div
            style="
                background:#28a745;
                padding:25px;
                text-align:center;
            "
        >

            <h1
                style="
                    color:#ffffff;
                    margin:0;
                "
            >
                🌱 E-Waste Management
            </h1>

        </div>


        <div
            style="
                padding:35px;
                text-align:center;
            "
        >

            <h2>
                Email Verification
            </h2>


            <p
                style="
                    color:#666666;
                    font-size:16px;
                "
            >
                Your verification code is:
            </p>


            <div
                style="
                    margin:30px auto;
                    padding:20px;
                    max-width:250px;
                    background:#f1fff5;
                    border:2px solid #28a745;
                    border-radius:10px;
                "
            >

                <span
                    style="
                        color:#28a745;
                        font-size:36px;
                        font-weight:bold;
                        letter-spacing:8px;
                    "
                >
                    {otp_code}
                </span>

            </div>


            <p
                style="
                    color:#666666;
                    font-size:14px;
                "
            >
                This code will expire in
                <strong>10 minutes</strong>.
            </p>


            <p
                style="
                    color:#999999;
                    font-size:13px;
                "
            >
                If you did not request this code,
                you can safely ignore this email.
            </p>


            <p
                style="
                    color:#dc3545;
                    font-size:13px;
                    font-weight:bold;
                "
            >
                Never share your verification code
                with anyone.
            </p>

        </div>


        <div
            style="
                padding:20px;
                background:#f8f9fa;
                text-align:center;
            "
        >

            <p
                style="
                    color:#999999;
                    font-size:12px;
                    margin:0;
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

        subject = (
            'Welcome to E-Waste Management System!'
        )


        text_body = f"""
Welcome to E-Waste Management System!

Hi {username},

Your account has been successfully
verified and activated.

You can now use the E-Waste Management System.

🌱♻️
"""


        html_body = f"""
<!DOCTYPE html>

<html lang="en">

<head>

    <meta charset="UTF-8">

    <title>Welcome</title>

</head>


<body
    style="
        font-family:Arial,Helvetica,sans-serif;
        padding:30px;
        background:#f4f7f5;
    "
>

    <div
        style="
            max-width:600px;
            margin:auto;
            background:#ffffff;
            padding:30px;
            border-radius:12px;
        "
    >

        <h2>
            🌱 Welcome to E-Waste Management!
        </h2>


        <p>
            Hi <strong>{username}</strong>,
        </p>


        <p>
            Your account has been successfully
            verified and activated.
        </p>


        <p>
            You can now use the E-Waste Management System.
        </p>


        <p>
            🌱♻️ Start your eco-friendly journey!
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