from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Create database base
Base = declarative_base()

# Security Events table
class SecurityEvent(Base):
    __tablename__ = 'security_events'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    event_type = Column(String(100), nullable=False)
    source_ip = Column(String(45))  # IPv4 and IPv6 compatible
    destination_ip = Column(String(45))
    source_port = Column(Integer)
    destination_port = Column(Integer)
    protocol = Column(String(20))
    severity = Column(String(20), nullable=False)  # Low, Medium, High, Critical
    message = Column(Text, nullable=False)
    user_agent = Column(Text)
    username = Column(String(100))
    status_code = Column(Integer)
    file_path = Column(String(500))
    process_name = Column(String(200))
    raw_log = Column(Text)  # Store original log entry
    
    def __repr__(self):
        return f"<SecurityEvent(id={self.id}, type='{self.event_type}', severity='{self.severity}')>"
    
    def to_dict(self):
        """Convert event to dictionary for JSON responses"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S') if self.timestamp else None,
            'event_type': self.event_type,
            'source_ip': self.source_ip,
            'destination_ip': self.destination_ip,
            'source_port': self.source_port,
            'destination_port': self.destination_port,
            'protocol': self.protocol,
            'severity': self.severity,
            'message': self.message,
            'user_agent': self.user_agent,
            'username': self.username,
            'status_code': self.status_code,
            'file_path': self.file_path,
            'process_name': self.process_name
        }

# Alerts table
class Alert(Base):
    __tablename__ = 'alerts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    alert_type = Column(String(100), nullable=False)
    severity = Column(String(20), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    source_ip = Column(String(45))
    affected_user = Column(String(100))
    status = Column(String(20), default='Open')  # Open, Investigating, Resolved
    assigned_to = Column(String(100))
    event_count = Column(Integer, default=1)
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S') if self.timestamp else None,
            'alert_type': self.alert_type,
            'severity': self.severity,
            'title': self.title,
            'description': self.description,
            'source_ip': self.source_ip,
            'affected_user': self.affected_user,
            'status': self.status,
            'assigned_to': self.assigned_to,
            'event_count': self.event_count
        }

class DatabaseManager:
    def __init__(self, db_path='siem_database.db'):
        """Initialize database connection"""
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        Base.metadata.create_all(self.engine)
        
        # Create session factory
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        
        print(f"✅ Database initialized: {db_path}")
        self.create_sample_data()
    
    def create_sample_data(self):
        """Create some sample security events for testing"""
        sample_events = [
            SecurityEvent(
                event_type='Failed Login',
                source_ip='192.168.1.100',
                severity='Medium',
                message='Failed login attempt for user: admin',
                username='admin',
                status_code=401
            ),
            SecurityEvent(
                event_type='Brute Force Attack',
                source_ip='10.0.0.50',
                severity='High',
                message='Multiple failed login attempts detected (15 attempts in 5 minutes)',
                username='admin',
                status_code=401
            ),
            SecurityEvent(
                event_type='Suspicious File Access',
                source_ip='192.168.1.25',
                severity='Medium',
                message='Unauthorized access attempt to sensitive file',
                username='guest',
                file_path='/etc/passwd'
            ),
            SecurityEvent(
                event_type='Port Scan Detected',
                source_ip='203.0.113.10',
                destination_ip='192.168.1.1',
                severity='High',
                message='Port scanning activity detected from external IP',
                protocol='TCP'
            ),
            SecurityEvent(
                event_type='Malware Detection',
                source_ip='192.168.1.150',
                severity='Critical',
                message='Potential malware detected in downloaded file',
                file_path='C:\\Users\\John\\Downloads\\suspicious.exe',
                process_name='suspicious.exe'
            )
        ]
        
        # Check if we already have sample data
        existing_count = self.session.query(SecurityEvent).count()
        if existing_count == 0:
            for event in sample_events:
                self.session.add(event)
            
            # Add sample alerts
            sample_alerts = [
                Alert(
                    alert_type='Brute Force Attack',
                    severity='High',
                    title='Multiple Failed Login Attempts',
                    description='User admin has failed login 15 times in 5 minutes from IP 10.0.0.50',
                    source_ip='10.0.0.50',
                    affected_user='admin',
                    event_count=15
                ),
                Alert(
                    alert_type='Malware Detection',
                    severity='Critical',
                    title='Potential Malware Detected',
                    description='Suspicious executable detected on workstation',
                    source_ip='192.168.1.150',
                    affected_user='John',
                    event_count=1
                )
            ]
            
            for alert in sample_alerts:
                self.session.add(alert)
            
            self.session.commit()
            print("✅ Sample security events and alerts created")
    
    def add_event(self, **kwargs):
        """Add a new security event to the database"""
        event = SecurityEvent(**kwargs)
        self.session.add(event)
        self.session.commit()
        return event
    
    def get_recent_events(self, limit=10):
        """Get most recent security events"""
        events = self.session.query(SecurityEvent)\
                             .order_by(SecurityEvent.timestamp.desc())\
                             .limit(limit).all()
        return [event.to_dict() for event in events]
    
    def get_events_by_severity(self, severity):
        """Get events by severity level"""
        events = self.session.query(SecurityEvent)\
                             .filter(SecurityEvent.severity == severity)\
                             .order_by(SecurityEvent.timestamp.desc()).all()
        return [event.to_dict() for event in events]
    
    def get_event_statistics(self):
        """Get event statistics for dashboard"""
        total_events = self.session.query(SecurityEvent).count()
        high_severity = self.session.query(SecurityEvent)\
                                   .filter(SecurityEvent.severity == 'High').count()
        critical_severity = self.session.query(SecurityEvent)\
                                       .filter(SecurityEvent.severity == 'Critical').count()
        open_alerts = self.session.query(Alert)\
                                 .filter(Alert.status == 'Open').count()
        
        return {
            'total_events': total_events,
            'high_severity': high_severity,
            'critical_severity': critical_severity,
            'active_alerts': open_alerts
        }
    
    def create_alert(self, **kwargs):
        """Create a new alert"""
        alert = Alert(**kwargs)
        self.session.add(alert)
        self.session.commit()
        return alert
    
    def get_recent_alerts(self, limit=5):
        """Get most recent alerts"""
        alerts = self.session.query(Alert)\
                            .order_by(Alert.timestamp.desc())\
                            .limit(limit).all()
        return [alert.to_dict() for alert in alerts]
    
    def close(self):
        """Close database connection"""
        self.session.close()

# Initialize database when module is imported
if __name__ == "__main__":
    # Test the database
    db = DatabaseManager()
    print("\n📊 Database Statistics:")
    stats = db.get_event_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n🔍 Recent Events:")
    events = db.get_recent_events(3)
    for event in events:
        print(f"  {event['timestamp']} - {event['event_type']} ({event['severity']})")
    
    db.close()