from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
import os
import smtplib
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
import pytz
from fastapi import FastAPI, logger
from db import get_db
from db.models import User
from logging import getLogger
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger("uvicorn.error")
def send_expiration_email(to_email: str, plan: str, billing_cycle: str):
    from_email = os.getenv("SMTP_USERNAME")
    app_url = os.getenv("APP_URL")
    
    # Create email
    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = "Your Subscription Has Expired"
    
    body = (
        f"Dear User,\n\n"
        f"Your {plan} ({billing_cycle}) subscription has expired.\n"
        f"You've been downgraded to the Free plan. To continue enjoying premium features, please renew your subscription.\n"
        f"Click here to renew: {app_url}\n\n"
        f"Thank you for using our service!\n"
        f"Best regards,\nYour App Team"
    )
    msg.attach(MIMEText(body, "plain"))
    
    try:
        server = smtplib.SMTP(os.getenv("SMTP_SERVER"), os.getenv("SMTP_PORT"))
        server.starttls()
        server.login(os.getenv("SMTP_USERNAME"), os.getenv("SMTP_PASSWORD"))
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
        print(f"Email sent to {to_email}")
        return True
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")
        return False
def check_expired_subscriptions():
    print("Checking expired subscriptions")
    db = next(get_db())
    try:
        current_time = datetime.now(pytz.UTC)
        users = db.query(User).filter(User.expires_at != None, User.expires_at < current_time).all()
        
        for user in users:
            logger.info(f"Downgrading user {user.email} from {user.role} to free due to expiration")
            previous_role = user.role
            previous_billing_cycle = user.billing_cycle
            user.role = "free"
            user.billing_cycle = "monthly"
            user.expires_at = None
            
            # Send email notification if not already sent
            if not user.notification_sent:
                success = send_expiration_email(user.email, previous_role, previous_billing_cycle)
                if success:
                    user.notification_sent = True
                    logger.info(f"Expiration email sent to {user.email}")
                else:
                    logger.error(f"Failed to send expiration email to {user.email}")
        
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error checking subscriptions: {e}")
    finally:
        db.close()