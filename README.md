# 🛡️ Ultimate SIEM Security Dashboard

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Flask](https://img.shields.io/badge/flask-2.3.3-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

A comprehensive Security Information and Event Management (SIEM) dashboard built with Flask for real-time security monitoring, threat detection, and incident response.

## 🚀 Features

### 🔍 **Real-Time Security Monitoring**
- Live security event tracking and analysis
- Interactive dashboards with real-time updates
- Advanced filtering and search capabilities
- Auto-refresh functionality (30-second intervals)

### 📊 **Data Visualization**
- Interactive charts and graphs using Chart.js
- Event distribution by severity levels
- Time-series analysis of security events
- Responsive design for all device types

### 🚨 **Alert Management**
- Intelligent alert generation for critical events
- Email notifications for high-priority incidents
- Alert status tracking (Open, Investigating, Resolved)
- Customizable alert thresholds

### 📈 **Reporting & Export**
- Export security reports to Excel format
- Generate PDF reports with statistics
- Comprehensive event logging
- Historical data analysis

### 🔐 **Security Event Types**
- Failed login attempts
- Brute force attack detection
- Malware detection alerts
- Network anomaly monitoring
- Suspicious file access tracking
- Port scan detection

## 🛠️ Technology Stack

- **Backend**: Python 3.8+, Flask 2.3.3
- **Database**: SQLAlchemy ORM with SQLite
- **Frontend**: HTML5, CSS3, JavaScript
- **Charts**: Chart.js for data visualization
- **Export**: Pandas, ReportLab, OpenPyXL
- **Email**: SMTP integration for alerts

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/Khushi-Janji21/ultimate-siem-dashboard.git
   cd ultimate-siem-dashboard
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your email configuration
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the dashboard**
   Open your browser and go to: `http://127.0.0.1:5000`

## ⚙️ Configuration

### Email Alerts Setup

1. Copy `.env.example` to `.env`
2. Configure your email settings:
   ```bash
   EMAIL_ADDRESS=your-email@gmail.com
   EMAIL_PASSWORD=your-app-password  # Use App Password for Gmail
   ALERT_RECIPIENT=security-team@company.com
   ```

### Gmail Setup (Recommended)
1. Enable 2-Factor Authentication
2. Generate an App Password
3. Use the App Password in the configuration

## 🖥️ Dashboard Overview

### Main Dashboard Features
- **📊 Statistics Cards**: Total events, high severity alerts, critical events
- **📈 Interactive Charts**: Event distribution and timeline analysis
- **🔍 Advanced Filters**: Filter by severity, event type, or custom search
- **📋 Event Table**: Detailed view of all security events
- **🚨 Alert Panel**: Active alerts and their current status

### Available Actions
- **🔄 Refresh**: Manual dashboard refresh
- **➕ Add Test Event**: Generate sample security events
- **📊 Export Excel**: Download events in Excel format
- **📋 Export PDF**: Generate comprehensive PDF reports

## 🎯 Use Cases

### For Security Analysts
- Monitor real-time security events
- Investigate suspicious activities
- Generate compliance reports
- Track incident response metrics

### For IT Administrators
- System health monitoring
- Network security oversight
- User activity analysis
- Automated alert management

### For Compliance Teams
- Audit trail maintenance
- Regulatory reporting
- Security metrics tracking
- Incident documentation

## 📊 Sample Events

The dashboard comes with pre-populated sample data including:
- Failed login attempts
- Brute force attack simulations
- Malware detection events
- Network anomaly alerts
- Suspicious file access logs

## 🔧 API Endpoints

- `GET /api/events` - Retrieve security events
- `GET /api/stats` - Get dashboard statistics
- `GET /api/alerts` - Fetch active alerts
- `POST /add_test_event` - Add test security event

## 🚀 Advanced Features

### Real-Time Monitoring
- Automatic page refresh every 30 seconds
- Live event streaming
- Instant alert notifications

### Data Export
- Excel export with full event details
- PDF reports with charts and statistics
- Historical data archiving

### Responsive Design
- Mobile-friendly interface
- Tablet optimization
- Desktop full-screen support

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Flask team for the excellent web framework
- Chart.js for beautiful data visualizations
- SQLAlchemy for robust database management
- The cybersecurity community for inspiration

## 📞 Contact

**Khushi Janji**
- GitHub: [@Khushi-Janji21](https://github.com/Khushi-Janji21)
- LinkedIn: [Your LinkedIn Profile]

---

⭐ **Star this repository if you found it helpful!**

## 🖼️ Screenshots

*Add screenshots of your dashboard here*

1. **Main Dashboard View**
   - Overview of security statistics
   - Interactive charts and graphs

2. **Event Filtering Interface**
   - Advanced search capabilities
   - Real-time filtering options

3. **Alert Management Panel**
   - Active alerts display
   - Status tracking system

4. **Export Functionality**
   - Excel and PDF export options
   - Comprehensive reporting features



![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Flask](https://img.shields.io/badge/flask-2.3.3-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
