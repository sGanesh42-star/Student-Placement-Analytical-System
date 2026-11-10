# Student Placement Analytical System

A Flask web application with signup/login, student dashboard, placement prediction, profile editing, and admin analytics.

## Setup (Windows / VS Code)

1. Install Python 3.10+.
2. Extract this folder and open it in VS Code.
3. Open Terminal in VS Code:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   python app.py
   ```
4. Open `http://127.0.0.1:5000`.

## Demo admin
- Email: `admin@placement.com`
- Password: `Admin123!`

## Notes
- The database (`placement.db`) is created automatically.
- The ML model uses generated demonstration data. Predictions are not real placement guarantees.
- Change `app.secret_key` before deployment and use a production WSGI server. Do not deploy Flask debug mode.
