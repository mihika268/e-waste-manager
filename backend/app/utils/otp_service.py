from app import db
from app.models.otp import OTP
from app.utils.email_service import EmailService
from flask import current_app
import logging


logger = logging.getLogger(__name__)


class OTPService:

    def __init__(self):
        self.email_service = EmailService()

    # ============================================================
    # GENERATE AND SEND OTP
    # ============================================================

    def generate_and_send_otp(
        self,
        email,
        purpose='registration'
    ):
        try:

            # ----------------------------------------------------
            # Remove expired OTPs
            # ----------------------------------------------------

            OTP.cleanup_expired_otps()

            # ----------------------------------------------------
            # Invalidate previous unused OTPs
            # ----------------------------------------------------

            existing_otps = OTP.query.filter(
                OTP.email == email,
                OTP.purpose == purpose,
                OTP.is_used.is_(False)
            ).all()

            for old_otp in existing_otps:
                old_otp.is_used = True

            db.session.commit()

            # ----------------------------------------------------
            # Generate new OTP
            # ----------------------------------------------------

            expiry_minutes = current_app.config.get(
                'OTP_EXPIRY_MINUTES',
                10
            )

            otp = OTP(
                email=email,
                purpose=purpose,
                expiry_minutes=expiry_minutes
            )

            db.session.add(otp)
            db.session.commit()

            # ----------------------------------------------------
            # Send OTP through Resend
            # ----------------------------------------------------

            email_sent = self.email_service.send_otp_email(
                email,
                otp.otp_code,
                purpose
            )

            # ----------------------------------------------------
            # Email failed
            # ----------------------------------------------------

            if not email_sent:

                logger.error(
                    "OTP email could not be sent to %s",
                    email
                )

                # Delete OTP because user cannot receive it
                db.session.delete(otp)
                db.session.commit()

                return {
                    'success': False,
                    'message': (
                        'Unable to send verification email. '
                        'Please check the email configuration '
                        'and try again.'
                    ),
                    'email_sent': False
                }

            # ----------------------------------------------------
            # Email sent successfully
            # ----------------------------------------------------

            logger.info(
                "OTP email sent successfully to %s",
                email
            )

            return {
                'success': True,
                'message': (
                    'Verification email sent successfully'
                ),
                'otp_id': otp.id,
                'email_sent': True,
                'expires_at': (
                    otp.expires_at.isoformat()
                )
            }

        except Exception as e:

            logger.exception(
                "Error generating/sending OTP for %s: %s",
                email,
                str(e)
            )

            db.session.rollback()

            return {
                'success': False,
                'message': (
                    'Unable to send verification email.'
                ),
                'email_sent': False
            }

    # ============================================================
    # VERIFY OTP
    # ============================================================

    def verify_otp(
        self,
        email,
        otp_code,
        purpose='registration'
    ):
        try:

            # ----------------------------------------------------
            # Find valid OTP
            # ----------------------------------------------------

            otp = OTP.query.filter(
                OTP.email == email,
                OTP.otp_code == otp_code,
                OTP.purpose == purpose,
                OTP.is_used.is_(False),
                OTP.expires_at > db.func.now()
            ).first()

            # ----------------------------------------------------
            # Invalid / expired OTP
            # ----------------------------------------------------

            if not otp:

                logger.warning(
                    "Invalid or expired OTP for %s",
                    email
                )

                return {
                    'success': False,
                    'message': (
                        'Invalid or expired OTP'
                    )
                }

            # ----------------------------------------------------
            # Mark OTP as used
            # ----------------------------------------------------

            otp.is_used = True

            db.session.commit()

            logger.info(
                "OTP verified successfully for %s",
                email
            )

            return {
                'success': True,
                'message': (
                    'OTP verified successfully'
                )
            }

        except Exception as e:

            logger.exception(
                "OTP verification error for %s: %s",
                email,
                str(e)
            )

            db.session.rollback()

            return {
                'success': False,
                'message': (
                    'Unable to verify OTP'
                )
            }

    # ============================================================
    # RESEND OTP
    # ============================================================

    def resend_otp(
        self,
        email,
        purpose='registration'
    ):
        try:

            # ----------------------------------------------------
            # Invalidate existing OTPs
            # ----------------------------------------------------

            existing_otps = OTP.query.filter(
                OTP.email == email,
                OTP.purpose == purpose,
                OTP.is_used.is_(False)
            ).all()

            for otp in existing_otps:
                otp.is_used = True

            db.session.commit()

            logger.info(
                "Previous OTPs invalidated for %s",
                email
            )

            # ----------------------------------------------------
            # Generate and send new OTP
            # ----------------------------------------------------

            return self.generate_and_send_otp(
                email,
                purpose
            )

        except Exception as e:

            logger.exception(
                "Resend OTP error for %s: %s",
                email,
                str(e)
            )

            db.session.rollback()

            return {
                'success': False,
                'message': (
                    'Unable to resend verification email'
                ),
                'email_sent': False
            }

    # ============================================================
    # CLEANUP EXPIRED OTPs
    # ============================================================

    def cleanup_expired_otps(self):

        try:

            count = OTP.cleanup_expired_otps()

            logger.info(
                "Cleaned up %s expired OTPs",
                count
            )

            return count

        except Exception as e:

            logger.exception(
                "OTP cleanup error: %s",
                str(e)
            )

            return 0