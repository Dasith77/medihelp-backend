import logging
from typing import List, Optional
from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr

from app.config import settings

logger = logging.getLogger(__name__)

# Email configuration
mail_config = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME or "",
    MAIL_PASSWORD=settings.MAIL_PASSWORD or "",
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.MAIL_USE_CREDENTIALS,
    TEMPLATE_FOLDER=Path(__file__).parent.parent / "templates" / "email",
)

fast_mail = FastMail(mail_config)


class EmailService:
    @staticmethod
    async def send_booking_confirmation(
        recipient_emails: List[str],
        booking_reference: str,
        doctor_name: str,
        doctor_specialization: str,
        booking_date: str,
        session_time: str,
        patients: List[dict],
        tracking_url: str,
    ) -> bool:
        """
        Send booking confirmation email with tracking link.

        Args:
            recipient_emails: List of email addresses to send to
            booking_reference: Booking reference number (e.g., BK-XXXXXXXX)
            doctor_name: Name of the doctor
            doctor_specialization: Doctor's specialization
            booking_date: Formatted date string
            session_time: Session time range
            patients: List of patient dicts with name, queue_number, approximate_time
            tracking_url: URL to track the booking

        Returns:
            True if email sent successfully, False otherwise
        """
        if not settings.MAIL_ENABLED:
            logger.info(f"Email disabled. Would send to: {recipient_emails}")
            return False

        try:
            # Build HTML email content
            html_content = EmailService._build_confirmation_email(
                booking_reference=booking_reference,
                doctor_name=doctor_name,
                doctor_specialization=doctor_specialization,
                booking_date=booking_date,
                session_time=session_time,
                patients=patients,
                tracking_url=tracking_url,
            )

            message = MessageSchema(
                subject=f"Booking Confirmed - {booking_reference} | MediHelp",
                recipients=recipient_emails,
                body=html_content,
                subtype=MessageType.html,
            )

            await fast_mail.send_message(message)
            logger.info(f"Booking confirmation email sent to: {recipient_emails}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False

    @staticmethod
    def _build_confirmation_email(
        booking_reference: str,
        doctor_name: str,
        doctor_specialization: str,
        booking_date: str,
        session_time: str,
        patients: List[dict],
        tracking_url: str,
    ) -> str:
        """Build HTML email content for booking confirmation."""

        # Build patients list HTML
        patients_html = ""
        for patient in patients:
            patients_html += f"""
            <tr>
                <td style="padding: 12px; border-bottom: 1px solid #e5e7eb;">
                    <div style="display: flex; align-items: center;">
                        <div style="width: 32px; height: 32px; background-color: #dbeafe; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 12px; font-weight: bold; color: #2563eb;">
                            {patient['queue_number']}
                        </div>
                        <div>
                            <div style="font-weight: 500;">{patient['name']}</div>
                            <div style="font-size: 12px; color: #6b7280;">Queue #{patient['queue_number']} • ~{patient['approximate_time']}</div>
                        </div>
                    </div>
                </td>
            </tr>
            """

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Booking Confirmation</title>
</head>
<body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f3f4f6;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <!-- Header -->
        <div style="background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%); border-radius: 12px 12px 0 0; padding: 30px; text-align: center;">
            <h1 style="color: white; margin: 0; font-size: 24px;">Booking Confirmed!</h1>
            <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0;">Your appointment has been successfully booked</p>
        </div>

        <!-- Content -->
        <div style="background-color: white; padding: 30px; border-radius: 0 0 12px 12px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
            <!-- Reference Number -->
            <div style="background-color: #f0f9ff; border: 2px dashed #2563eb; border-radius: 8px; padding: 20px; text-align: center; margin-bottom: 24px;">
                <p style="margin: 0 0 8px 0; color: #6b7280; font-size: 14px;">Booking Reference</p>
                <p style="margin: 0; font-size: 28px; font-weight: bold; color: #2563eb; letter-spacing: 2px;">{booking_reference}</p>
            </div>

            <!-- Doctor Info -->
            <div style="background-color: #f9fafb; border-radius: 8px; padding: 16px; margin-bottom: 24px;">
                <div style="display: flex; align-items: center;">
                    <div style="width: 48px; height: 48px; background-color: #e5e7eb; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 16px;">
                        <span style="font-size: 20px;">👨‍⚕️</span>
                    </div>
                    <div>
                        <p style="margin: 0; font-weight: 600; font-size: 16px;">{doctor_name}</p>
                        <p style="margin: 4px 0 0 0; color: #6b7280; font-size: 14px;">{doctor_specialization}</p>
                    </div>
                </div>
            </div>

            <!-- Appointment Details -->
            <div style="margin-bottom: 24px;">
                <h3 style="margin: 0 0 16px 0; font-size: 16px; color: #374151;">Appointment Details</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 8px 0; color: #6b7280;">📅 Date</td>
                        <td style="padding: 8px 0; text-align: right; font-weight: 500;">{booking_date}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; color: #6b7280;">🕐 Session Time</td>
                        <td style="padding: 8px 0; text-align: right; font-weight: 500;">{session_time}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; color: #6b7280;">💳 Payment</td>
                        <td style="padding: 8px 0; text-align: right;">
                            <span style="background-color: #fef3c7; color: #d97706; padding: 4px 8px; border-radius: 4px; font-size: 12px;">Cash on Arrival</span>
                        </td>
                    </tr>
                </table>
            </div>

            <!-- Patients -->
            <div style="margin-bottom: 24px;">
                <h3 style="margin: 0 0 16px 0; font-size: 16px; color: #374151;">Patients ({len(patients)})</h3>
                <table style="width: 100%; border-collapse: collapse; background-color: #f9fafb; border-radius: 8px;">
                    {patients_html}
                </table>
            </div>

            <!-- Track Button -->
            <div style="text-align: center; margin: 32px 0;">
                <a href="{tracking_url}" style="display: inline-block; background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%); color: white; text-decoration: none; padding: 14px 32px; border-radius: 8px; font-weight: 600; font-size: 16px;">
                    🔍 Track Your Queue
                </a>
            </div>

            <!-- Tracking Link -->
            <div style="background-color: #f3f4f6; border-radius: 8px; padding: 16px; margin-bottom: 24px;">
                <p style="margin: 0 0 8px 0; font-size: 12px; color: #6b7280;">Or copy this tracking link:</p>
                <p style="margin: 0; font-size: 12px; color: #2563eb; word-break: break-all;">{tracking_url}</p>
            </div>

            <!-- Instructions -->
            <div style="border-top: 1px solid #e5e7eb; padding-top: 24px;">
                <h4 style="margin: 0 0 12px 0; font-size: 14px; color: #374151;">📋 Important Instructions</h4>
                <ul style="margin: 0; padding-left: 20px; color: #6b7280; font-size: 14px; line-height: 1.6;">
                    <li>Please arrive 15 minutes before your approximate time</li>
                    <li>Bring this email or your reference number</li>
                    <li>Use the tracking link to check real-time queue status</li>
                    <li>For cancellations, please notify at least 2 hours in advance</li>
                </ul>
            </div>
        </div>

        <!-- Footer -->
        <div style="text-align: center; padding: 24px; color: #6b7280; font-size: 12px;">
            <p style="margin: 0 0 8px 0;">© 2024 MediHelp. All rights reserved.</p>
            <p style="margin: 0;">This is an automated email. Please do not reply directly.</p>
        </div>
    </div>
</body>
</html>
        """
        return html

    @staticmethod
    async def send_queue_update(
        recipient_emails: List[str],
        booking_reference: str,
        patient_name: str,
        queue_number: int,
        current_queue: int,
        tracking_url: str,
    ) -> bool:
        """Send queue update notification email."""
        if not settings.MAIL_ENABLED:
            logger.info(f"Email disabled. Would send queue update to: {recipient_emails}")
            return False

        try:
            positions_ahead = queue_number - current_queue
            status_message = "It's your turn!" if positions_ahead <= 0 else f"{positions_ahead} patient(s) ahead of you"

            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Queue Update</title>
</head>
<body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f3f4f6;">
    <div style="max-width: 500px; margin: 0 auto; padding: 20px;">
        <div style="background-color: white; border-radius: 12px; padding: 30px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); text-align: center;">
            <div style="font-size: 48px; margin-bottom: 16px;">{"🔔" if positions_ahead > 0 else "✅"}</div>
            <h2 style="margin: 0 0 8px 0; color: #374151;">Queue Update</h2>
            <p style="margin: 0 0 24px 0; color: #6b7280;">Ref: {booking_reference}</p>

            <div style="background-color: #f0f9ff; border-radius: 8px; padding: 20px; margin-bottom: 24px;">
                <p style="margin: 0 0 8px 0; color: #6b7280; font-size: 14px;">Current Queue Number</p>
                <p style="margin: 0; font-size: 48px; font-weight: bold; color: #2563eb;">{current_queue}</p>
            </div>

            <p style="margin: 0 0 8px 0; color: #374151;">Hi {patient_name},</p>
            <p style="margin: 0 0 24px 0; color: #6b7280;">Your queue number is <strong>#{queue_number}</strong></p>
            <p style="margin: 0 0 24px 0; font-size: 18px; font-weight: 600; color: {"#059669" if positions_ahead <= 0 else "#d97706"};">{status_message}</p>

            <a href="{tracking_url}" style="display: inline-block; background-color: #2563eb; color: white; text-decoration: none; padding: 12px 24px; border-radius: 8px; font-weight: 600;">
                Track Live Queue
            </a>
        </div>
    </div>
</body>
</html>
            """

            message = MessageSchema(
                subject=f"Queue Update - {status_message} | MediHelp",
                recipients=recipient_emails,
                body=html_content,
                subtype=MessageType.html,
            )

            await fast_mail.send_message(message)
            logger.info(f"Queue update email sent to: {recipient_emails}")
            return True

        except Exception as e:
            logger.error(f"Failed to send queue update email: {str(e)}")
            return False
