import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings


def send_booking_confirmation(
    booking,
    patients: list,
    doctor_name: str,
    session_date: str,
    session_time: str,
) -> bool:
    """
    Send booking confirmation email to the patient.

    Args:
        booking: Booking object with reference, email, secure_token
        patients: List of patient objects with name, age, phone, queue_number
        doctor_name: Name of the doctor
        session_date: Formatted date string
        session_time: Formatted time string

    Returns:
        True if email sent successfully, False otherwise
    """
    try:
        # Create message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Booking Confirmation - {booking.booking_reference}"
        msg["From"] = settings.smtp_from
        msg["To"] = booking.email

        # Build tracking URL
        tracking_url = f"{settings.patient_web_url}/track?token={booking.secure_token}"

        # Build patient table rows for HTML
        patient_rows_html = ""
        for patient in patients:
            patient_rows_html += f"""
            <tr>
                <td style="padding: 10px; border: 1px solid #ddd;">{patient.queue_number}</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{patient.name}</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{patient.age}</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{patient.phone}</td>
            </tr>
            """

        # Build patient list for plain text
        patient_list_text = ""
        for patient in patients:
            patient_list_text += (
                f"  - Queue #{patient.queue_number}: {patient.name}, "
                f"Age: {patient.age}, Phone: {patient.phone}\n"
            )

        # Plain text version
        text_content = f"""
Booking Confirmation - MediHelp Dispensary

Your booking has been confirmed!

Booking Reference: {booking.booking_reference}

Appointment Details:
- Doctor: {doctor_name}
- Date: {session_date}
- Time: {session_time}

Patients:
{patient_list_text}
Track your queue status:
{tracking_url}

Please arrive 10 minutes before your estimated time.

Thank you for choosing MediHelp Dispensary.
        """.strip()

        # HTML version
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background-color: #4CAF50;
            color: white;
            padding: 20px;
            text-align: center;
            border-radius: 5px 5px 0 0;
        }}
        .content {{
            background-color: #f9f9f9;
            padding: 20px;
            border: 1px solid #ddd;
            border-top: none;
        }}
        .booking-ref {{
            background-color: #e8f5e9;
            padding: 15px;
            border-radius: 5px;
            text-align: center;
            margin: 15px 0;
        }}
        .booking-ref strong {{
            font-size: 24px;
            color: #2e7d32;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}
        th {{
            background-color: #4CAF50;
            color: white;
            padding: 10px;
            text-align: left;
        }}
        .details {{
            background-color: white;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
        }}
        .track-btn {{
            display: inline-block;
            background-color: #4CAF50;
            color: white;
            padding: 12px 30px;
            text-decoration: none;
            border-radius: 5px;
            margin: 15px 0;
        }}
        .footer {{
            text-align: center;
            color: #666;
            font-size: 12px;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Booking Confirmed!</h1>
    </div>
    <div class="content">
        <div class="booking-ref">
            <p>Your Booking Reference</p>
            <strong>{booking.booking_reference}</strong>
        </div>

        <div class="details">
            <h3>Appointment Details</h3>
            <p><strong>Doctor:</strong> {doctor_name}</p>
            <p><strong>Date:</strong> {session_date}</p>
            <p><strong>Time:</strong> {session_time}</p>
        </div>

        <h3>Registered Patients</h3>
        <table>
            <thead>
                <tr>
                    <th>Queue #</th>
                    <th>Name</th>
                    <th>Age</th>
                    <th>Phone</th>
                </tr>
            </thead>
            <tbody>
                {patient_rows_html}
            </tbody>
        </table>

        <div style="text-align: center;">
            <p>Track your queue status in real-time:</p>
            <a href="{tracking_url}" class="track-btn">Track My Queue</a>
        </div>

        <p style="color: #666; font-size: 14px;">
            <strong>Note:</strong> Please arrive 10 minutes before your estimated time.
        </p>
    </div>
    <div class="footer">
        <p>Thank you for choosing MediHelp Dispensary</p>
        <p>This is an automated message. Please do not reply to this email.</p>
    </div>
</body>
</html>
        """.strip()

        # Attach parts
        part1 = MIMEText(text_content, "plain")
        part2 = MIMEText(html_content, "html")
        msg.attach(part1)
        msg.attach(part2)

        # Send email
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
            server.sendmail(settings.smtp_from, booking.email, msg.as_string())

        print(f"Booking confirmation email sent to {booking.email}")
        return True

    except Exception as e:
        print(f"Failed to send booking confirmation email: {e}")
        return False
