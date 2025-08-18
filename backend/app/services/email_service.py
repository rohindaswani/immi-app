import os
import smtplib
import ssl
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from email.mime.text import MIMEText as MimeText
from email.mime.multipart import MIMEMultipart as MimeMultipart

try:
    from jinja2 import Environment, FileSystemLoader
    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False
    Environment = None
    FileSystemLoader = None

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending email notifications"""
    
    def __init__(self):
        # Email configuration from environment variables
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("FROM_EMAIL", self.smtp_username)
        self.from_name = os.getenv("FROM_NAME", "Immigration Advisor")
        
        # Template configuration
        if JINJA2_AVAILABLE:
            template_dir = os.path.join(os.path.dirname(__file__), "..", "templates", "email")
            self.template_env = Environment(loader=FileSystemLoader(template_dir))
        else:
            self.template_env = None
        
        # Check if email is configured
        self.is_configured = bool(self.smtp_username and self.smtp_password)
        
        if not self.is_configured:
            logger.warning("Email service not configured - missing SMTP credentials")
    
    def send_notification_email(
        self,
        to_email: str,
        user_name: str,
        notification_type: str,
        notification_title: str,
        notification_content: str,
        priority: str = "medium",
        related_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Send a notification email"""
        if not self.is_configured:
            logger.warning("Cannot send email - service not configured")
            return False
        
        try:
            # Choose template based on notification type
            template_name = self._get_template_name(notification_type)
            
            # Prepare template data
            template_data = {
                "user_name": user_name,
                "notification_title": notification_title,
                "notification_content": notification_content,
                "priority": priority,
                "notification_type": notification_type,
                "current_date": datetime.now().strftime("%B %d, %Y"),
                "related_data": related_data or {},
                "app_name": "Immigration Advisor",
                "support_email": "support@immigrationadvisor.com"
            }
            
            # Generate email content
            subject = self._generate_subject(notification_type, notification_title, priority)
            html_content = self._render_template(template_name, template_data)
            text_content = self._generate_text_content(template_data)
            
            # Send email
            return self._send_email(
                to_email=to_email,
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )
            
        except Exception as e:
            logger.error(f"Error sending notification email to {to_email}: {str(e)}")
            return False
    
    def send_deadline_alert_email(
        self,
        to_email: str,
        user_name: str,
        deadline_title: str,
        deadline_date: datetime,
        days_until: int,
        deadline_type: str,
        is_critical: bool = False
    ) -> bool:
        """Send a deadline alert email"""
        priority = "high" if is_critical or days_until <= 7 else "medium"
        
        related_data = {
            "deadline_date": deadline_date.strftime("%B %d, %Y"),
            "days_until": days_until,
            "deadline_type": deadline_type,
            "is_critical": is_critical,
            "urgency_text": self._get_urgency_text(days_until, is_critical)
        }
        
        content = f"""
        Your {deadline_type} deadline is approaching in {days_until} day{'s' if days_until != 1 else ''}.
        
        Deadline Date: {deadline_date.strftime('%B %d, %Y')}
        
        Please take action to ensure you meet this deadline and maintain your legal status.
        """
        
        return self.send_notification_email(
            to_email=to_email,
            user_name=user_name,
            notification_type="deadline",
            notification_title=deadline_title,
            notification_content=content,
            priority=priority,
            related_data=related_data
        )
    
    def send_document_expiry_email(
        self,
        to_email: str,
        user_name: str,
        document_type: str,
        document_number: str,
        expiry_date: datetime,
        days_until: int
    ) -> bool:
        """Send a document expiry alert email"""
        priority = "high" if days_until <= 30 else "medium"
        
        related_data = {
            "document_type": document_type,
            "document_number": document_number,
            "expiry_date": expiry_date.strftime("%B %d, %Y"),
            "days_until": days_until,
            "renewal_urgency": self._get_renewal_urgency_text(document_type, days_until)
        }
        
        content = f"""
        Your {document_type} is expiring soon and needs to be renewed.
        
        Document: {document_type} (#{document_number})
        Expiry Date: {expiry_date.strftime('%B %d, %Y')}
        Days Until Expiry: {days_until}
        
        Please begin the renewal process as soon as possible.
        """
        
        return self.send_notification_email(
            to_email=to_email,
            user_name=user_name,
            notification_type="document_expiry",
            notification_title=f"{document_type} Expiring Soon",
            notification_content=content,
            priority=priority,
            related_data=related_data
        )
    
    def send_monthly_checkin_email(
        self,
        to_email: str,
        user_name: str
    ) -> bool:
        """Send a monthly check-in reminder email"""
        content = """
        It's time for your monthly immigration status check-in.
        
        Please log in to your account and:
        • Review your immigration timeline
        • Update any changes in your status
        • Check for upcoming deadlines
        • Upload any new documents
        
        Regular check-ins help ensure you stay on top of important deadlines and maintain your legal status.
        """
        
        related_data = {
            "checkin_month": datetime.now().strftime("%B %Y"),
            "login_url": "https://app.immigrationadvisor.com/login"
        }
        
        return self.send_notification_email(
            to_email=to_email,
            user_name=user_name,
            notification_type="checkin",
            notification_title="Monthly Status Check-In Reminder",
            notification_content=content,
            priority="medium",
            related_data=related_data
        )
    
    def _get_template_name(self, notification_type: str) -> str:
        """Get email template name based on notification type"""
        template_mapping = {
            "deadline": "deadline_alert.html",
            "document_expiry": "document_expiry.html",
            "checkin": "monthly_checkin.html",
            "i94_expiry": "i94_expiry.html",
            "status_change": "status_change.html"
        }
        return template_mapping.get(notification_type, "generic_notification.html")
    
    def _generate_subject(self, notification_type: str, title: str, priority: str) -> str:
        """Generate email subject line"""
        priority_prefix = ""
        if priority == "high":
            priority_prefix = "[URGENT] "
        elif priority == "critical":
            priority_prefix = "[CRITICAL] "
        
        return f"{priority_prefix}{title} - Immigration Advisor"
    
    def _render_template(self, template_name: str, data: Dict[str, Any]) -> str:
        """Render email template"""
        if not JINJA2_AVAILABLE or not self.template_env:
            return self._generate_fallback_html(data)
            
        try:
            template = self.template_env.get_template(template_name)
            return template.render(**data)
        except Exception as e:
            logger.warning(f"Could not render template {template_name}: {str(e)}")
            # Fallback to generic template
            return self._generate_fallback_html(data)
    
    def _generate_fallback_html(self, data: Dict[str, Any]) -> str:
        """Generate fallback HTML content"""
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; margin: 20px; line-height: 1.6;">
            <h2 style="color: #2c5282;">Immigration Advisor Notification</h2>
            <p>Hello {data.get('user_name', 'User')},</p>
            
            <div style="background-color: #f7fafc; padding: 20px; border-left: 4px solid #3182ce; margin: 20px 0;">
                <h3 style="margin-top: 0; color: #2c5282;">{data.get('notification_title', 'Notification')}</h3>
                <p>{data.get('notification_content', '')}</p>
            </div>
            
            <p>Please log in to your Immigration Advisor account to review your status and take any necessary actions.</p>
            
            <p>Best regards,<br>The Immigration Advisor Team</p>
            
            <hr style="margin: 30px 0; border: none; border-top: 1px solid #e2e8f0;">
            <p style="font-size: 12px; color: #718096;">
                This is an automated notification. If you have questions, please contact us at {data.get('support_email', 'support@immigrationadvisor.com')}.
            </p>
        </body>
        </html>
        """
    
    def _generate_text_content(self, data: Dict[str, Any]) -> str:
        """Generate plain text content"""
        return f"""
        Immigration Advisor Notification
        
        Hello {data.get('user_name', 'User')},
        
        {data.get('notification_title', 'Notification')}
        
        {data.get('notification_content', '')}
        
        Please log in to your Immigration Advisor account to review your status and take any necessary actions.
        
        Best regards,
        The Immigration Advisor Team
        
        ---
        This is an automated notification. If you have questions, please contact us at {data.get('support_email', 'support@immigrationadvisor.com')}.
        """
    
    def _send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str
    ) -> bool:
        """Send email using SMTP"""
        try:
            # Create message
            message = MimeMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email
            
            # Add parts
            text_part = MimeText(text_content, "plain")
            html_part = MimeText(html_content, "html")
            
            message.attach(text_part)
            message.attach(html_part)
            
            # Create secure connection and send
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(message)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    def _get_urgency_text(self, days_until: int, is_critical: bool) -> str:
        """Get urgency text based on days until deadline"""
        if is_critical:
            return "CRITICAL DEADLINE"
        elif days_until <= 1:
            return "URGENT - Due tomorrow or today"
        elif days_until <= 7:
            return "URGENT - Due this week"
        elif days_until <= 14:
            return "Important - Due in 2 weeks"
        else:
            return "Upcoming deadline"
    
    def _get_renewal_urgency_text(self, document_type: str, days_until: int) -> str:
        """Get renewal urgency text for documents"""
        if document_type.lower() in ["visa", "ead"]:
            if days_until <= 30:
                return "Start renewal process immediately"
            elif days_until <= 60:
                return "Begin renewal process soon"
            else:
                return "Plan for renewal"
        else:
            if days_until <= 60:
                return "Renewal required soon"
            else:
                return "Plan ahead for renewal"
    
    def test_email_configuration(self) -> Dict[str, Any]:
        """Test email configuration"""
        if not self.is_configured:
            return {
                "status": "error",
                "message": "Email not configured - missing SMTP credentials"
            }
        
        try:
            # Test SMTP connection
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.smtp_username, self.smtp_password)
            
            return {
                "status": "success",
                "message": "Email configuration is working"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Email configuration test failed: {str(e)}"
            }