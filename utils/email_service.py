import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import sqlite3
from datetime import datetime
import time
import threading
from flask_mail import Message

class EmailService:
    def __init__(self, app, mail):
        self.app = app
        self.mail = mail
        self.rate_limit_count = 0
        self.rate_limit_start = time.time()
    
    def get_db_connection(self):
        conn = sqlite3.connect(self.app.config['DATABASE_PATH'])
        conn.row_factory = sqlite3.Row
        return conn
    
    def get_email_template(self, template_name='Default Template'):
        conn = self.get_db_connection()
        template = conn.execute(
            'SELECT * FROM email_templates WHERE name = ?', 
            (template_name,)
        ).fetchone()
        conn.close()
        return dict(template) if template else None
    
    def create_personalized_email(self, student, template):
        grade = self.calculate_grade(student['score'])
        
        # Replace template variables
        email_content = template['content']
        email_content = email_content.replace('{{student_name}}', student['name'])
        email_content = email_content.replace('{{subject}}', student.get('subject', 'General'))
        email_content = email_content.replace('{{score}}', str(student['score']))
        email_content = email_content.replace('{{grade}}', grade)
        email_content = email_content.replace('{{semester}}', student.get('semester', 'Spring 2024'))
        email_content = email_content.replace('{{custom_message}}', self.get_custom_message(student['score']))
        
        email_subject = template['subject']
        email_subject = email_subject.replace('{{subject}}', student.get('subject', 'General'))
        email_subject = email_subject.replace('{{student_name}}', student['name'])
        
        return email_subject, email_content
    
    def calculate_grade(self, score):
        if score >= 90: return "A"
        elif score >= 80: return "B"
        elif score >= 70: return "C"
        elif score >= 60: return "D"
        else: return "F"
    
    def get_custom_message(self, score):
        if score >= 90:
            return "Outstanding performance! You have demonstrated exceptional understanding of the subject."
        elif score >= 80:
            return "Excellent work! You have shown great proficiency in the subject."
        elif score >= 70:
            return "Good job! You have a solid understanding of the material."
        elif score >= 60:
            return "Satisfactory performance. Consider reviewing areas for improvement."
        else:
            return "We encourage you to meet with your instructor to discuss improvement strategies."
    
    def check_rate_limit(self):
        current_time = time.time()
        if current_time - self.rate_limit_start >= 3600:  # 1 hour
            self.rate_limit_count = 0
            self.rate_limit_start = current_time
        
        if self.rate_limit_count >= self.app.config['RATE_LIMIT']:
            return False
        
        self.rate_limit_count += 1
        return True
    
    def send_bulk_emails(self, batch_size=50):
        try:
            conn = self.get_db_connection()
            
            # Get unsent students
            students = conn.execute(
                'SELECT * FROM students WHERE sent = FALSE LIMIT ?', 
                (batch_size,)
            ).fetchall()
            
            if not students:
                return {'success': True, 'message': 'No students to send emails to', 'sent': 0, 'failed': 0}
            
            template = self.get_email_template()
            if not template:
                return {'success': False, 'error': 'No email template found'}
            
            batch_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            sent_count = 0
            failed_count = 0
            errors = []
            
            for student_row in students:
                student = dict(student_row)
                
                if not self.check_rate_limit():
                    errors.append("Rate limit exceeded")
                    break
                
                try:
                    subject, content = self.create_personalized_email(student, template)
                    
                    msg = Message(
                        subject=subject,
                        sender=self.app.config['MAIL_DEFAULT_SENDER'],
                        recipients=[student['email']],
                        html=content
                    )
                    
                    self.mail.send(msg)
                    
                    # Update student record
                    conn.execute(
                        'UPDATE students SET sent = TRUE, sent_at = ? WHERE id = ?',
                        (datetime.now(), student['id'])
                    )
                    
                    # Log success
                    conn.execute('''
                        INSERT INTO email_logs (student_email, student_name, status, sent_at, batch_id)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (student['email'], student['name'], 'sent', datetime.now(), batch_id))
                    
                    sent_count += 1
                    
                    # Small delay to avoid overwhelming the email server
                    time.sleep(0.1)
                    
                except Exception as e:
                    failed_count += 1
                    error_msg = f"{student['email']}: {str(e)}"
                    errors.append(error_msg)
                    
                    # Log error
                    conn.execute('''
                        INSERT INTO email_logs (student_email, student_name, status, sent_at, error_message, batch_id)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (student['email'], student['name'], 'failed', datetime.now(), str(e), batch_id))
            
            conn.commit()
            conn.close()
            
            result = {
                'success': True,
                'message': f'Emails sent: {sent_count} successful, {failed_count} failed',
                'sent': sent_count,
                'failed': failed_count,
                'batch_id': batch_id
            }
            
            if errors:
                result['errors'] = errors[:10]  # Return first 10 errors
            
            return result
            
        except Exception as e:
            return {'success': False, 'error': f'Error sending emails: {str(e)}'}