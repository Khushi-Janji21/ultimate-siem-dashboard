from flask import Flask, render_template, jsonify, request, redirect, url_for, send_file
from datetime import datetime, timedelta
import json
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
import os
from dotenv import load_dotenv
from database import DatabaseManager
# Load environment variables
load_dotenv()
# Create Flask application
app = Flask(__name__)

# Initialize database
db = DatabaseManager()

# Email configuration (you'll need to update these)
# Replace the hardcoded EMAIL_CONFIG with:
# Replace the EMAIL_CONFIG section in your app.py (around line 13-20) with this:

EMAIL_CONFIG = {
    'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
    'smtp_port': int(os.getenv('SMTP_PORT', '587')),
    'email': os.getenv('EMAIL_ADDRESS'),
    'password': os.getenv('EMAIL_PASSWORD'), 
    'recipient': os.getenv('ALERT_RECIPIENT')
}

def send_alert_email(event_data):
    """Send email alert for critical events"""
    try:
        # Check if email configuration is available
        if not all([EMAIL_CONFIG['email'], EMAIL_CONFIG['password'], EMAIL_CONFIG['recipient']]):
            print("⚠️ Email configuration not complete. Skipping email alert.")
            return False
            
        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG['email']
        msg['To'] = EMAIL_CONFIG['recipient']
        msg['Subject'] = f"🚨 CRITICAL SECURITY ALERT - {event_data['event_type']}"
        
        body = f"""
        CRITICAL SECURITY EVENT DETECTED
        
        Event Type: {event_data['event_type']}
        Severity: {event_data['severity']}
        Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        Source IP: {event_data.get('source_ip', 'Unknown')}
        Message: {event_data['message']}
        
        Please investigate immediately.
        
        SIEM Dashboard: http://127.0.0.1:5000
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
        server.starttls()
        server.login(EMAIL_CONFIG['email'], EMAIL_CONFIG['password'])
        server.send_message(msg)
        server.quit()
        
        print(f"✅ Email alert sent for {event_data['event_type']}")
        return True
    except Exception as e:
        print(f"❌ Email alert failed: {str(e)}")
        return False
# Route for main dashboard
@app.route('/')
def dashboard():
    # Get filter parameters
    severity_filter = request.args.get('severity', '')
    event_type_filter = request.args.get('event_type', '')
    search_query = request.args.get('search', '')
    
    # Get data from database
    stats = db.get_event_statistics()
    
    # Apply filters
    if severity_filter or event_type_filter or search_query:
        events = get_filtered_events(severity_filter, event_type_filter, search_query)
    else:
        events = db.get_recent_events(20)
    
    recent_alerts = db.get_recent_alerts(5)
    
    # Get chart data
    chart_data = get_chart_data()
    
    # Generate HTML table rows for events
    event_rows = ""
    for event in events[:10]:  # Show only first 10 for display
        severity_class = f"severity-{event['severity'].lower()}"
        event_rows += f"""
                    <tr>
                        <td>{event['timestamp']}</td>
                        <td>{event['event_type']}</td>
                        <td>{event['source_ip'] or 'N/A'}</td>
                        <td><span class="{severity_class}">{event['severity']}</span></td>
                        <td title="{event['message']}">{event['message'][:60]}{'...' if len(event['message']) > 60 else ''}</td>
                    </tr>
        """
    
    # Generate alert rows
    alert_rows = ""
    for alert in recent_alerts:
        status_class = f"status-{alert['status'].lower()}"
        alert_rows += f"""
                    <tr>
                        <td>{alert['timestamp']}</td>
                        <td>{alert['alert_type']}</td>
                        <td><span class="severity-{alert['severity'].lower()}">{alert['severity']}</span></td>
                        <td><span class="{status_class}">{alert['status']}</span></td>
                        <td>{alert['title']}</td>
                    </tr>
        """
    
    # Get unique event types for filter dropdown
    all_events = db.get_recent_events(100)
    event_types = list(set([event['event_type'] for event in all_events]))
    event_types.sort()
    
    # Generate filter options
    event_type_options = ""
    for et in event_types:
        selected = "selected" if et == event_type_filter else ""
        event_type_options += f'<option value="{et}" {selected}>{et}</option>'
    
    severity_options = ""
    for sev in ['Low', 'Medium', 'High', 'Critical']:
        selected = "selected" if sev == severity_filter else ""
        severity_options += f'<option value="{sev}" {selected}>{sev}</option>'
    
    # Return the ultimate HTML
    html_content = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Ultimate SIEM Dashboard</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js"></script>
        <style>
            body {{ 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                margin: 0; 
                padding: 20px; 
                background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
                color: white; 
                min-height: 100vh;
            }}
            .header {{ 
                background: linear-gradient(135deg, #2c2c2c 0%, #3c3c3c 100%);
                padding: 30px; 
                border-radius: 15px; 
                margin-bottom: 30px; 
                text-align: center;
                box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            }}
            .header h1 {{
                margin: 0;
                font-size: 2.5em;
                background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
                background-clip: text;
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }}
            .stats {{ 
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px; 
                margin-bottom: 30px; 
            }}
            .stat-card {{ 
                background: linear-gradient(135deg, #2c2c2c 0%, #3c3c3c 100%);
                padding: 25px; 
                border-radius: 15px; 
                text-align: center;
                box-shadow: 0 8px 32px rgba(0,0,0,0.3);
                transition: transform 0.3s ease;
            }}
            .stat-card:hover {{
                transform: translateY(-5px);
            }}
            .stat-card h2 {{
                font-size: 3em;
                margin: 10px 0;
                text-shadow: 0 0 20px rgba(255,255,255,0.1);
            }}
            
            .charts-section {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                margin-bottom: 30px;
            }}
            .chart-container {{
                background: linear-gradient(135deg, #2c2c2c 0%, #3c3c3c 100%);
                padding: 25px;
                border-radius: 15px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.3);
                height: 400px;
            }}
            
            .filters-section {{
                background: linear-gradient(135deg, #2c2c2c 0%, #3c3c3c 100%);
                padding: 20px;
                border-radius: 15px;
                margin-bottom: 20px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            }}
            .filters-section h3 {{
                margin-top: 0;
            }}
            .filter-row {{
                display: flex;
                gap: 15px;
                align-items: center;
                flex-wrap: wrap;
            }}
            .filter-group {{
                display: flex;
                flex-direction: column;
                gap: 5px;
            }}
            .filter-group label {{
                font-size: 14px;
                color: #ccc;
            }}
            select, input[type="text"] {{
                padding: 8px 12px;
                border: 1px solid #555;
                border-radius: 8px;
                background: #1a1a1a;
                color: white;
                font-size: 14px;
            }}
            .btn {{
                padding: 10px 20px;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-weight: bold;
                transition: all 0.3s ease;
                text-decoration: none;
                display: inline-block;
            }}
            .btn-primary {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }}
            .btn-success {{
                background: linear-gradient(135deg, #1dd1a1 0%, #10ac84 100%);
                color: white;
            }}
            .btn-warning {{
                background: linear-gradient(135deg, #feca57 0%, #ff9ff3 100%);
                color: white;
            }}
            .btn-danger {{
                background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
                color: white;
            }}
            .btn:hover {{
                transform: scale(1.05);
                box-shadow: 0 5px 15px rgba(0,0,0,0.3);
            }}
            
            .action-buttons {{
                position: fixed;
                top: 20px;
                right: 20px;
                display: flex;
                flex-direction: column;
                gap: 10px;
                z-index: 1000;
            }}
            
            .content-grid {{
                display: grid;
                grid-template-columns: 2fr 1fr;
                gap: 20px;
            }}
            .events-table, .alerts-table {{ 
                background: linear-gradient(135deg, #2c2c2c 0%, #3c3c3c 100%);
                padding: 25px; 
                border-radius: 15px; 
                box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            }}
            table {{ 
                width: 100%; 
                border-collapse: collapse; 
            }}
            th, td {{ 
                padding: 12px; 
                text-align: left; 
                border-bottom: 1px solid #444; 
            }}
            th {{ 
                background: linear-gradient(135deg, #3c3c3c 0%, #4c4c4c 100%);
                font-weight: 600;
                position: sticky;
                top: 0;
            }}
            .severity-high {{ color: #ff6b6b; font-weight: bold; }}
            .severity-medium {{ color: #feca57; font-weight: bold; }}
            .severity-critical {{ color: #ff3838; font-weight: bold; text-shadow: 0 0 10px rgba(255,56,56,0.5); }}
            .severity-low {{ color: #48dbfb; }}
            .status-open {{ color: #ff6b6b; }}
            .status-investigating {{ color: #feca57; }}
            .status-resolved {{ color: #1dd1a1; }}
            
            @media (max-width: 768px) {{
                .content-grid, .charts-section {{
                    grid-template-columns: 1fr;
                }}
                .stats {{
                    grid-template-columns: repeat(2, 1fr);
                }}
                .filter-row {{
                    flex-direction: column;
                    align-items: stretch;
                }}
                .action-buttons {{
                    position: relative;
                    top: auto;
                    right: auto;
                    flex-direction: row;
                    margin-bottom: 20px;
                }}
            }}
        </style>
        <script>
            let refreshInterval;
            function startAutoRefresh() {{
                refreshInterval = setInterval(function(){{
                    location.reload();
                }}, 30000);
            }}
            
            function refreshNow() {{
                location.reload();
            }}
            
            function addTestEvent() {{
                fetch('/add_test_event', {{method: 'POST'}})
                .then(() => location.reload());
            }}
            
            function applyFilters() {{
                const severity = document.getElementById('severityFilter').value;
                const eventType = document.getElementById('eventTypeFilter').value;
                const search = document.getElementById('searchInput').value;
                
                let url = '/?';
                if (severity) url += 'severity=' + severity + '&';
                if (eventType) url += 'event_type=' + eventType + '&';
                if (search) url += 'search=' + search + '&';
                
                window.location.href = url;
            }}
            
            function clearFilters() {{
                window.location.href = '/';
            }}
        </script>
    </head>
    <body onload="startAutoRefresh()">
        <div class="action-buttons">
            <button class="btn btn-primary" onclick="refreshNow()">🔄 Refresh</button>
            <button class="btn btn-success" onclick="addTestEvent()">+ Add Test Event</button>
            <a href="/export/excel" class="btn btn-warning">📊 Export Excel</a>
            <a href="/export/pdf" class="btn btn-danger">📋 Export PDF</a>
        </div>
        
        <div class="header">
            <h1>🛡️ Ultimate SIEM Security Dashboard</h1>
            <p>Advanced Security Event Monitoring & Threat Detection</p>
            <p style="font-size: 14px; opacity: 0.7;">Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <h3>📊 Total Events</h3>
                <h2>{stats['total_events']}</h2>
            </div>
            <div class="stat-card">
                <h3>⚠️ High Severity</h3>
                <h2 style="color: #ff6b6b;">{stats['high_severity']}</h2>
            </div>
            <div class="stat-card">
                <h3>🚨 Critical Events</h3>
                <h2 style="color: #ff3838;">{stats['critical_severity']}</h2>
            </div>
            <div class="stat-card">
                <h3>🔔 Active Alerts</h3>
                <h2 style="color: #feca57;">{stats['active_alerts']}</h2>
            </div>
        </div>
        
        <div class="charts-section">
            <div class="chart-container">
                <h3>📈 Events by Severity</h3>
                <canvas id="severityChart"></canvas>
            </div>
            <div class="chart-container">
                <h3>📅 Events Over Time</h3>
                <canvas id="timeChart"></canvas>
            </div>
        </div>
        
        <div class="filters-section">
            <h3>🔍 Search & Filter Events</h3>
            <div class="filter-row">
                <div class="filter-group">
                    <label>Severity:</label>
                    <select id="severityFilter">
                        <option value="">All Severities</option>
                        {severity_options}
                    </select>
                </div>
                <div class="filter-group">
                    <label>Event Type:</label>
                    <select id="eventTypeFilter">
                        <option value="">All Types</option>
                        {event_type_options}
                    </select>
                </div>
                <div class="filter-group">
                    <label>Search:</label>
                    <input type="text" id="searchInput" placeholder="Search in messages..." value="{search_query}">
                </div>
                <div class="filter-group" style="justify-content: flex-end; margin-top: 20px;">
                    <button class="btn btn-primary" onclick="applyFilters()">Apply Filters</button>
                    <button class="btn btn-secondary" onclick="clearFilters()">Clear</button>
                </div>
            </div>
        </div>
        
        <div class="content-grid">
            <div class="events-table">
                <h3>🔍 Security Events ({len(events)} found)</h3>
                <table id="eventsTable">
                    <thead>
                        <tr>
                            <th>⏰ Time</th>
                            <th>🎯 Event Type</th>
                            <th>🌐 Source IP</th>
                            <th>⚡ Severity</th>
                            <th>💬 Message</th>
                        </tr>
                    </thead>
                    <tbody>
                        {event_rows}
                    </tbody>
                </table>
            </div>
            
            <div class="alerts-table">
                <h3>🚨 Active Alerts</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Time</th>
                            <th>Type</th>
                            <th>Severity</th>
                            <th>Status</th>
                            <th>Title</th>
                        </tr>
                    </thead>
                    <tbody>
                        {alert_rows}
                    </tbody>
                </table>
            </div>
        </div>
        
        <script>
            // Initialize Charts
            const ctx1 = document.getElementById('severityChart').getContext('2d');
            new Chart(ctx1, {{
                type: 'doughnut',
                data: {{
                    labels: {json.dumps(chart_data['severity_labels'])},
                    datasets: [{{
                        data: {json.dumps(chart_data['severity_counts'])},
                        backgroundColor: ['#48dbfb', '#feca57', '#ff6b6b', '#ff3838']
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{
                            labels: {{ color: 'white' }}
                        }}
                    }}
                }}
            }});
            
            const ctx2 = document.getElementById('timeChart').getContext('2d');
            new Chart(ctx2, {{
                type: 'line',
                data: {{
                    labels: {json.dumps(chart_data['time_labels'])},
                    datasets: [{{
                        label: 'Events',
                        data: {json.dumps(chart_data['time_counts'])},
                        borderColor: '#4ecdc4',
                        backgroundColor: 'rgba(78, 205, 196, 0.1)',
                        fill: true
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        y: {{
                            ticks: {{ color: 'white' }}
                        }},
                        x: {{
                            ticks: {{ color: 'white' }}
                        }}
                    }},
                    plugins: {{
                        legend: {{
                            labels: {{ color: 'white' }}
                        }}
                    }}
                }}
            }});
            
            console.log("🎉 Ultimate SIEM Dashboard Loaded!");
            console.log("📊 Stats:", {json.dumps(stats)});
            console.log("🔄 Auto-refresh: Every 30 seconds");
        </script>
    </body>
    </html>
    '''
    
    return html_content

def get_filtered_events(severity_filter, event_type_filter, search_query):
    """Get filtered events from database"""
    # This is a simplified version - you might want to add SQL filtering
    all_events = db.get_recent_events(100)
    filtered_events = []
    
    for event in all_events:
        # Apply severity filter
        if severity_filter and event['severity'] != severity_filter:
            continue
            
        # Apply event type filter
        if event_type_filter and event['event_type'] != event_type_filter:
            continue
            
        # Apply search filter
        if search_query:
            search_lower = search_query.lower()
            if not any([
                search_lower in event['message'].lower(),
                search_lower in event['event_type'].lower(),
                search_lower in (event['source_ip'] or '').lower()
            ]):
                continue
        
        filtered_events.append(event)
    
    return filtered_events

def get_chart_data():
    """Get data for charts"""
    events = db.get_recent_events(100)
    
    # Severity distribution
    severity_counts = {'Low': 0, 'Medium': 0, 'High': 0, 'Critical': 0}
    for event in events:
        severity_counts[event['severity']] += 1
    
    # Events over time (last 7 days)
    time_counts = []
    time_labels = []
    for i in range(7):
        date = datetime.now() - timedelta(days=6-i)
        date_str = date.strftime('%m/%d')
        time_labels.append(date_str)
        
        # Count events for this date (simplified - just random data for demo)
        count = len([e for e in events if date_str in e['timestamp']])
        time_counts.append(count if count > 0 else random.randint(0, 5))
    
    return {
        'severity_labels': list(severity_counts.keys()),
        'severity_counts': list(severity_counts.values()),
        'time_labels': time_labels,
        'time_counts': time_counts
    }

# Route to add test events
@app.route('/add_test_event', methods=['POST'])
def add_test_event():
    test_events = [
        {
            'event_type': 'Suspicious Login',
            'source_ip': f'192.168.1.{random.randint(100, 200)}',
            'severity': random.choice(['High', 'Critical']),
            'message': f'Login from unusual location at {datetime.now().strftime("%H:%M:%S")}',
            'username': random.choice(['admin', 'user1', 'guest'])
        },
        {
            'event_type': 'Malware Detection',
            'source_ip': f'10.0.0.{random.randint(10, 100)}',
            'severity': 'Critical',
            'message': f'Potential malware detected at {datetime.now().strftime("%H:%M:%S")}',
            'file_path': f'/downloads/suspicious_{random.randint(1,999)}.exe'
        },
        {
            'event_type': 'Network Anomaly',
            'source_ip': f'203.0.113.{random.randint(1, 50)}',
            'severity': random.choice(['Medium', 'High']),
            'message': f'Unusual traffic pattern detected at {datetime.now().strftime("%H:%M:%S")}',
            'protocol': 'TCP'
        }
    ]
    
    event_data = random.choice(test_events)
    db.add_event(**event_data)
    
    # Send email alert for critical events
    if event_data['severity'] == 'Critical':
        send_alert_email(event_data)
    
    return jsonify({'status': 'success', 'message': 'Test event added'})

# Export routes
@app.route('/export/excel')
def export_excel():
    """Export events to Excel"""
    try:
        events = db.get_recent_events(100)
        df = pd.DataFrame(events)
        
        # Create Excel file in memory
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Security Events', index=False)
        
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'security_events_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/export/pdf')
def export_pdf():
    """Export events to PDF"""
    try:
        events = db.get_recent_events(20)
        stats = db.get_event_statistics()
        
        # Create PDF in memory
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        
        # Title
        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, 750, f"SIEM Security Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Stats
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, 720, "Statistics:")
        p.setFont("Helvetica", 10)
        y = 700
        for key, value in stats.items():
            p.drawString(70, y, f"{key.replace('_', ' ').title()}: {value}")
            y -= 20
        
        # Events table
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y-20, "Recent Security Events:")
        
        y -= 50
        p.setFont("Helvetica", 8)
        for event in events[:15]:  # Limit to 15 events
            if y < 100:  # Start new page if needed
                p.showPage()
                y = 750
            
            p.drawString(50, y, f"{event['timestamp']} | {event['event_type']} | {event['severity']}")
            y -= 10
            p.drawString(70, y, f"IP: {event['source_ip'] or 'N/A'} | {event['message'][:80]}...")
            y -= 20
        
        p.save()
        buffer.seek(0)
        
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'security_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API endpoints
@app.route('/api/events')
def get_events():
    events = db.get_recent_events(50)
    return jsonify(events)

@app.route('/api/stats')
def get_stats():
    stats = db.get_event_statistics()
    return jsonify(stats)

@app.route('/api/alerts')
def get_alerts():
    alerts = db.get_recent_alerts(10)
    return jsonify(alerts)

# Run the application
if __name__ == '__main__':
    print("🚀 Starting ULTIMATE SIEM Dashboard...")
    print("🌐 Open your browser and go to: http://127.0.0.1:5000")
    print("✨ New Features:")
    print("   📊 Interactive Charts & Graphs")
    print("   🔍 Advanced Search & Filtering") 
    print("   📧 Email Alerts for Critical Events")
    print("   📋 Export to Excel & PDF")
    print("   🎨 Enhanced UI with animations")
    print("   📱 Fully responsive design")
    app.run(debug=True, host='127.0.0.1', port=5000)