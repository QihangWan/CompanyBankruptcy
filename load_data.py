import pandas as pd
from models import db, Company, FinancialRatio
import os

def load_data():
    try:
        # Read CSV
        df = pd.read_csv('data/data.csv')
        
        # Data Validation: Check if required columns exist
        required_columns = ['Bankrupt?'] + [col for col in df.columns if col != 'Bankrupt?']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

        # Data Cleaning: Handle missing values and outliers
        # Fill NaN with median for numerical columns
        for col in df.columns:
            if df[col].dtype in ['float64', 'int64']:
                df[col].fillna(df[col].median(), inplace=True)
        
        # Remove outliers (values beyond 3 standard deviations)
        for col in df.columns:
            if col != 'Bankrupt?' and df[col].dtype in ['float64', 'int64']:
                mean = df[col].mean()
                std = df[col].std()
                df = df[(df[col] >= mean - 3 * std) & (df[col] <= mean + 3 * std)]

        print(f"Loaded {len(df)} records after cleaning")

        # Create database tables
        db.drop_all()  # Drop existing tables to avoid duplicates
        db.create_all()

        # Load companies
        for index, row in df.iterrows():
            company = Company(
                company_id=index + 1,
                bankruptcy_status=row['Bankrupt?'],
                year=1999 + (index % 11),  # Infer year (1999-2009)
                industry='Finance'  # Placeholder
            )
            db.session.add(company)

        db.session.commit()

        # Load financial ratios
        ratio_columns = [col for col in df.columns if col != 'Bankrupt?']
        for index, row in df.iterrows():
            for col in ratio_columns:
                ratio = FinancialRatio(
                    company_id=index + 1,
                    ratio_name=col,
                    ratio_value=row[col]
                )
                db.session.add(ratio)

        db.session.commit()
        print("Data loaded successfully")
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        db.session.rollback()

if __name__ == '__main__':
    from app import app
    with app.app_context():
        load_data()