# Credit_Scoring_Loan_Application_SystemTask: 
Credit Scoring and Loan Application System
Objective:
Create a system to calculate a "credit score" for loan applicants based on predefined criteria and process loan applications based on that score. This will involve FastAPI for backend processing, MongoDB for data storage, and HTML/CSS for a minimal user interface.
Requirements:
Backend (FastAPI):
Endpoints:
POST /register: Register new users with basic information (name, email, phone).
POST /login: User login for authentication, using JWT for secure session management.
POST /apply-loan: Accept loan applications with details like loan amount, tenure, and purpose.
GET /loan-status/{loan_id}: Check the status of an application.
GET /credit-score: Calculate a credit score for the user based on predefined criteria.
GET /admin/all-loans: Admin-only endpoint to review all loan applications.
POST /admin/review-loan/{loan_id}: Admin endpoint to approve/reject applications based on the credit score and other factors.
Credit Score Calculation Logic:
Factors to consider in the credit score calculation: income, existing loans, repayment history (you can simulate some of these for the test).
Implement a score threshold; if the applicant’s score meets the threshold, they are eligible for review by an admin, else they are automatically marked as Rejected.
Keep the score calculation logic modular so it can be expanded upon in the future.
Database (MongoDB):
Users: Store user information with fields for user role (user/admin).
Applications: Track each loan application, including fields for status (Pending, Approved, Rejected), credit score, and applicant details.
Logs: Keep an activity log for audit purposes, recording changes in loan application status, actions taken by admin, etc.
Frontend (HTML/CSS):
Pages:
Register/Login Page: Allow users to register and log in.
Loan Application Form: Form to apply for a loan, which displays calculated credit score dynamically.
Status Check Page: Displays loan application status to the applicant.
Admin Dashboard: Allows admins to view all applications, filter by status, and review credit scores.
Performance Optimization:
Cache the credit score calculation for each user to avoid recalculating it with every request.
Use indexes in MongoDB on frequently queried fields (e.g., user ID, loan status).
Security and Compliance:
Ensure sensitive data, like credit scores and personal details, are handled securely.
Use JWT tokens with proper expiration and role-based access for endpoint protection.
Implement input validation to prevent SQL injection or NoSQL injection attacks.
Documentation:
Document API endpoints with sample requests, responses, and expected HTTP status codes.
Add any instructions for setup, database initialization, and sample data for testing.
Demo:
Prepare a 10-15 minute demo showcasing the system’s functionality:
Registering a user and logging in.
Applying for a loan, with the credit score calculation visible to the applicant.
Viewing loan status and admin’s ability to review and update application statuses.
Walkthrough of API documentation for endpoints and credit score logic.
Expected Deliverables:
GitHub link with the code and setup instructions.
Documentation covering API usage and assumptions made in the credit score logic.
A brief performance analysis detailing how caching and MongoDB indexing were implemented.
