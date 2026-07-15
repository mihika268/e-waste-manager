from app import db
from app.models.otp import OTP
from app.models.user import User
from app.utils.email_service import EmailService
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class OTPService:
    def __init__(self):
        self.email_service = EmailService()
    
    def generate_and_send_otp(self, email, purpose='registration'):
        """Generate OTP and send it via email"""
        try:
            # Clean up expired OTPs first
            OTP.cleanup_expired_otps()
            
            # Check if there's already a valid OTP for this email and purpose
            existing_otp = OTP.query.filter(
                OTP.email == email,
                OTP.purpose == purpose,
                OTP.is_used == False,
                OTP.expires_at > db.func.now()
            ).first()
            
            if existing_otp:
                # Resend the existing OTP
                logger.info(f"Resending existing OTP for {email}")
                success = self.email_service.send_otp_email(email, existing_otp.otp_code, purpose)
                if success:
                    return {
                        'success': True,
                        'message': 'OTP sent successfully',
                        'otp_id': existing_otp.id,
                        'expires_at': existing_otp.expires_at.isoformat(),
                        'otp_code': existing_otp.otp_code  # Always include OTP in response for development
                    }
                else:
                    return {
                        'success': True,
                        'message': 'OTP generated. Check console/logs for the code if email failed.',
                        'otp_id': existing_otp.id,
                        'expires_at': existing_otp.expires_at.isoformat(),
                        'otp_code': existing_otp.otp_code  # Include OTP in response for development
                    }
            
            # Create new OTP
            expiry_minutes = current_app.config.get('OTP_EXPIRY_MINUTES', 10)
            otp = OTP(email=email, purpose=purpose, expiry_minutes=expiry_minutes)
            
            db.session.add(otp)
            db.session.commit()
            
            # Send OTP via email
            success = self.email_service.send_otp_email(email, otp.otp_code, purpose)
            
            if success:
                logger.info(f"OTP generated and sent successfully for {email}")
                return {
                    'success': True,
                    'message': 'OTP sent successfully',
                    'otp_id': otp.id,
                    'expires_at': otp.expires_at.isoformat(),
                    'otp_code': otp.otp_code  # Always include OTP in response for development
                }
            else:
                # Even if email fails, OTP is still valid for manual verification
                logger.warning(f"OTP generated but email failed for {email}")
                return {
                    'success': True,
                    'message': 'OTP generated. Check console/logs for the code if email failed.',
                    'otp_id': otp.id,
                    'expires_at': otp.expires_at.isoformat(),
                    'otp_code': otp.otp_code  # Include OTP in response for development
                }
                
        except Exception as e:
            logger.error(f"Error generating OTP for {email}: {str(e)}")
            db.session.rollback()
            return {
                'success': False,
                'message': f'Error generating OTP: {str(e)}'
            }
    
    def verify_otp(self, email, otp_code, purpose='registration'):
        """Verify OTP code"""
        try:
            # Find valid OTP
            otp = OTP.query.filter(
                OTP.email == email,
                OTP.otp_code == otp_code,
                OTP.purpose == purpose,
                OTP.is_used == False,
                OTP.expires_at > db.func.now()
            ).first()
            
            if not otp:
                return {
                    'success': False,
                    'message': 'Invalid or expired OTP'
                }
            
            # Mark OTP as used
            otp.mark_as_used()
            
            logger.info(f"OTP verified successfully for {email}")
            return {
                'success': True,
                'message': 'OTP verified successfully'
            }
            
        except Exception as e:
            logger.error(f"Error verifying OTP for {email}: {str(e)}")
            return {
                'success': False,
                'message': f'Error verifying OTP: {str(e)}'
            }
    
    def resend_otp(self, email, purpose='registration'):
        """Resend OTP for the same email and purpose"""
        try:
            # Invalidate existing OTPs for this email and purpose
            existing_otps = OTP.query.filter(
                OTP.email == email,
                OTP.purpose == purpose,
                OTP.is_used == False
            ).all()
            
            for otp in existing_otps:
                otp.is_used = True
            
            db.session.commit()
            
            # Generate and send new OTP
            return self.generate_and_send_otp(email, purpose)
            
        except Exception as e:
            logger.error(f"Error resending OTP for {email}: {str(e)}")
            db.session.rollback()
            return {
                'success': False,
                'message': f'Error resending OTP: {str(e)}'
            }
    
    def cleanup_expired_otps(self):
        """Clean up expired OTPs"""
        try:
            count = OTP.cleanup_expired_otps()
            logger.info(f"Cleaned up {count} expired OTPs")
            return count
        except Exception as e:
            logger.error(f"Error cleaning up expired OTPs: {str(e)}")
            return 0
