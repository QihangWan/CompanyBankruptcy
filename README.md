Company Bankruptcy Analysis
Overview
This is a Flask-based web application developed for CS551P Advanced Programming Assessment 3 (2024-25). The application analyzes company bankruptcy data using an open dataset from Kaggle (company_bankruptcy_prediction, 6,819 records, 96 features), sourced from the Taiwan Economic Journal (1999-2009). It provides a database-driven platform to display company details, filter and sort companies by bankruptcy status and other criteria, and perform in-depth financial analysis by comparing bankrupt and non-bankrupt companies across multiple ratios. The application uses SQLite as the database, is styled with Bootstrap CSS, and is prepared for deployment on Render.
After data cleaning (removing outliers beyond 3 standard deviations and filling missing values with medians), the dataset contains approximately 2,600 records, which still meets the assessment requirement of 2,000-7,000 records.
Requirements

Python 3.8.0
Flask==2.0.1, Flask-SQLAlchemy==2.5.1, pandas==1.3.3, gunicorn==20.1.0, werkzeug>=2.0,<3.0, SQLAlchemy>=1.2.0,<2.0 (see requirements.txt)

Installation

Clone the repository:git clone <repository_url>
cd company_bankruptcy_app


Create and activate a virtual environment:python3.8 -m venv venv
source venv/bin/activate


Install dependencies:pip install -r requirements.txt


Load the data into SQLite:python load_data.py


This will create data/bankruptcy.db with approximately 2,600 company records and their financial ratios after cleaning (outlier removal and median imputation).



Usage

Run the application:export FLASK_APP=app.py
export FLASK_ENV=development
flask run --host=0.0.0.0


Access the app at http://localhost:5000 (or the Codio preview URL).


Features:
Home Page (/): View a paginated list of companies (20 per page), with filters for bankruptcy status ("Yes" or "No") and sorting options ("Sort By: Company ID or Year", "Ascending or Descending").
Detail Page (/company/<id>): View financial ratios for a specific company (e.g., /company/1). Ratios with values less than 0 or greater than 1 are highlighted in red to indicate potential anomalies.
Analysis Page (/analysis): Compare bankrupt vs. non-bankrupt companies across multiple financial ratios (ROA(C), ROA(A), ROA(B)), including average, standard deviation, minimum, and maximum values, with insights into financial performance differences.


Deployed App:
Access the deployed app at: <render_url> (to be updated after deployment).



Testing
Run unit tests to verify functionality:
python -m unittest tests/test_app.py


Tests cover the home page, detail page, analysis page, and 404 error handling. Note that the test data uses a memory database, so it may not reflect the exact cleaned dataset (~2,600 records).

Maintenance

Update Data: Replace data/data.csv with a new dataset and re-run python load_data.py. The script will clean the data by filling missing values with medians and removing outliers (beyond 3 standard deviations), which may reduce the record count.
Database: The SQLite database (data/bankruptcy.db) is automatically created by load_data.py. To reset, delete the file and re-run the script.
Render Deployment: Monitor Render logs for issues. Update requirements.txt if dependencies change.
Enhancements:
Add more financial ratios to the analysis page (e.g., Net Profit Margin).
Adjust the outlier removal threshold in load_data.py (e.g., change 3 standard deviations to 4) to retain more data if needed.



Deployment

Local Deployment:
Follow the installation steps above and run flask run.


Render Deployment:
Deployed on Render with SQLite.
Ensure data/bankruptcy.db is generated during deployment (handled by load_data.py in the build command).
Build Command: pip install -r requirements.txt && python load_data.py
Start Command: gunicorn app:app
Python Version: 3.8.0 (specified in runtime.txt).



Notes

Error Handling: The app handles 404 and 500 errors with custom pages. Custom exceptions (DatabaseQueryError, DataValidationError) are implemented for specific error scenarios, with logs recorded in logs/app.log.
Git Log: See git-log.txt for version control history, including commits for setup, data loading, testing, styling, and deployment preparation.
Known Issues:
If the analysis page shows 0.0 for averages, verify the dataset (data.csv) contains the correct column names and data for the analyzed ratios (ROA(C), ROA(A), ROA(B)).



Development History

Initial setup with Flask, SQLite database, and basic templates.
Added data loading script (load_data.py) for 6,819 records, later enhanced with data cleaning (resulting in ~2,600 records).
Implemented templates for list, detail, and analysis pages, with Bootstrap styling and a background image (static/background.jpg).
Fixed dependency issues (werkzeug, SQLAlchemy) for Python 3.8.0 compatibility.
Added error handling for the analysis page to manage missing data.
Enhanced the list page with sorting functionality (by Company ID or Year, ascending/descending).
Added conditional rendering in the detail page to highlight anomalous ratio values.
Expanded the analysis page to include multi-dimensional analysis of ROA(C), ROA(A), and ROA(B), with statistical metrics (average, standard deviation, min, max).
Separated routes into a Flask Blueprint (routes.py) and added a custom decorator to log request times.

Development Challenges and Solutions

Challenge: Initial dependency conflicts with werkzeug and SQLAlchemy caused import errors.
Solution: Locked versions in requirements.txt (werkzeug>=2.0,<3.0, SQLAlchemy>=1.2.0,<2.0).


Challenge: Data cleaning reduced the dataset from 6,819 to ~2,600 records due to outlier removal.
Solution: Ensured the cleaned dataset still meets the 2,000-7,000 record requirement; the threshold (3 standard deviations) can be adjusted if more data retention is needed.


Challenge: Analysis page crashed when query results were None.
Solution: Added None checks in app.py to set default values, preventing round errors in the template.



