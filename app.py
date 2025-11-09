from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, send_file, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
import pandas as pd
import os
import json
from datetime import datetime
import logging
from io import BytesIO
import secrets
import tempfile

from config import Config

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = 'your-secret-key-here'  # Required for sessions

# Ensure database directory exists
db_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database')
os.makedirs(db_dir, exist_ok=True)

# Update SQLALCHEMY_DATABASE_URI to use absolute path
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(db_dir, "results.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
mail = Mail(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database Models
class StudentResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(50), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    class_name = db.Column(db.String(50), nullable=False)
    final_english = db.Column(db.Float, nullable=False)
    final_english_it = db.Column(db.Float, nullable=False)
    final_pl = db.Column(db.Float, nullable=False)
    final_algorithm = db.Column(db.Float, nullable=False)
    final_web_design = db.Column(db.Float, nullable=False)
    final_git = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)
    grade = db.Column(db.String(10), nullable=False)
    comments = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class EmailLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(20), nullable=False)  # sent, failed
    error_message = db.Column(db.Text)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    batch_id = db.Column(db.String(32), nullable=False)

# Helper Functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def calculate_grade(total_score):
    if total_score >= 90:
        return 'A'
    elif total_score >= 80:
        return 'B'
    elif total_score >= 70:
        return 'C'
    elif total_score >= 60:
        return 'D'
    else:
        return 'F'

