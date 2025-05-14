from flask import Blueprint, render_template, request
from sqlalchemy import func
from models import Company, FinancialRatio
from app import db, app
import time
from functools import wraps

# Blueprint
main_bp = Blueprint('main', __name__)

# Custom decorator to log request time
def log_request_time(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        result = f(*args, **kwargs)
        end_time = time.time()
        app.logger.info(f"Request to {f.__name__} took {end_time - start_time:.2f} seconds")
        return result
    return decorated_function

# Home route: List companies with filter and sorting
@main_bp.route('/')
@log_request_time
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
@main_bp.route('/company/<int:company_id>')
@log_request_time
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
@main_bp.route('/analysis')
@log_request_time
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