import os
from werkzeug.utils import secure_filename

def allowed_file(filename, allowed_extensions):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def secure_filename_with_timestamp(filename):
    name, ext = os.path.splitext(filename)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{secure_filename(name)}_{timestamp}{ext}"

def generate_report(students_data, report_type='summary'):
    if report_type == 'summary':
        return {
            'total_students': len(students_data),
            'subjects': list(set(student.get('subject', 'General') for student in students_data)),
            'score_range': {
                'min': min(student['score'] for student in students_data),
                'max': max(student['score'] for student in students_data),
                'average': sum(student['score'] for student in students_data) / len(students_data)
            }
        }
    
    return None