def generate_email_template(student_data):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 20px; border-radius: 0 0 10px 10px; }}
            .result-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            .result-table th, .result-table td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            .result-table th {{ background-color: #667eea; color: white; }}
            .grade-{student_data['grade'].lower()} {{ 
                font-weight: bold; 
                padding: 5px 10px; 
                border-radius: 5px; 
                color: white;
            }}
            .grade-a {{ background-color: #28a745; }}
            .grade-b {{ background-color: #17a2b8; }}
            .grade-c {{ background-color: #ffc107; color: black; }}
            .grade-d {{ background-color: #fd7e14; }}
            .grade-f {{ background-color: #dc3545; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Academic Results</h1>
                <p>Semester Examination Results</p>
            </div>
            <div class="content">
                <h2>Dear {student_data['first_name']} {student_data['last_name']},</h2>
                <p>We are pleased to inform you that your examination results for the current semester are now available.</p>
                
                <h3>Your Results:</h3>
                <table class="result-table">
                    <tr>
                        <th>Subject</th>
                        <th>Score</th>
                    </tr>
                    <tr><td>Final English</td><td>{student_data['final_english']}</td></tr>
                    <tr><td>Final English IT</td><td>{student_data['final_english_it']}</td></tr>
                    <tr><td>Final Professional Life</td><td>{student_data['final_pl']}</td></tr>
                    <tr><td>Final Algorithm</td><td>{student_data['final_algorithm']}</td></tr>
                    <tr><td>Final Web Design</td><td>{student_data['final_web_design']}</td></tr>
                    <tr><td>Final Git</td><td>{student_data['final_git']}</td></tr>
                    <tr style="background-color: #e9ecef;">
                        <td><strong>Total Score</strong></td>
                        <td><strong>{student_data['total']}</strong></td>
                    </tr>
                    <tr style="background-color: #e9ecef;">
                        <td><strong>Grade</strong></td>
                        <td><span class="grade-{student_data['grade'].lower()}">{student_data['grade']}</span></td>
                    </tr>
                </table>
                
                <h3>Comments:</h3>
                <p>{student_data['comments']}</p>
                
                <p>If you have any questions or concerns about your results, please don't hesitate to contact your academic advisor.</p>
                
                <p>Best regards,<br>Academic Department of Passerelles Numeriques</p>
            </div>
        </div>
    </body>
    </html>
    """

# Global variable to store temporary student data (for demo purposes)
# In production, use a proper caching system like Redis
_temp_student_data = {}

# Routes
@app.route('/')
def index():
    stats = {
        'total_students': StudentResult.query.count(),
        'sent_emails': EmailLog.query.filter_by(status='sent').count(),
        'failed_emails': EmailLog.query.filter_by(status='failed').count()
    }
    return render_template('index.html', stats=stats)

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            try:
                # Read file
                if file.filename.endswith('.csv'):
                    df = pd.read_csv(file)
                else:
                    df = pd.read_excel(file)
                
                # Validate required columns
                required_columns = ['first_name', 'last_name', 'email', 'class', 
                                  'final_english', 'final_english_it', 'final_pl', 
                                  'final_algorithm', 'final_web_design', 'final_git']
                
                missing_columns = [col for col in required_columns if col not in df.columns]
                if missing_columns:
                    flash(f'Missing required columns: {", ".join(missing_columns)}', 'error')
                    return redirect(request.url)
                
                # Process data
                students_data = []
                for index, row in df.iterrows():
                    total_score = sum([
                        float(row['final_english']), 
                        float(row['final_english_it']), 
                        float(row['final_pl']),
                        float(row['final_algorithm']), 
                        float(row['final_web_design']), 
                        float(row['final_git'])
                    ])
                    
                    student_data = {
                        'student_id': f"STU{secrets.token_hex(4).upper()}",
                        'first_name': str(row['first_name']),
                        'last_name': str(row['last_name']),
                        'email': str(row['email']),
                        'class_name': str(row['class']),
                        'final_english': float(row['final_english']),
                        'final_english_it': float(row['final_english_it']),
                        'final_pl': float(row['final_pl']),
                        'final_algorithm': float(row['final_algorithm']),
                        'final_web_design': float(row['final_web_design']),
                        'final_git': float(row['final_git']),
                        'total': total_score,
                        'grade': calculate_grade(total_score),
                        'comments': row.get('comments', 'Good work! Keep it up.')
                    }
                    students_data.append(student_data)
                
                # Store in session for preview
                session_id = secrets.token_hex(16)
                _temp_student_data[session_id] = students_data
                session['upload_session_id'] = session_id
                
                return redirect(url_for('preview_data'))
                
            except Exception as e:
                flash(f'Error processing file: {str(e)}', 'error')
                return redirect(request.url)
        else:
            flash('Invalid file type. Please upload CSV or Excel files.', 'error')
            return redirect(request.url)
    
    return render_template('upload.html')

@app.route('/preview')
def preview_data():
    session_id = session.get('upload_session_id')
    if not session_id or session_id not in _temp_student_data:
        flash('No data to preview. Please upload a file first.', 'error')
        return redirect(url_for('upload_file'))
    
    students_data = _temp_student_data[session_id]
    return render_template('preview.html', students=students_data)

@app.route('/send-emails', methods=['POST'])
def send_emails():
    session_id = session.get('upload_session_id')
    if not session_id or session_id not in _temp_student_data:
        return jsonify({'success': False, 'message': 'No student data found. Please upload a file first.'})
    
    students_data = _temp_student_data[session_id]
    batch_id = secrets.token_hex(16)
    results = {'sent': 0, 'failed': 0, 'details': []}
    
    for student_data in students_data:
        try:
            # Check if student already exists
            existing_student = StudentResult.query.filter_by(email=student_data['email']).first()
            if existing_student:
                # Update existing record
                for key, value in student_data.items():
                    if hasattr(existing_student, key) and key != 'id':
                        setattr(existing_student, key, value)
            else:
                # Create new record
                student = StudentResult(**student_data)
                db.session.add(student)
            
            db.session.commit()
            
            # Send email
            email_html = generate_email_template(student_data)
            msg = Message(
                subject=f"Your Academic Results - {student_data['first_name']} {student_data['last_name']}",
                recipients=[student_data['email']],
                html=email_html
            )
            
            mail.send(msg)
            
            # Log success
            log = EmailLog(
                student_id=student_data['student_id'],
                email=student_data['email'],
                status='sent',
                batch_id=batch_id
            )
            db.session.add(log)
            results['sent'] += 1
            results['details'].append({
                'student': f"{student_data['first_name']} {student_data['last_name']}",
                'email': student_data['email'],
                'status': 'sent'
            })
            
        except Exception as e:
            # Log failure
            log = EmailLog(
                student_id=student_data.get('student_id', 'UNKNOWN'),
                email=student_data['email'],
                status='failed',
                error_message=str(e),
                batch_id=batch_id
            )
            db.session.add(log)
            results['failed'] += 1
            results['details'].append({
                'student': f"{student_data['first_name']} {student_data['last_name']}",
                'email': student_data['email'],
                'status': 'failed',
                'error': str(e)
            })
        
        db.session.commit()
    
    # Clear temporary data
    if session_id in _temp_student_data:
        del _temp_student_data[session_id]
    session.pop('upload_session_id', None)
    
    return jsonify({
        'success': True,
        'message': f'Emails sent successfully! Sent: {results["sent"]}, Failed: {results["failed"]}',
        'results': results
    })

@app.route('/results')
def view_results():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    students = StudentResult.query.order_by(StudentResult.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('results.html', students=students)

@app.route('/logs')
def view_logs():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    logs = EmailLog.query.order_by(EmailLog.sent_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('logs.html', logs=logs)

@app.route('/export-logs')
def export_logs():
    logs = EmailLog.query.all()
    
    data = []
    for log in logs:
        data.append({
            'Student ID': log.student_id,
            'Email': log.email,
            'Status': log.status,
            'Error Message': log.error_message or '',
            'Sent At': log.sent_at.strftime('%Y-%m-%d %H:%M:%S'),
            'Batch ID': log.batch_id
        })
    
    df = pd.DataFrame(data)
    output = BytesIO()
    df.to_csv(output, index=False)
    output.seek(0)
    
    return send_file(
        output,
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'email_logs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )

@app.route('/api/stats')
def api_stats():
    stats = {
        'total_students': StudentResult.query.count(),
        'sent_emails': EmailLog.query.filter_by(status='sent').count(),
        'failed_emails': EmailLog.query.filter_by(status='failed').count(),
        'success_rate': 0
    }
    
    total_emails = stats['sent_emails'] + stats['failed_emails']
    if total_emails > 0:
        stats['success_rate'] = round((stats['sent_emails'] / total_emails) * 100, 2)
    
    return jsonify(stats)

@app.route('/clear-data', methods=['POST'])
def clear_data():
    """Clear all data (for testing purposes)"""
    try:
        # Clear all records
        StudentResult.query.delete()
        EmailLog.query.delete()
        db.session.commit()
        
        # Clear temporary data
        _temp_student_data.clear()
        session.clear()
        
        flash('All data cleared successfully', 'success')
    except Exception as e:
        flash(f'Error clearing data: {str(e)}', 'error')
    
    return redirect(url_for('index'))

# Error handlers
@app.errorhandler(413)
def too_large(e):
    flash('File too large. Please upload files smaller than 16MB.', 'error')
    return redirect(url_for('upload_file'))

@app.errorhandler(500)
def internal_error(error):
    flash('An internal error occurred. Please try again.', 'error')
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    # Create uploads directory if it doesn't exist
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('database', exist_ok=True)
    
    app.run(debug=True)