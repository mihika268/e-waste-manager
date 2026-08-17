import logging
import requests

from flask import current_app


logger = logging.getLogger(__name__)


class EmailService:

    def __init__(self):

        # ========================================================
        # RESEND CONFIGURATION
        # ========================================================

        self.resend_api_key = current_app.config.get(
            'RESEND_API_KEY'
        )

        self.resend_from_email = current_app.config.get(
            'RESEND_FROM_EMAIL'
        ) or 'onboarding@resend.dev'


    # ============================================================
    # VALIDATE CONFIGURATION
    # ============================================================

    def _validate_config(self):

        if not self.resend_api_key:

            logger.error(
                'Missing RESEND_API_KEY'
            )

            return False

        if not self.resend_from_email:

            logger.error(
                'Missing RESEND_FROM_EMAIL'
            )

            return False

        return True


    # ============================================================
    # SEND EMAIL THROUGH RESEND
    # ============================================================

    def _send_email(
        self,
        to_email,
        subject,
        text_body,
        html_body
    ):

        try:

            if not self._validate_config():

                return False


            # ----------------------------------------------------
            # RESEND API REQUEST
            # ----------------------------------------------------

            response = requests.post(
                'https://api.resend.com/emails',

                headers={
                    'Authorization':
                        f'Bearer {self.resend_api_key}',

                    'Content-Type':
                        'application/json'
                },

                json={

                    'from':
                        f'E-Waste Management System '
                        f'<{self.resend_from_email}>',

                    'to': [
                        to_email
                    ],

                    'subject':
                        subject,

                    'text':
                        text_body,

                    'html':
                        html_body
                },

                timeout=20
            )


            # ----------------------------------------------------
            # SUCCESS
            # ----------------------------------------------------

            if 200 <= response.status_code < 300:

                logger.info(
                    'Email successfully sent to %s',
                    to_email
                )

                return True


            # ----------------------------------------------------
            # RESEND ERROR
            # ----------------------------------------------------

            logger.error(
                'Resend API error: HTTP %s - %s',
                response.status_code,
                response.text
            )

            return False


        except requests.RequestException as e:

            logger.error(
                'Resend connection error: %s',
                str(e)
            )

            return False


        except Exception as e:

            logger.exception(
                'Unexpected email error: %s',
                str(e)
            )

            return False


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


        # --------------------------------------------------------
        # PLAIN TEXT EMAIL
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
        # HTML EMAIL
        # --------------------------------------------------------

        html_body = f"""
<!DOCTYPE html>

<html>

<head>

    <meta charset="UTF-8">

    <title>
        Email Verification
    </title>

</head>


<body style="
    margin:0;
    padding:0;
    background:#f4f7f5;
    font-family:Arial,sans-serif;
">


    <div style="
        max-width:600px;
        margin:40px auto;
        background:white;
        border-radius:12px;
        overflow:hidden;
    ">


        <!-- HEADER -->

        <div style="
            background:#28a745;
            padding:25px;
            text-align:center;
        ">

            <h1 style="
                color:white;
                margin:0;
            ">

                🌱 E-Waste Management

            </h1>

        </div>


        <!-- CONTENT -->

        <div style="
            padding:35px;
            text-align:center;
        ">


            <h2>
                Email Verification
            </h2>


            <p style="
                color:#666;
                font-size:16px;
            ">

                Thank you for registering with
                E-Waste Management System.

            </p>


            <p style="
                color:#666;
                font-size:16px;
            ">

                Your verification code is:

            </p>


            <!-- OTP -->

            <div style="
                margin:30px auto;
                padding:20px;
                background:#f8fff9;
                border:2px solid #28a745;
                border-radius:10px;
                max-width:250px;
            ">

                <div style="
                    color:#28a745;
                    font-size:36px;
                    font-weight:bold;
                    letter-spacing:8px;
                ">

                    {otp_code}

                </div>

            </div>


            <p style="
                color:#666;
                font-size:14px;
            ">

                This code will expire in
                <strong>10 minutes</strong>.

            </p>


            <p style="
                color:#999;
                font-size:13px;
            ">

                If you did not request this code,
                you can safely ignore this email.

            </p>


            <p style="
                color:#dc3545;
                font-size:13px;
                font-weight:bold;
            ">

                Never share your verification code.

            </p>


        </div>


        <!-- FOOTER -->

        <div style="
            padding:20px;
            background:#f8f9fa;
            text-align:center;
        ">

            <p style="
                color:#999;
                font-size:12px;
                margin:0;
            ">

                Automated email from
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


        # --------------------------------------------------------
        # PLAIN TEXT EMAIL
        # --------------------------------------------------------

        text_body = f"""
Welcome to E-Waste Management System!

Hi {username},

Your account has been successfully verified.

You can now use the E-Waste Management System.

Thank you!
"""


        # --------------------------------------------------------
        # HTML EMAIL
        # --------------------------------------------------------

        html_body = f"""
<!DOCTYPE html>

<html>

<head>

    <meta charset="UTF-8">

    <title>
        Welcome
    </title>

</head>


<body style="
    font-family:Arial,sans-serif;
    background:#f4f7f5;
    padding:30px;
">


    <div style="
        max-width:600px;
        margin:auto;
        background:white;
        padding:30px;
        border-radius:12px;
    ">


        <h1 style="
            color:#28a745;
        ">

            🌱 Welcome to E-Waste Management!

        </h1>


        <p>

            Hi {username},

        </p>


        <p>

            Your account has been successfully
            verified and activated.

        </p>


        <p>

            You can now use all available
            features of the E-Waste Management System.

        </p>


        <p>

            🌱♻️ Thank you for helping manage
            e-waste responsibly.

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