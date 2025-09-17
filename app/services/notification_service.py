from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
import smtplib
import json
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings
from app.core.deps import get_redis
import redis

logger = logging.getLogger(__name__)

class NotificationChannel(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WEBHOOK = "webhook"
    IN_APP = "in_app"

class NotificationPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class NotificationService:
    """Service for handling various types of notifications"""
    
    def __init__(self):
        self.redis_client = redis.from_url(settings.redis_url, decode_responses=True)
        self.notification_templates = self._load_templates()
        
    def send_notification(self, 
                         recipient: str,
                         subject: str,
                         message: str,
                         channels: List[NotificationChannel],
                         priority: NotificationPriority = NotificationPriority.MEDIUM,
                         metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Send notification through specified channels"""
        try:
            notification_id = self._generate_notification_id()
            
            # Store notification record
            notification_record = {
                'id': notification_id,
                'recipient': recipient,
                'subject': subject,
                'message': message,
                'channels': [ch.value for ch in channels],
                'priority': priority.value,
                'metadata': metadata or {},
                'created_at': datetime.utcnow().isoformat(),
                'status': 'pending',
                'delivery_attempts': {}
            }
            
            # Send through each channel
            delivery_results = {}
            for channel in channels:
                try:
                    if channel == NotificationChannel.EMAIL:
                        result = self._send_email(recipient, subject, message)
                    elif channel == NotificationChannel.SMS:
                        result = self._send_sms(recipient, message)
                    elif channel == NotificationChannel.PUSH:
                        result = self._send_push(recipient, subject, message)
                    elif channel == NotificationChannel.WEBHOOK:
                        result = self._send_webhook(recipient, subject, message, metadata)
                    elif channel == NotificationChannel.IN_APP:
                        result = self._send_in_app(recipient, subject, message)
                    else:
                        result = {'success': False, 'error': 'Unknown channel'}
                    
                    delivery_results[channel.value] = result
                    
                except Exception as e:
                    logger.error(f"Failed to send notification via {channel.value}: {e}")
                    delivery_results[channel.value] = {'success': False, 'error': str(e)}
            
            # Update notification record
            notification_record['delivery_attempts'] = delivery_results
            notification_record['status'] = 'completed' if any(r.get('success') for r in delivery_results.values()) else 'failed'
            
            # Store in Redis
            self.redis_client.setex(
                f"notification:{notification_id}",
                86400,  # 24 hours
                json.dumps(notification_record)
            )
            
            return {
                'notification_id': notification_id,
                'status': notification_record['status'],
                'delivery_results': delivery_results
            }
            
        except Exception as e:
            logger.error(f"Notification sending failed: {e}")
            return {
                'notification_id': None,
                'status': 'failed',
                'error': str(e)
            }
    
    def send_delay_alert(self, schedule_id: int, delay_minutes: int, 
                        affected_passengers: int, recipients: List[str]) -> Dict[str, Any]:
        """Send delay alert notification"""
        subject = f"Train Delay Alert - Schedule {schedule_id}"
        message = self._format_delay_message(schedule_id, delay_minutes, affected_passengers)
        
        # Determine priority based on delay severity
        if delay_minutes > 60:
            priority = NotificationPriority.CRITICAL
        elif delay_minutes > 30:
            priority = NotificationPriority.HIGH
        else:
            priority = NotificationPriority.MEDIUM
        
        # Send to all recipients
        results = []
        for recipient in recipients:
            result = self.send_notification(
                recipient=recipient,
                subject=subject,
                message=message,
                channels=[NotificationChannel.EMAIL, NotificationChannel.IN_APP],
                priority=priority,
                metadata={
                    'schedule_id': schedule_id,
                    'delay_minutes': delay_minutes,
                    'affected_passengers': affected_passengers,
                    'alert_type': 'delay'
                }
            )
            results.append(result)
        
        return {
            'alert_type': 'delay',
            'recipients_notified': len(recipients),
            'results': results
        }
    
    def send_maintenance_reminder(self, train_id: int, train_number: str, 
                                days_until_maintenance: int, recipients: List[str]) -> Dict[str, Any]:
        """Send maintenance reminder notification"""
        subject = f"Maintenance Reminder - Train {train_number}"
        message = self._format_maintenance_message(train_number, days_until_maintenance)
        
        priority = NotificationPriority.HIGH if days_until_maintenance <= 3 else NotificationPriority.MEDIUM
        
        results = []
        for recipient in recipients:
            result = self.send_notification(
                recipient=recipient,
                subject=subject,
                message=message,
                channels=[NotificationChannel.EMAIL],
                priority=priority,
                metadata={
                    'train_id': train_id,
                    'train_number': train_number,
                    'days_until_maintenance': days_until_maintenance,
                    'alert_type': 'maintenance'
                }
            )
            results.append(result)
        
        return {
            'alert_type': 'maintenance',
            'recipients_notified': len(recipients),
            'results': results
        }
    
    def send_incident_alert(self, incident_type: str, severity: str, 
                          description: str, affected_services: List[str], 
                          recipients: List[str]) -> Dict[str, Any]:
        """Send incident alert notification"""
        subject = f"Incident Alert - {incident_type.title()} ({severity.title()})"
        message = self._format_incident_message(incident_type, severity, description, affected_services)
        
        priority_map = {
            'low': NotificationPriority.LOW,
            'medium': NotificationPriority.MEDIUM,
            'high': NotificationPriority.HIGH,
            'critical': NotificationPriority.CRITICAL
        }
        priority = priority_map.get(severity.lower(), NotificationPriority.MEDIUM)
        
        # Use multiple channels for high priority incidents
        channels = [NotificationChannel.EMAIL, NotificationChannel.IN_APP]
        if priority in [NotificationPriority.HIGH, NotificationPriority.CRITICAL]:
            channels.append(NotificationChannel.SMS)
        
        results = []
        for recipient in recipients:
            result = self.send_notification(
                recipient=recipient,
                subject=subject,
                message=message,
                channels=channels,
                priority=priority,
                metadata={
                    'incident_type': incident_type,
                    'severity': severity,
                    'affected_services': affected_services,
                    'alert_type': 'incident'
                }
            )
            results.append(result)
        
        return {
            'alert_type': 'incident',
            'recipients_notified': len(recipients),
            'results': results
        }
    
    def send_performance_report(self, report_data: Dict[str, Any], 
                              recipients: List[str]) -> Dict[str, Any]:
        """Send performance report notification"""
        subject = f"Performance Report - {report_data.get('period', 'Daily')}"
        message = self._format_performance_message(report_data)
        
        results = []
        for recipient in recipients:
            result = self.send_notification(
                recipient=recipient,
                subject=subject,
                message=message,
                channels=[NotificationChannel.EMAIL],
                priority=NotificationPriority.LOW,
                metadata={
                    'report_type': 'performance',
                    'report_data': report_data
                }
            )
            results.append(result)
        
        return {
            'alert_type': 'performance_report',
            'recipients_notified': len(recipients),
            'results': results
        }
    
    def get_notification_history(self, recipient: Optional[str] = None, 
                               limit: int = 50) -> List[Dict[str, Any]]:
        """Get notification history"""
        try:
            # Get notification keys from Redis
            pattern = f"notification:*"
            keys = self.redis_client.keys(pattern)
            
            notifications = []
            for key in keys[-limit:]:
                data = self.redis_client.get(key)
                if data:
                    notification = json.loads(data)
                    if recipient is None or notification['recipient'] == recipient:
                        notifications.append(notification)
            
            # Sort by creation time, newest first
            notifications.sort(key=lambda x: x['created_at'], reverse=True)
            return notifications[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get notification history: {e}")
            return []
    
    def _send_email(self, recipient: str, subject: str, message: str) -> Dict[str, Any]:
        """Send email notification"""
        try:
            # This is a placeholder implementation
            # In a real system, you would configure SMTP settings
            logger.info(f"Sending email to {recipient}: {subject}")
            
            # Simulate email sending
            return {
                'success': True,
                'channel': 'email',
                'sent_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'channel': 'email',
                'error': str(e)
            }
    
    def _send_sms(self, recipient: str, message: str) -> Dict[str, Any]:
        """Send SMS notification"""
        try:
            # Placeholder SMS implementation
            logger.info(f"Sending SMS to {recipient}: {message[:50]}...")
            
            return {
                'success': True,
                'channel': 'sms',
                'sent_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'channel': 'sms',
                'error': str(e)
            }
    
    def _send_push(self, recipient: str, subject: str, message: str) -> Dict[str, Any]:
        """Send push notification"""
        try:
            # Placeholder push notification implementation
            logger.info(f"Sending push notification to {recipient}: {subject}")
            
            return {
                'success': True,
                'channel': 'push',
                'sent_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'channel': 'push',
                'error': str(e)
            }
    
    def _send_webhook(self, recipient: str, subject: str, message: str, 
                     metadata: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Send webhook notification"""
        try:
            # Placeholder webhook implementation
            logger.info(f"Sending webhook to {recipient}: {subject}")
            
            return {
                'success': True,
                'channel': 'webhook',
                'sent_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'channel': 'webhook',
                'error': str(e)
            }
    
    def _send_in_app(self, recipient: str, subject: str, message: str) -> Dict[str, Any]:
        """Send in-app notification"""
        try:
            # Store in-app notification in Redis
            notification_key = f"in_app:{recipient}:{datetime.utcnow().timestamp()}"
            notification_data = {
                'subject': subject,
                'message': message,
                'created_at': datetime.utcnow().isoformat(),
                'read': False
            }
            
            self.redis_client.setex(notification_key, 604800, json.dumps(notification_data))  # 7 days
            
            return {
                'success': True,
                'channel': 'in_app',
                'sent_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'channel': 'in_app',
                'error': str(e)
            }
    
    def _generate_notification_id(self) -> str:
        """Generate unique notification ID"""
        import uuid
        return str(uuid.uuid4())
    
    def _load_templates(self) -> Dict[str, str]:
        """Load notification templates"""
        return {
            'delay_alert': "Train delay alert: Schedule {schedule_id} is delayed by {delay_minutes} minutes, affecting {affected_passengers} passengers.",
            'maintenance_reminder': "Maintenance reminder: Train {train_number} requires maintenance in {days_until_maintenance} days.",
            'incident_alert': "Incident alert: {incident_type} ({severity}) - {description}. Affected services: {affected_services}.",
            'performance_report': "Performance report for {period}: {summary}"
        }
    
    def _format_delay_message(self, schedule_id: int, delay_minutes: int, affected_passengers: int) -> str:
        """Format delay alert message"""
        return f"""
        TRAIN DELAY ALERT
        
        Schedule ID: {schedule_id}
        Delay: {delay_minutes} minutes
        Affected Passengers: {affected_passengers}
        
        Please take appropriate action to minimize passenger impact.
        
        Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
        """
    
    def _format_maintenance_message(self, train_number: str, days_until_maintenance: int) -> str:
        """Format maintenance reminder message"""
        urgency = "URGENT" if days_until_maintenance <= 3 else "SCHEDULED"
        
        return f"""
        {urgency} MAINTENANCE REMINDER
        
        Train: {train_number}
        Maintenance Due: {days_until_maintenance} days
        
        Please schedule maintenance to avoid service disruption.
        
        Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
        """
    
    def _format_incident_message(self, incident_type: str, severity: str, 
                                description: str, affected_services: List[str]) -> str:
        """Format incident alert message"""
        return f"""
        INCIDENT ALERT - {severity.upper()}
        
        Type: {incident_type.title()}
        Severity: {severity.title()}
        Description: {description}
        
        Affected Services:
        {chr(10).join(f"- {service}" for service in affected_services)}
        
        Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
        """
    
    def _format_performance_message(self, report_data: Dict[str, Any]) -> str:
        """Format performance report message"""
        return f"""
        PERFORMANCE REPORT - {report_data.get('period', 'Daily').upper()}
        
        Summary:
        - On-time Performance: {report_data.get('on_time_performance', 0):.1f}%
        - Total Schedules: {report_data.get('total_schedules', 0)}
        - Completed Schedules: {report_data.get('completed_schedules', 0)}
        - Average Delay: {report_data.get('average_delay', 0):.1f} minutes
        
        Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
        """

# Global notification service instance
notification_service = NotificationService()
