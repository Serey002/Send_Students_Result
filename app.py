from flask import Flask, render_template, request, jsonify, session, send_file
from flask_mail import Mail
import sqlite3
import os
import json
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import pandas as pd
from io import BytesIO

from config import Config
from utils.email_service import EmailService
from utils.file_processor import FileProcessor
from utils.helpers import allowed_file, generate_report

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
mail = Mail(app)
email_service = EmailService(app, mail)
file_processor = FileProcessor()

# Ensure directories exist
for directory in ['uploads', 'database', 'logs']:
    os.makedirs(directory, exist_ok=True)

def get_db_connection():
    conn = sqlite3.connect(app.config['DATABASE_PATH'])
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    
    # Students table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            score REAL NOT NULL,
            subject TEXT,
            semester TEXT,
            sent BOOLEAN DEFAULT FALSE,
            sent_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Email logs table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS email_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_email TEXT,
            student_name TEXT,
            status TEXT,
            sent_at TIMESTAMP,
            error_message TEXT,
            batch_id TEXT
        )
    ''')
    
    # Email templates table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS email_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            subject TEXT,
            content TEXT,
            is_default BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert default template
    default_template = '''
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
            .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }
            .content { padding: 30px; background: #f9f9f9; border-radius: 0 0 10px 10px; }
            .score-card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin: 20px 0; }
            .grade { font-size: 24px; font-weight: bold; color: #4CAF50; }
            .footer { text-align: center; margin-top: 20px; color: #666; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Academic Results</h1>
            </div>
            <div class="content">
                <p>Dear {{student_name}},</p>
                <p>We are pleased to inform you about your academic performance:</p>
                
                <div class="score-card">
                    <h3>Result Details</h3>
                    <p><strong>Subject:</strong> {{subject}}</p>
                    <p><strong>Score:</strong> {{score}}/100</p>
                    <p><strong>Grade:</strong> <span class="grade">{{grade}}</span></p>
                    <p><strong>Semester:</strong> {{semester}}</p>
                </div>
                
                <p>{{custom_message}}</p>
                <p>Keep up the great work!</p>
            </div>
            <div class="footer">
                <p>Best regards,<br>Academic Department</p>
            </div>
        </div>
    </body>
    </html>
    '''
    
    conn.execute('''
        INSERT OR IGNORE INTO email_templates (name, subject, content, is_default)
        VALUES (?, ?, ?, ?)
    ''', ('Default Template', 'Your Academic Results - {{subject}}', default_template, True))
    
    conn.commit()
    conn.close()

init_db()

# Routes
@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/upload')
def upload_page():
    return render_template('upload.html')

@app.route('/logs')
def logs_page():
    return render_template('logs.html')

# API Routes
@app.route('/api/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file selected'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'})
        
        if file and allowed_file(file.filename, app.config['ALLOWED_EXTENSIONS']):
            # Process file
            result = file_processor.process_file(file)
            
            if not result['success']:
                return jsonify({'success': False, 'error': result['error']})
            
            # Store in database
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Clear previous unsent data
            cursor.execute('DELETE FROM students WHERE sent = FALSE')
            
            for student in result['data']:
                cursor.execute('''
                    INSERT INTO students (name, email, score, subject, semester)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    student['name'], 
                    student['email'], 
                    student['score'], 
                    student.get('subject', 'General'),
                    student.get('semester', 'Spring 2024')
                ))
            
            conn.commit()
            conn.close()
            
            return jsonify({
                'success': True,
                'message': f'Successfully uploaded {len(result["data"])} student records',
                'data': result['data'],
                'stats': result['stats']
            })
            
        return jsonify({'success': False, 'error': 'Invalid file type'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error processing file: {str(e)}'})

@app.route('/api/students')
def get_students():
    try:
        conn = get_db_connection()
        
        status = request.args.get('status', 'all')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        query = 'SELECT * FROM students WHERE 1=1'
        count_query = 'SELECT COUNT(*) FROM students WHERE 1=1'
        params = []
        
        if status == 'sent':
            query += ' AND sent = TRUE'
            count_query += ' AND sent = TRUE'
        elif status == 'unsent':
            query += ' AND sent = FALSE'
            count_query += ' AND sent = FALSE'
        
        # Get total count
        total = conn.execute(count_query, params).fetchone()[0]
        
        # Add pagination
        query += ' ORDER BY created_at DESC LIMIT ? OFFSET ?'
        params.extend([per_page, (page - 1) * per_page])
        
        students = conn.execute(query, params).fetchall()
        
        student_list = []
        for student in students:
            student_list.append(dict(student))
        
        conn.close()
        
        return jsonify({
            'success': True,
            'students': student_list,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/send-emails', methods=['POST'])
def send_emails():
    try:
        data = request.get_json()
        batch_size = data.get('batch_size', app.config['BATCH_SIZE'])
        
        result = email_service.send_bulk_emails(batch_size)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/dashboard-stats')
def dashboard_stats():
    try:
        conn = get_db_connection()
        
        # Basic stats
        total_students = conn.execute('SELECT COUNT(*) FROM students').fetchone()[0]
        sent_emails = conn.execute('SELECT COUNT(*) FROM students WHERE sent = TRUE').fetchone()[0]
        unsent_emails = conn.execute('SELECT COUNT(*) FROM students WHERE sent = FALSE').fetchone()[0]
        
        # Recent activity
        recent_logs = conn.execute('''
            SELECT * FROM email_logs 
            ORDER BY sent_at DESC 
            LIMIT 5
        ''').fetchall()
        
        # Subject distribution
        subject_stats = conn.execute('''
            SELECT subject, COUNT(*) as count, AVG(score) as avg_score
            FROM students 
            GROUP BY subject
        ''').fetchall()
        
        # Daily sent stats (last 7 days)
        daily_stats = conn.execute('''
            SELECT DATE(sent_at) as date, COUNT(*) as count
            FROM email_logs 
            WHERE status = 'sent' AND sent_at >= DATE('now', '-7 days')
            GROUP BY DATE(sent_at)
            ORDER BY date
        ''').fetchall()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_students': total_students,
                'sent_emails': sent_emails,
                'unsent_emails': unsent_emails,
                'completion_rate': (sent_emails / total_students * 100) if total_students > 0 else 0
            },
            'recent_activity': [dict(log) for log in recent_logs],
            'subject_stats': [dict(stat) for stat in subject_stats],
            'daily_stats': [dict(stat) for stat in daily_stats]
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/export-logs')
def export_logs():
    try:
        format_type = request.args.get('format', 'csv')
        
        conn = get_db_connection()
        logs = conn.execute('SELECT * FROM email_logs ORDER BY sent_at DESC').fetchall()
        conn.close()
        
        if format_type == 'csv':
            df = pd.DataFrame([dict(log) for log in logs])
            output = BytesIO()
            df.to_csv(output, index=False)
            output.seek(0)
            
            return send_file(
                output,
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'email_logs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            )
        else:
            return jsonify({'success': True, 'logs': [dict(log) for log in logs]})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)