"""Email notification service for Explorers Choice."""
import email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
import smtplib
from typing import Any

from .config import settings

logger = logging.getLogger("explorers.email")


def send_email(
    to_email: str,
    subject: str,
    text_content: str,
    html_content: str | None = None,
) -> bool:
    """Send an email using configured SMTP settings.

    Returns True if sent successfully, False otherwise.
    """
    if not settings.smtp_host or not settings.smtp_host.strip():
        logger.warning(
            "SMTP_HOST is not configured. Email notification skipped for '%s' to '%s'. "
            "To enable live emails, set SMTP_HOST, SMTP_PORT, SMTP_USERNAME, and SMTP_PASSWORD in backend/.env.",
            subject,
            to_email,
        )
        return False

    from_addr = (settings.smtp_from_email or settings.smtp_username or "infoexplorerschoice@gmail.com").strip()
    from_name = settings.smtp_from_name or "Explorers Choice"
    formatted_from = email.utils.formataddr((from_name, from_addr))

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = formatted_from
    message["To"] = to_email
    message["Date"] = email.utils.formatdate(localtime=True)
    message["Message-ID"] = email.utils.make_msgid(domain="explorerschoice.in")

    # Plain text version
    part_text = MIMEText(text_content, "plain", "utf-8")
    message.attach(part_text)

    # HTML version if provided
    if html_content:
        part_html = MIMEText(html_content, "html", "utf-8")
        message.attach(part_html)

    try:
        if settings.smtp_use_ssl:
            with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port, timeout=20) as server:
                if settings.smtp_username and settings.smtp_password:
                    server.login(settings.smtp_username, settings.smtp_password)
                server.send_message(message)
        else:
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=20) as server:
                server.ehlo()
                if settings.smtp_use_tls:
                    server.starttls()
                    server.ehlo()
                if settings.smtp_username and settings.smtp_password:
                    server.login(settings.smtp_username, settings.smtp_password)
                server.send_message(message)

        logger.info("Successfully sent email notification '%s' to %s", subject, to_email)
        return True
    except Exception as exc:
        logger.error("Failed to send email to %s: %s", to_email, exc, exc_info=True)
        return False


