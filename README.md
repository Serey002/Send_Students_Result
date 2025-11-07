# Student Result Management System

A Flask-based web application for managing and distributing student results via email. This system allows educational institutions to upload student results in bulk, preview the data, and send personalized result notifications to students via email.

## Features

- **Bulk Upload**: Upload student results using CSV or Excel files
- **Data Preview**: Preview the uploaded data before sending
- **Email Notifications**: Send personalized result notifications to students
- **Email Logging**: Track all email delivery statuses
- **Responsive Design**: Works on both desktop and mobile devices
- **RESTful API**: Includes API endpoints for integration with other systems

## Tech Stack

- **Backend**: Python 3.8+, Flask
- **Database**: SQLite (can be configured to use other databases)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Email**: Flask-Mail (SMTP)
- **Data Processing**: Pandas

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Virtual environment (recommended)

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Serey002/Send_Students_Result.git
   cd Send_Students_Result
   ```

2. **Create and activate a virtual environment**
   ```bash
   # On Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   Create a `.env` file in the project root and add the following variables:
   ```
   SECRET_KEY=secret-key-here
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=serey.phem.12022006@gmail.com
   MAIL_PASSWORD=uqyu sitz mtap aogc
   MAIL_DEFAULT_SENDER=serey.phem.12022006@gmail.com
   ```

## Database Setup

The application uses SQLite by default. To initialize the database:

```bash
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

## Running the Application

1. **Development Server**
   ```bash
   python app.py
   ```
   The application will be available at `http://127.0.0.1:5000/`

2. **Production Server**
   For production, it's recommended to use Gunicorn with a production-ready web server like Nginx.
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

## Usage

1. **Upload Results**
   - Navigate to the upload page
   - Select a CSV or Excel file containing student results
   - The file should include the following columns:
     - student_id
     - first_name
     - last_name
     - email
     - class_name
     - final_english
     - final_english_it
     - final_pl
     - final_algorithm
     - final_web_design
     - final_git
     - total

2. **Preview Data**
   - After uploading, you can preview the data before sending
   - Verify all information is correct

3. **Send Emails**
   - Click the "Send Emails" button to send result notifications
   - The system will show the sending progress

4. **View Logs**
   - Check the email delivery status in the logs section
   - Export logs for record-keeping

## API Endpoints

- `GET /api/stats`: Get system statistics
- `GET /api/results`: Get all results (JSON)
- `GET /api/logs`: Get email logs (JSON)
- `POST /api/upload`: Upload results file (requires authentication)

## File Structure

```
Send_Students_Result/
├── app.py                 # Main application file
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables
├── database/             # Database files
├── static/               # Static files (CSS, JS, images)
│   └── css/
│       └── style.css
├── templates/            # HTML templates
└── uploads/              # Directory for uploaded files
```

## Contributing

1. Fork the repository
2. Create a new branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Flask](https://flask.palletsprojects.com/)
- [Bootstrap](https://getbootstrap.com/)
- [Pandas](https://pandas.pydata.org/)

## Support

For support, please open an issue on the [GitHub repository](https://github.com/Serey002/Send_Students_Result/issues).