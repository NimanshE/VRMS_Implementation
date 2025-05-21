# Video Rental Store Management System (VRSMS)

## Overview
The Video Rental Store Management System (VRSMS) is a comprehensive web application designed to automate and streamline the daily operations of a video and music CD rental store. The system manages customer memberships, inventory control, rental processing, loss/damage handling, automatic charge updates, financial reporting, and notifications.

## Features
- **Membership Management**: 
  - Registration with Rs. 1000 deposit
  - Cancellation with deposit return (if no dues exist)
  - Membership verification
  
- **Inventory Control**:
  - Track video CDs, DVDs (VHS/MP4 formats), and music CDs
  - Record procurement date, price, and rental charges
  - Automatic reduction of rental charges after one year
  - Disposal of unissued items at 10% of purchase price
  
- **Rental Operations**:
  - Loan of at most one video and one music CD per transaction
  - Return tracking and charge calculation
  - Lost or damaged item handling
  
- **Financial Management**:
  - Real-time profit/loss reporting
  - Receipt generation
  - Late fee processing
  
- **User Roles**:
  - Customer: Browse, rent, return, manage membership
  - Clerk: Process rentals/returns, handle lost/damaged items
  - Admin: Manage inventory, users, generate reports

## Technology Stack
- **Backend**: Python with Flask framework
- **Database**: SQLite (rental.db)
- **Frontend**: HTML, CSS, JavaScript
- **Notifications**: Email integration

## Installation and Setup

### Prerequisites
- Python 3.x
- pip package manager

### Steps to Run
1. Clone the repository:
   ```
   git clone https://github.com/NimanshE/VRMS_Implementation.git
   cd VRMS_Implementation
   ```

2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up the database:
   ```
   python populate_db.py
   ```

4. Run the application:
   ```
   python app.py
   ```

5. Access the application:
   ```
   http://127.0.0.1:5000
   ```

## Code Structure
- `app.py` - Main Flask server
- `models.py` - Database schema definitions
- `populate_db.py` - Database initialization script
- `templates/` - HTML pages
- `static/` - CSS and JavaScript files

## Database Schema
The application uses SQLite with the following main tables:
- Users (Admin, Clerk, Customer)
- Items (Video, Music)
- Rentals
- Transactions
- Deposits

## User Workflows

### Customer Workflow
1. Register/Login
2. Browse available items
3. Add items to cart
4. Request rental
5. Return items or report loss/damage
6. Cancel membership if desired

### Clerk Workflow
1. Login
2. Process rental requests
3. Handle returns
4. Process loss/damage claims
5. Update inventory status

### Admin Workflow
1. Login
2. Manage inventory (add/remove items)
3. Manage users (add/remove)
4. Generate financial reports
5. View system statistics

## Future Enhancements
- Mobile application integration
- Cloud storage for data backup
- Predictive analytics for inventory management
- Barcode/QR code scanning for faster processing
- Recommendation system based on user preferences

## Contributors
- Nimansh Endlay
- Preyanshe Jindal
- Hitansh Kapoor
- Dev Tripathi
- Gautam Lochab


## Acknowledgements
- Flask Documentation: https://flask.palletsprojects.com/
- SQLite Documentation: https://www.sqlite.org/docs.html
- Fundamentals of Software Engineering, Fourth Edition, By Rajib Mall
