employees = {
    "sonal": {
        "password": "finance123",
        "role": "Financial Analyst",
        "access_level": [1, 3, 4],
        "location": "Mumbai",
        "working_hours": "09:00 - 18:00",
        "files": [
            {"name": "Financial Report 2024.pdf", "url": "/files/financial_report_2024.pdf"},
            {"name": "Investment Analysis.docx", "url": "/files/investment_analysis.docx"}
        ]
    },
    "pranjal": {
        "password": "account123",
        "role": "Accountant",
        "access_level": [1, 3],
        "location": "Bangalore",
        "working_hours": "10:00 - 19:00",
        "files": [
            {"name": "Tax Documents.pdf", "url": "/files/tax_documents.pdf"},
            {"name": "Company Ledger.xlsx", "url": "/files/company_ledger.xlsx"}
        ]
    },
    "moon": {
        "password": "senior123",
        "role": "Senior Management",
        "access_level": [1, 2, 3, 4],
        "location": "Delhi",
        "working_hours": "08:00 - 17:00",
        "files": [
            {"name": "Strategic Business Plan.docx", "url": "/files/strategic_plan.docx"},
            {"name": "Employee Payroll Records.xlsx", "url": "/files/payroll_records.xlsx"}
        ]
    },
    "vanshita": {
        "password": "ceo123",
        "role": "CEO",
        "access_level": [1, 2, 3, 4, 5],
        "location": "Delhi",
        "working_hours": "Anytime",
        "files": [
            {"name": "Board Meeting Documents.pdf", "url": "/files/board_meeting.pdf"},
            {"name": "Critical Business Continuity Plans.pdf", "url": "/files/business_continuity.pdf"}
        ]
    },
    "mansi": {
        "password": "loan123",
        "role": "Loan Officer",
        "access_level": [1, 2, 3],
        "location": "Pune",
        "working_hours": "09:00 - 18:00",
        "files": [
            {"name": "Loan Applications.docx", "url": "/files/loan_applications.docx"},
            {"name": "Customer Account Details.xlsx", "url": "/files/customer_accounts.xlsx"}
        ]
    },
    "simba": {
        "password": "customer123",
        "role": "Customer Service",
        "access_level": [1, 2],
        "location": "Chennai",
        "working_hours": "09:00 - 17:00",
        "files": [
            {"name": "Customer Queries.csv", "url": "/files/customer_queries.csv"},
            {"name": "General Customer FAQs.pdf", "url": "/files/faqs.pdf"}
        ]
    }
}

# File access mapping (For reference)
file_access = {
    1: ["Company Policies", "Public Reports"],
    2: ["Customer Account Details", "Loan Applications"],
    3: ["Financial Statements", "General Ledger"],
    4: ["Employee Records", "Strategic Plans"],
    5: ["Board Meeting Documents", "Critical Business Continuity Plans"]
}