def build_booking_notification_content(data: dict[str, Any]) -> tuple[str, str, str]:
    """Generate subject, plain text, and HTML body for a new tour booking."""
    booking_ref = data.get("booking_reference", "N/A")
    package_name = data.get("package_name", "Tour Package")
    destination_name = data.get("destination_name", "Destination")
    travel_date = str(data.get("travel_date", "N/A"))
    adults = data.get("adults", 1)
    children = data.get("children", 0)
    infants = data.get("infants", 0)
    duration_days = data.get("duration_days", "")
    total_price = data.get("total", 0.0)
    currency = data.get("currency", "USD")
    full_name = data.get("full_name", "")
    customer_email = data.get("email", "")
    phone = data.get("phone", "")
    country = data.get("country", "")
    departure_info = data.get("departure_information", "")
    special_reqs = data.get("special_requirements", "")
    notes = data.get("notes", "")
    status_str = data.get("status", "PENDING_CONFIRMATION")
    booking_mode = data.get("booking_mode", "ON_REQUEST")

    subject = f"New Tour Booking: {package_name} ({booking_ref}) - {full_name}"

    travelers_summary = f"{adults} Adult(s)"
    if children:
        travelers_summary += f", {children} Child(ren)"
    if infants:
        travelers_summary += f", {infants} Infant(s)"

    # Plain text format
    text_content = f"""
=====================================================
NEW TOUR BOOKING RECEIVED - EXPLORERS CHOICE
=====================================================

A new tour booking has been placed.

BOOKING DETAILS:
----------------
Reference Code   : {booking_ref}
Package / Tour   : {package_name}
Destination      : {destination_name}
Duration         : {duration_days} Days
Travel Date      : {travel_date}
Guests           : {travelers_summary}
Total Amount     : {currency} {total_price:,.2f}
Booking Mode     : {booking_mode}
Status           : {status_str}

CUSTOMER CONTACT:
-----------------
Full Name        : {full_name}
Email            : {customer_email}
Phone            : {phone}
Country          : {country}

ADDITIONAL INFORMATION:
-----------------------
Departure Info   : {departure_info or 'None provided'}
Special Requests : {special_reqs or 'None'}
Notes            : {notes or 'None'}

=====================================================
You can view and manage this booking in the Admin Dashboard.
"""

    # HTML format
    html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>New Tour Booking: {booking_ref}</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      background-color: #f7f6f2;
      color: #2b2d2f;
      margin: 0;
      padding: 24px;
      line-height: 1.6;
    }}
    .container {{
      max-width: 600px;
      margin: 0 auto;
      background-color: #ffffff;
      border-radius: 8px;
      overflow: hidden;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
      border: 1px solid #e5e3dc;
    }}
    .header {{
      background-color: #1c3b2b;
      color: #f7f6f2;
      padding: 28px 24px;
      text-align: center;
    }}
    .header h1 {{
      margin: 0;
      font-size: 24px;
      letter-spacing: 0.5px;
    }}
    .header p {{
      margin: 6px 0 0 0;
      font-size: 14px;
      color: #d1d5db;
    }}
    .badge {{
      display: inline-block;
      margin-top: 10px;
      padding: 4px 12px;
      border-radius: 20px;
      font-size: 13px;
      font-weight: 600;
      background-color: #c97a56;
      color: #ffffff;
    }}
    .content {{
      padding: 24px;
    }}
    .section-title {{
      font-size: 16px;
      font-weight: 700;
      color: #1c3b2b;
      margin-top: 20px;
      margin-bottom: 12px;
      border-bottom: 2px solid #e5e3dc;
      padding-bottom: 6px;
      text-transform: uppercase;
      letter-spacing: 0.8px;
    }}
    .details-table {{
      width: 100%;
      border-collapse: collapse;
      margin-bottom: 16px;
    }}
    .details-table td {{
      padding: 8px 6px;
      vertical-align: top;
      font-size: 14px;
    }}
    .details-table td.label {{
      color: #5d6166;
      width: 38%;
      font-weight: 500;
    }}
    .details-table td.value {{
      color: #1c3b2b;
      font-weight: 600;
    }}
    .total-box {{
      background-color: #f1ede4;
      border-radius: 6px;
      padding: 14px 18px;
      margin-top: 16px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .total-label {{
      font-size: 15px;
      font-weight: 700;
      color: #1c3b2b;
    }}
    .total-amount {{
      font-size: 20px;
      font-weight: 800;
      color: #c97a56;
    }}
    .notes-box {{
      background-color: #faf9f6;
      border-left: 4px solid #c97a56;
      padding: 10px 14px;
      margin-top: 8px;
      font-size: 13px;
      color: #4b5563;
    }}
    .footer {{
      background-color: #f7f6f2;
      padding: 18px 24px;
      text-align: center;
      font-size: 12px;
      color: #83888e;
      border-top: 1px solid #e5e3dc;
    }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>New Tour Booking</h1>
      <p>A new customer booking request has been submitted</p>
      <div class="badge">{booking_ref}</div>
    </div>

    <div class="content">
      <div class="section-title">Tour Details</div>
      <table class="details-table">
        <tr>
          <td class="label">Package Name:</td>
          <td class="value">{package_name}</td>
        </tr>
        <tr>
          <td class="label">Destination:</td>
          <td class="value">{destination_name}</td>
        </tr>
        <tr>
          <td class="label">Duration:</td>
          <td class="value">{duration_days} Days</td>
        </tr>
        <tr>
          <td class="label">Travel Date:</td>
          <td class="value">{travel_date}</td>
        </tr>
        <tr>
          <td class="label">Guests:</td>
          <td class="value">{travelers_summary}</td>
        </tr>
        <tr>
          <td class="label">Booking Mode:</td>
          <td class="value">{booking_mode}</td>
        </tr>
        <tr>
          <td class="label">Status:</td>
          <td class="value">{status_str}</td>
        </tr>
      </table>

      <div class="total-box">
        <span class="total-label">Total Booking Price</span>
        <span class="total-amount">{currency} {total_price:,.2f}</span>
      </div>

      <div class="section-title">Customer Contact Details</div>
      <table class="details-table">
        <tr>
          <td class="label">Customer Name:</td>
          <td class="value">{full_name}</td>
        </tr>
        <tr>
          <td class="label">Email Address:</td>
          <td class="value"><a href="mailto:{customer_email}" style="color: #1c3b2b; text-decoration: underline;">{customer_email}</a></td>
        </tr>
        <tr>
          <td class="label">Phone Number:</td>
          <td class="value"><a href="tel:{phone}" style="color: #1c3b2b; text-decoration: underline;">{phone}</a></td>
        </tr>
        <tr>
          <td class="label">Country:</td>
          <td class="value">{country}</td>
        </tr>
      </table>

      {f'''<div class="section-title">Departure &amp; Flight Information</div>
      <div class="notes-box">{departure_info}</div>''' if departure_info else ''}

      {f'''<div class="section-title">Special Requirements</div>
      <div class="notes-box">{special_reqs}</div>''' if special_reqs else ''}

      {f'''<div class="section-title">Customer Notes</div>
      <div class="notes-box">{notes}</div>''' if notes else ''}
    </div>

    <div class="footer">
      <p style="margin: 0;">Explorers Choice &bull; Tour &amp; Travel Booking Notifications</p>
      <p style="margin: 4px 0 0 0;">Recipient: {settings.admin_notification_email}</p>
    </div>
  </div>
</body>
</html>
"""
    return subject, text_content, html_content


def send_booking_notification_email(booking_data: dict[str, Any]) -> bool:
    """Convenience background task function to send a new booking alert to the administrator."""
    subject, text_content, html_content = build_booking_notification_content(booking_data)
    recipient = settings.admin_notification_email or "infoexplorerschoice@gmail.com"
    return send_email(
        to_email=recipient,
        subject=subject,
        text_content=text_content,
        html_content=html_content,
    )


def build_train_booking_notification_content(data: dict[str, Any]) -> tuple[str, str, str]:
    """Generate subject, plain text, and HTML body for a train ticket booking."""
    booking_ref = data.get("booking_reference", "N/A")
    pnr = data.get("pnr_number", "N/A")
    train_num = data.get("train_number", "")
    train_name = data.get("train_name", "Express")
    from_st = data.get("from_station_name", "")
    from_code = data.get("from_station_code", "")
    to_st = data.get("to_station_name", "")
    to_code = data.get("to_station_code", "")
    journey_date = str(data.get("journey_date", ""))
    dep_time = data.get("departure_time", "")
    arr_time = data.get("arrival_time", "")
    travel_class = data.get("travel_class", "")
    quota = data.get("quota", "GENERAL")
    passengers = data.get("passengers", [])
    contact_name = data.get("contact_name", "")
    contact_email = data.get("contact_email", "")
    contact_phone = data.get("contact_phone", "")
    total_amount = data.get("total_amount", 0.0)
    currency = data.get("currency", "INR")
    status = data.get("status", "CONFIRMED")

    subject = f"Train Ticket Confirmed: {train_name} ({train_num}) - PNR {pnr} - {contact_name}"

    passengers_text = ""
    passengers_html_rows = ""
    for idx, p in enumerate(passengers, 1):
        p_name = p.get("name", "Passenger")
        p_age = p.get("age", "")
        p_gender = p.get("gender", "")
        p_seat = p.get("seat_number", "Confirmed")
        p_status = p.get("status", "CNF")
        passengers_text += f"\n  {idx}. {p_name} ({p_age} yrs, {p_gender}) - Seat/Berth: {p_seat} [{p_status}]"
        passengers_html_rows += f"""
        <tr>
          <td style="padding: 8px 6px; font-weight: 600; color: #1c3b2b;">{idx}. {p_name}</td>
          <td style="padding: 8px 6px; color: #5d6166;">{p_age} yrs / {p_gender}</td>
          <td style="padding: 8px 6px; font-weight: 700; color: #1c3b2b;">{p_seat}</td>
          <td style="padding: 8px 6px; font-weight: 700; color: #2e7d32;">{p_status}</td>
        </tr>
        """

    text_content = f"""
=====================================================
CONFIRMED TRAIN TICKET BOOKING - EXPLORERS CHOICE
=====================================================

A train ticket has been booked successfully!

JOURNEY & TRAIN DETAILS:
------------------------
PNR Number       : {pnr}
Booking Ref      : {booking_ref}
Train            : {train_name} ({train_num})
From Station     : {from_st} ({from_code})
To Station       : {to_st} ({to_code})
Date of Journey  : {journey_date}
Departure Time   : {dep_time}
Arrival Time     : {arr_time}
Class & Quota    : {travel_class} | {quota}
Status           : {status}

PASSENGERS & SEAT ALLOCATION:
-----------------------------{passengers_text}

CONTACT DETAILS:
----------------
Passenger / Lead : {contact_name}
Email            : {contact_email}
Mobile           : {contact_phone}

PAYMENT SUMMARY:
----------------
Total Fare       : {currency} {total_amount:,.2f}

=====================================================
Explorers Choice Train Desk
"""

    html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Train Ticket Confirmation - PNR {pnr}</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      background-color: #f7f6f2;
      color: #2b2d2f;
      margin: 0;
      padding: 24px;
      line-height: 1.6;
    }}
    .container {{
      max-width: 600px;
      margin: 0 auto;
      background-color: #ffffff;
      border-radius: 8px;
      overflow: hidden;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
      border: 1px solid #e5e3dc;
    }}
    .header {{
      background: linear-gradient(135deg, #1c3b2b 0%, #29553f 100%);
      color: #f7f6f2;
      padding: 28px 24px;
      text-align: center;
    }}
    .header h1 {{
      margin: 0;
      font-size: 24px;
    }}
    .pnr-pill {{
      display: inline-block;
      margin-top: 10px;
      padding: 6px 16px;
      border-radius: 20px;
      font-size: 15px;
      font-weight: 800;
      background-color: #c97a56;
      color: #ffffff;
      letter-spacing: 1px;
    }}
    .content {{
      padding: 24px;
    }}
    .route-box {{
      background-color: #faf9f6;
      border: 1px solid #e5e3dc;
      border-radius: 8px;
      padding: 16px;
      margin-bottom: 20px;
      text-align: center;
    }}
    .station-name {{
      font-size: 16px;
      font-weight: 700;
      color: #1c3b2b;
    }}
    .station-time {{
      font-size: 14px;
      color: #c97a56;
      font-weight: 600;
    }}
    .section-title {{
      font-size: 15px;
      font-weight: 700;
      color: #1c3b2b;
      margin-top: 20px;
      margin-bottom: 12px;
      border-bottom: 2px solid #e5e3dc;
      padding-bottom: 6px;
      text-transform: uppercase;
      letter-spacing: 0.8px;
    }}
    .table {{
      width: 100%;
      border-collapse: collapse;
      margin-bottom: 16px;
    }}
    .table th {{
      background-color: #f1ede4;
      padding: 8px 6px;
      text-align: left;
      font-size: 12px;
      color: #1c3b2b;
    }}
    .table td {{
      font-size: 14px;
      border-bottom: 1px solid #f1ede4;
    }}
    .total-box {{
      background-color: #f1ede4;
      border-radius: 6px;
      padding: 14px 18px;
      margin-top: 16px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .total-amount {{
      font-size: 20px;
      font-weight: 800;
      color: #c97a56;
    }}
    .footer {{
      background-color: #f7f6f2;
      padding: 18px 24px;
      text-align: center;
      font-size: 12px;
      color: #83888e;
      border-top: 1px solid #e5e3dc;
    }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>Train Ticket Confirmation</h1>
      <p style="margin: 4px 0 0 0; color: #d1d5db;">Explorers Choice Train Desk</p>
      <div class="pnr-pill">PNR: {pnr}</div>
    </div>

    <div class="content">
      <div class="route-box">
        <div style="font-size: 18px; font-weight: 800; color: #1c3b2b;">{train_name} ({train_num})</div>
        <div style="margin-top: 8px; display: flex; justify-content: space-around; align-items: center;">
          <div>
            <div class="station-name">{from_st} ({from_code})</div>
            <div class="station-time">{dep_time}</div>
          </div>
          <div style="font-size: 20px; color: #c97a56;">&rarr;</div>
          <div>
            <div class="station-name">{to_st} ({to_code})</div>
            <div class="station-time">{arr_time}</div>
          </div>
        </div>
        <div style="margin-top: 10px; font-size: 13px; color: #6b7280;">Date of Journey: <strong>{journey_date}</strong> &bull; Class: <strong>{travel_class}</strong> &bull; Quota: <strong>{quota}</strong></div>
      </div>

      <div class="section-title">Passengers &amp; Berths</div>
      <table class="table">
        <thead>
          <tr>
            <th>Passenger</th>
            <th>Details</th>
            <th>Coach / Berth</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {passengers_html_rows}
        </tbody>
      </table>

      <div class="section-title">Contact &amp; Payment</div>
      <p style="margin: 4px 0; font-size: 14px;"><strong>Lead Passenger:</strong> {contact_name}</p>
      <p style="margin: 4px 0; font-size: 14px;"><strong>Email:</strong> {contact_email} &bull; <strong>Phone:</strong> {contact_phone}</p>
      <p style="margin: 4px 0; font-size: 14px;"><strong>Booking Ref:</strong> {booking_ref}</p>

      <div class="total-box">
        <span style="font-weight: 700; color: #1c3b2b;">Total Paid</span>
        <span class="total-amount">{currency} {total_amount:,.2f}</span>
      </div>
    </div>

    <div class="footer">
      <p style="margin: 0;">Explorers Choice &bull; Seamless Rail &amp; Holiday Travel</p>
      <p style="margin: 4px 0 0 0;">Notification sent to {settings.admin_notification_email}</p>
    </div>
  </div>
</body>
</html>
"""
    return subject, text_content, html_content


def send_train_booking_notification_email(data: dict[str, Any]) -> bool:
    """Send train ticket booking notification to the admin and customer."""
    subject, text_content, html_content = build_train_booking_notification_content(data)
    admin_email = settings.admin_notification_email or "infoexplorerschoice@gmail.com"
    
    # 1. Send to Admin
    send_email(
        to_email=admin_email,
        subject=subject,
        text_content=text_content,
        html_content=html_content,
    )

    # 2. Also send confirmation to customer if different
    cust_email = (data.get("contact_email") or "").strip().lower()
    if cust_email and cust_email != admin_email.lower() and "@" in cust_email:
        send_email(
            to_email=cust_email,
            subject=f"Your Train Ticket Confirmation - PNR {data.get('pnr_number', '')} (Explorers Choice)",
            text_content=text_content,
            html_content=html_content,
        )

    return True


def build_cab_booking_notification_content(data: dict[str, Any]) -> tuple[str, str, str]:
    """Generate subject, plain text, and HTML body for a new cab booking."""
    booking_ref = data.get("booking_reference", "N/A")
    trip_type = data.get("trip_type", "LOCAL")
    cab_type = data.get("cab_type", "Sedan")
    pickup_location = data.get("pickup_location", "")
    drop_location = data.get("drop_location", "")
    pickup_date = str(data.get("pickup_date", "N/A"))
    pickup_time = data.get("pickup_time", "")
    distance_kms = float(data.get("distance_kms", 0) or 0)
    passengers = data.get("passengers", 1)
    full_name = data.get("full_name", "")
    customer_email = data.get("email", "")
    phone = data.get("phone", "")
    special_reqs = data.get("special_requirements", "")
    status_str = data.get("status", "PENDING_CONFIRMATION")

    trip_labels = {
        "LOCAL": "Local / City Rental",
        "AIRPORT_TRANSFER": "Airport Transfer",
        "OUTSTATION": "Outstation / One Way",
    }
    trip_label = trip_labels.get(trip_type, trip_type)

    subject = f"New Cab Booking Request: {cab_type} - {pickup_location} to {drop_location} ({booking_ref})"

    text_content = f"""
=====================================================
NEW CAB BOOKING REQUEST - EXPLORERS CHOICE
=====================================================

A new cab booking request has been placed and needs confirmation.

BOOKING DETAILS:
----------------
Reference Code   : {booking_ref}
Trip Type        : {trip_label}
Cab Type         : {cab_type}
Pickup Location  : {pickup_location}
Drop Location    : {drop_location}
Pickup Date      : {pickup_date}
Pickup Time      : {pickup_time}
Approx. Distance : {distance_kms:,.0f} km
Passengers       : {passengers}
Fare             : To be confirmed by Explorers Choice
Status           : {status_str}

CUSTOMER CONTACT:
-----------------
Full Name        : {full_name}
Email            : {customer_email}
Phone            : {phone}

ADDITIONAL INFORMATION:
----------------------
Special Requests : {special_reqs or 'None'}

=====================================================
Confirm the cab with the customer and dispatch the driver.
"""

    html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>New Cab Booking: {booking_ref}</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      background-color: #f7f6f2;
      color: #2b2d2f;
      margin: 0;
      padding: 24px;
      line-height: 1.6;
    }}
    .container {{
      max-width: 600px;
      margin: 0 auto;
      background-color: #ffffff;
      border-radius: 8px;
      overflow: hidden;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
      border: 1px solid #e5e3dc;
    }}
    .header {{
      background: linear-gradient(135deg, #1c3b2b 0%, #29553f 100%);
      color: #f7f6f2;
      padding: 28px 24px;
      text-align: center;
    }}
    .header h1 {{
      margin: 0;
      font-size: 24px;
    }}
    .badge {{
      display: inline-block;
      margin-top: 10px;
      padding: 4px 12px;
      border-radius: 20px;
      font-size: 13px;
      font-weight: 600;
      background-color: #c97a56;
      color: #ffffff;
    }}
    .content {{
      padding: 24px;
    }}
    .route-box {{
      background-color: #faf9f6;
      border: 1px solid #e5e3dc;
      border-radius: 8px;
      padding: 16px;
      margin-bottom: 20px;
      text-align: center;
    }}
    .location-name {{
      font-size: 16px;
      font-weight: 700;
      color: #1c3b2b;
    }}
    .section-title {{
      font-size: 15px;
      font-weight: 700;
      color: #1c3b2b;
      margin-top: 20px;
      margin-bottom: 12px;
      border-bottom: 2px solid #e5e3dc;
      padding-bottom: 6px;
      text-transform: uppercase;
      letter-spacing: 0.8px;
    }}
    .details-table {{
      width: 100%;
      border-collapse: collapse;
      margin-bottom: 16px;
    }}
    .details-table td {{
      padding: 8px 6px;
      vertical-align: top;
      font-size: 14px;
    }}
    .details-table td.label {{
      color: #5d6166;
      width: 38%;
      font-weight: 500;
    }}
    .details-table td.value {{
      color: #1c3b2b;
      font-weight: 600;
    }}
    .total-box {{
      background-color: #f1ede4;
      border-radius: 6px;
      padding: 14px 18px;
      margin-top: 16px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .total-label {{
      font-size: 15px;
      font-weight: 700;
      color: #1c3b2b;
    }}
    .total-amount {{
      font-size: 20px;
      font-weight: 800;
      color: #c97a56;
    }}
    .notes-box {{
      background-color: #faf9f6;
      border-left: 4px solid #c97a56;
      padding: 10px 14px;
      margin-top: 8px;
      font-size: 13px;
      color: #4b5563;
    }}
    .footer {{
      background-color: #f7f6f2;
      padding: 18px 24px;
      text-align: center;
      font-size: 12px;
      color: #83888e;
      border-top: 1px solid #e5e3dc;
    }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>New Cab Booking Request</h1>
      <p style="margin: 4px 0 0 0; color: #d1d5db;">A customer cab request needs confirmation</p>
      <div class="badge">{booking_ref}</div>
    </div>

    <div class="content">
      <div class="route-box">
        <div style="font-size: 18px; font-weight: 800; color: #1c3b2b;">{cab_type} &bull; {trip_label}</div>
        <div style="margin-top: 12px; display: flex; justify-content: space-around; align-items: center;">
          <div>
            <div class="location-name">{pickup_location}</div>
            <div style="font-size: 12px; color: #6b7280;">Pickup</div>
          </div>
          <div style="font-size: 20px; color: #c97a56;">&rarr;</div>
          <div>
            <div class="location-name">{drop_location}</div>
            <div style="font-size: 12px; color: #6b7280;">Drop</div>
          </div>
        </div>
        <div style="margin-top: 10px; font-size: 13px; color: #6b7280;">Pickup: <strong>{pickup_date} at {pickup_time}</strong> &bull; Approx. Distance: <strong>{distance_kms:,.0f} km</strong> &bull; Passengers: <strong>{passengers}</strong></div>
      </div>

      <div class="section-title">Fare</div>
      <div class="notes-box">
        <strong>To be confirmed by the Explorers Choice team.</strong> A final
        quote for this trip will be sent to the customer before dispatch.
      </div>

      <div class="section-title">Customer Contact Details</div>
      <table class="details-table">
        <tr>
          <td class="label">Customer Name:</td>
          <td class="value">{full_name}</td>
        </tr>
        <tr>
          <td class="label">Email Address:</td>
          <td class="value"><a href="mailto:{customer_email}" style="color: #1c3b2b; text-decoration: underline;">{customer_email}</a></td>
        </tr>
        <tr>
          <td class="label">Phone Number:</td>
          <td class="value"><a href="tel:{phone}" style="color: #1c3b2b; text-decoration: underline;">{phone}</a></td>
        </tr>
      </table>

      {f'''<div class="section-title">Special Requirements</div>
      <div class="notes-box">{special_reqs}</div>''' if special_reqs else ''}
    </div>

    <div class="footer">
      <p style="margin: 0;">Explorers Choice &bull; Cab &amp; Car Rental Notifications</p>
      <p style="margin: 4px 0 0 0;">Recipient: {settings.admin_notification_email}</p>
    </div>
  </div>
</body>
</html>
"""
    return subject, text_content, html_content


def send_cab_booking_notification_email(data: dict[str, Any]) -> bool:
    """Send a cab booking request notification to the admin and to the customer."""
    subject, text_content, html_content = build_cab_booking_notification_content(data)
    admin_email = settings.admin_notification_email or "infoexplorerschoice@gmail.com"

    # 1. Send to Admin immediately
    send_email(
        to_email=admin_email,
        subject=subject,
        text_content=text_content,
        html_content=html_content,
    )

    # 2. Send a copy to the customer if different
    cust_email = (data.get("email") or "").strip().lower()
    if cust_email and cust_email != admin_email.lower() and "@" in cust_email:
        send_email(
            to_email=cust_email,
            subject=f"Your Cab Booking Request {data.get('booking_reference', '')} Received (Explorers Choice)",
            text_content=text_content,
            html_content=html_content,
        )

    return True
