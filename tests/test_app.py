import unittest
from app import app, db
from models import Company, FinancialRatio

class AppTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        with app.app_context():
            db.create_all()
            # Add test data
            company = Company(company_id=1, bankruptcy_status=1, year=2000, industry='Finance')
            ratio = FinancialRatio(company_id=1, ratio_name='ROA(C)', ratio_value=0.5)
            db.session.add(company)
            db.session.add(ratio)
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_list_companies(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Company List', response.data)

    def test_company_detail(self):
        response = self.app.get('/company/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Company 1 Details', response.data)

    def test_company_not_found(self):
        response = self.app.get('/company/999')
        self.assertEqual(response.status_code, 404)

    def test_analysis(self):
        response = self.app.get('/analysis')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Bankruptcy Analysis', response.data)

if __name__ == '__main__':
    unittest.main()