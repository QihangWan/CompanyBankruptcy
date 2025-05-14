from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Company(db.Model):
    __tablename__ = 'companies'
    company_id = db.Column(db.Integer, primary_key=True)
    bankruptcy_status = db.Column(db.Integer, nullable=False)  # 0: non-bankrupt, 1: bankrupt
    year = db.Column(db.Integer)  # Inferred or assumed
    industry = db.Column(db.String(50))  # Placeholder, can be enhanced
    ratios = db.relationship('FinancialRatio', backref='company', lazy=True)

class FinancialRatio(db.Model):
    __tablename__ = 'financial_ratios'
    ratio_id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.company_id'), nullable=False)
    ratio_name = db.Column(db.String(100), nullable=False)
    ratio_value = db.Column(db.Float, nullable=False)