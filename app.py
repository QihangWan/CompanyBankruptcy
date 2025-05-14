from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import os
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/bankruptcy.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Set up logging to file
if not os.path.exists('logs'):
    os.mkdir('logs')
file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('Application startup')

# Custom Exceptions
class DatabaseQueryError(Exception):
    """Raised when a database query fails."""
    pass

class DataValidationError(Exception):
    """Raised when data validation fails."""
    pass

# Import models
from models import Company, FinancialRatio

# Error handling
@app.errorhandler(404)
def page_not_found(e):
    app.logger.error(f"Page not found: {request.url}")
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    app.logger.error(f"Server error: {str(e)}, URL: {request.url}")
    return render_template('500.html'), 500

@app.errorhandler(DatabaseQueryError)
def handle_database_query_error(e):
    app.logger.error(f"Database query error: {str(e)}")
    return render_template('500.html', error_message="Database query failed. Please try again later."), 500

@app.errorhandler(DataValidationError)
def handle_data_validation_error(e):
    app.logger.error(f"Data validation error: {str(e)}")
    return render_template('500.html', error_message=str(e)), 500

# Home route: List companies with filter and sorting
@app.route('/')
def list_companies():
    try:
        bankruptcy_filter = request.args.get('bankruptcy', '')
        sort_by = request.args.get('sort_by', 'company_id')
        sort_order = request.args.get('sort_order', 'asc')

        # Validate parameters
        if sort_by not in ['company_id', 'year']:
            raise DataValidationError("Invalid sort_by parameter.")
        if sort_order not in ['asc', 'desc']:
            raise DataValidationError("Invalid sort_order parameter.")

        query = Company.query
        if bankruptcy_filter == 'yes':
            query = query.filter_by(bankruptcy_status=1)
        elif bankruptcy_filter == 'no':
            query = query.filter_by(bankruptcy_status=0)

        # Apply sorting
        if sort_by == 'year':
            if sort_order == 'desc':
                query = query.order_by(Company.year.desc())
            else:
                query = query.order_by(Company.year)
        else:
            if sort_order == 'desc':
                query = query.order_by(Company.company_id.desc())
            else:
                query = query.order_by(Company.company_id)

        companies = query.paginate(page=request.args.get('page', 1, type=int), per_page=20)
        if not companies.items and request.args.get('page', 1, type=int) > 1:
            raise DatabaseQueryError("No companies found for the requested page.")
        return render_template('list.html', companies=companies, bankruptcy_filter=bankruptcy_filter, sort_by=sort_by, sort_order=sort_order)
    except DatabaseQueryError as e:
        raise e
    except DataValidationError as e:
        raise e
    except Exception as e:
        app.logger.error(f"Error in list_companies: {str(e)}")
        return render_template('500.html'), 500

# Detail route: Show company details
@app.route('/company/<int:company_id>')
def company_detail(company_id):
    try:
        company = Company.query.get_or_404(company_id)
        ratios = FinancialRatio.query.filter_by(company_id=company_id).all()
        if not ratios:
            raise DatabaseQueryError(f"No financial ratios found for company ID {company_id}.")
        return render_template('detail.html', company=company, ratios=ratios)
    except DatabaseQueryError as e:
        raise e
    except Exception as e:
        app.logger.error(f"Error in company_detail: {str(e)}")
        return render_template('500.html'), 500

# Analysis route: Compare bankrupt vs non-bankrupt ratios
@app.route('/analysis')
def analysis():
    try:
        ratios_to_analyze = [
            'ROA(C) before interest and depreciation before interest',
            'ROA(A) before interest and % after tax',
            'ROA(B) before interest and depreciation after tax'
        ]

        analysis_results = {}

        for ratio_name in ratios_to_analyze:
            bankrupt_avg = db.session.query(func.avg(FinancialRatio.ratio_value)).join(Company).filter(
                Company.bankruptcy_status == 1, FinancialRatio.ratio_name == ratio_name
            ).scalar()
            bankrupt_avg = bankrupt_avg if bankrupt_avg is not None else 0.0

            non_bankrupt_avg = db.session.query(func.avg(FinancialRatio.ratio_value)).join(Company).filter(
                Company.bankruptcy_status == 0, FinancialRatio.ratio_name == ratio_name
            ).scalar()
            non_bankrupt_avg = non_bankrupt_avg if non_bankrupt_avg is not None else 0.0

            bankrupt_std = db.session.query(func.stddev(FinancialRatio.ratio_value)).join(Company).filter(
                Company.bankruptcy_status == 1, FinancialRatio.ratio_name == ratio_name
            ).scalar()
            bankrupt_std = bankrupt_std if bankrupt_std is not None else 0.0

            non_bankrupt_std = db.session.query(func.stddev(FinancialRatio.ratio_value)).join(Company).filter(
                Company.bankruptcy_status == 0, FinancialRatio.ratio_name == ratio_name
            ).scalar()
            non_bankrupt_std = non_bankrupt_std if non_bankrupt_std is not None else 0.0

            bankrupt_min = db.session.query(func.min(FinancialRatio.ratio_value)).join(Company).filter(
                Company.bankruptcy_status == 1, FinancialRatio.ratio_name == ratio_name
            ).scalar()
            bankrupt_min = bankrupt_min if bankrupt_min is not None else 0.0

            bankrupt_max = db.session.query(func.max(FinancialRatio.ratio_value)).join(Company).filter(
                Company.bankruptcy_status == 1, FinancialRatio.ratio_name == ratio_name
            ).scalar()
            bankrupt_max = bankrupt_max if bankrupt_max is not None else 0.0

            non_bankrupt_min = db.session.query(func.min(FinancialRatio.ratio_value)).join(Company).filter(
                Company.bankruptcy_status == 0, FinancialRatio.ratio_name == ratio_name
            ).scalar()
            non_bankrupt_min = non_bankrupt_min if non_bankrupt_min is not None else 0.0

            non_bankrupt_max = db.session.query(func.max(FinancialRatio.ratio_value)).join(Company).filter(
                Company.bankruptcy_status == 0, FinancialRatio.ratio_name == ratio_name
            ).scalar()
            non_bankrupt_max = non_bankrupt_max if non_bankrupt_max is not None else 0.0

            analysis_results[ratio_name] = {
                'bankrupt_avg': bankrupt_avg,
                'non_bankrupt_avg': non_bankrupt_avg,
                'bankrupt_std': bankrupt_std,
                'non_bankrupt_std': non_bankrupt_std,
                'bankrupt_min': bankrupt_min,
                'bankrupt_max': bankrupt_max,
                'non_bankrupt_min': non_bankrupt_min,
                'non_bankrupt_max': non_bankrupt_max
            }

        return render_template('analysis.html', analysis_results=analysis_results)
    except Exception as e:
        app.logger.error(f"Error in analysis: {str(e)}")
        return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)