import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_server = current_app.config.get('MAIL_SERVER')
        self.smtp_port = current_app.config.get('MAIL_PORT')
        self.use_tls = current_app.config.get('MAIL_USE_TLS')
        self.username = current_app.config.get('MAIL_USERNAME')
        self.password = current_app.config.get('MAIL_PASSWORD')
        self.default_sender = current_app.config.get('MAIL_DEFAULT_SENDER')
    
    def send_otp_email(self, to_email, otp_code, purpose='registration'):
        """Send OTP email to user"""
        try:
            if not self.username or not self.password:
                logger.warning("Email credentials not configured. OTP will be logged instead.")
                logger.info(f"OTP for {to_email}: {otp_code}")
                return True
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.default_sender
            msg['To'] = to_email
            msg['Subject'] = f"E-Waste Management - {purpose.title()} Verification Code"
            
            # Email body
            if purpose == 'registration':
                body = f"""
                <html>
                <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background-color: #f8f9fa; padding: 30px; border-radius: 10px; text-align: center;">
                        <h2 style="color: #28a745; margin-bottom: 20px;">🌱 E-Waste Management System</h2>
                        <h3 style="color: #333; margin-bottom: 20px;">Email Verification</h3>
                        <p style="color: #666; font-size: 16px; margin-bottom: 30px;">
                            Thank you for registering! Please use the following verification code to complete your account setup:
                        </p>
                        <div style="background-color: #fff; padding: 20px; border-radius: 8px; border: 2px solid #28a745; margin: 20px 0;">
                            <h1 style="color: #28a745; font-size: 32px; margin: 0; letter-spacing: 5px;">{otp_code}</h1>
                        </div>
                        <p style="color: #666; font-size: 14px; margin-top: 20px;">
                            This code will expire in 10 minutes. If you didn't request this code, please ignore this email.
                        </p>
                        <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                        <p style="color: #999; font-size: 12px;">
                            This is an automated message from E-Waste Management System. Please do not reply to this email.
                        </p>
                    </div>
                </body>
                </html>
                """
            else:
                body = f"""
                <html>
                <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background-color: #f8f9fa; padding: 30px; border-radius: 10px; text-align: center;">
                        <h2 style="color: #28a745; margin-bottom: 20px;">🌱 E-Waste Management System</h2>
                        <h3 style="color: #333; margin-bottom: 20px;">Verification Code</h3>
                        <p style="color: #666; font-size: 16px; margin-bottom: 30px;">
                            Please use the following verification code:
                        </p>
                        <div style="background-color: #fff; padding: 20px; border-radius: 8px; border: 2px solid #28a745; margin: 20px 0;">
                            <h1 style="color: #28a745; font-size: 32px; margin: 0; letter-spacing: 5px;">{otp_code}</h1>
                        </div>
                        <p style="color: #666; font-size: 14px; margin-top: 20px;">
                            This code will expire in 10 minutes.
                        </p>
                    </div>
                </body>
                </html>
                """
            
            msg.attach(MIMEText(body, 'html'))
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            if self.use_tls:
                server.starttls()
            server.login(self.username, self.password)
            text = msg.as_string()
            server.sendmail(self.default_sender, to_email, text)
            server.quit()
            
            logger.info(f"OTP email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send OTP email to {to_email}: {str(e)}")
            logger.info(f"OTP for {to_email}: {otp_code}")
            return False
    
    def send_welcome_email(self, to_email, username):
        """Send welcome email after successful registration"""
        try:
            if not self.username or not self.password:
                logger.info(f"Welcome email would be sent to {to_email} for user {username}")
                return True
            
            msg = MIMEMultipart()
            msg['From'] = self.default_sender
            msg['To'] = to_email
            msg['Subject'] = "Welcome to E-Waste Management System!"
            
            body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background-color: #f8f9fa; padding: 30px; border-radius: 10px;">
                    <h2 style="color: #28a745; margin-bottom: 20px; text-align: center;">🌱 Welcome to E-Waste Management!</h2>
                    <p style="color: #333; font-size: 16px; margin-bottom: 20px;">
                        Hi {username},
                    </p>
                    <p style="color: #666; font-size: 14px; line-height: 1.6; margin-bottom: 20px;">
                        Welcome to our E-Waste Management System! Your account has been successfully verified and activated.
                    </p>
                    <div style="background-color: #e8f5e8; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <h3 style="color: #28a745; margin-top: 0;">What you can do now:</h3>
                        <ul style="color: #666; font-size: 14px;">
                            <li>Add your e-waste items to track</li>
                            <li>Schedule collection pickups</li>
                            <li>Use our AI scanner to identify waste types</li>
                            <li>Connect with the community</li>
                            <li>Track your environmental impact</li>
                        </ul>
                    </div>
                    <p style="color: #666; font-size: 14px; text-align: center; margin-top: 30px;">
                        Start your eco-friendly journey today! 🌱♻️
                    </p>
                </div>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            if self.use_tls:
                server.starttls()
            server.login(self.username, self.password)
            text = msg.as_string()
            server.sendmail(self.default_sender, to_email, text)
            server.quit()
            
            logger.info(f"Welcome email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send welcome email to {to_email}: {str(e)}")
            return False
