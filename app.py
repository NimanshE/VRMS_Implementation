from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from flask_mail import Mail, Message
from datetime import timedelta
from sqlalchemy import func


app = Flask(__name__)
app.config['SECRET_KEY'] = 'videorental123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rental.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'vrms.group8@gmail.com'
app.config['MAIL_PASSWORD'] = 'loek ndyw ilrn ecxy'
app.config['MAIL_DEFAULT_SENDER'] = 'vrms.group8@gmail.com'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
mail = Mail(app)


# Models
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin', 'clerk', 'customer'
    address = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    deposit = db.Column(db.Float, default=0.0)
    membership_active = db.Column(db.Boolean, default=False)
    date_joined = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    # Specify foreign_keys for rentals relationship
    rentals = db.relationship('Rental', backref='user', lazy=True, foreign_keys='Rental.user_id')

class Rental(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    rental_date = db.Column(db.DateTime, default=datetime.utcnow)
    return_date = db.Column(db.DateTime)
    due_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'approved', 'returned', 'lost', 'damaged'
    approved_by = db.Column(db.Integer, db.ForeignKey('user.id'))  # Clerk/Admin who approved
    total_charge = db.Column(db.Float)
    lost_or_damaged = db.Column(db.Boolean, default=False)  # New field

    # Specify foreign_keys for approved_by relationship
    approved_by_user = db.relationship('User', foreign_keys=[approved_by])

    # For early return request and status
    early_return_requested = db.Column(db.Boolean, default=False)  # New field
    early_return_status = db.Column(db.String(20), default=None)  # 'pending', 'approved', 'denied'

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'video_cd', 'music_cd', 'dvd', 'vhs'
    format = db.Column(db.String(20))  # 'VHS', 'MP4', etc.
    genre = db.Column(db.String(50))
    daily_rate = db.Column(db.Float, nullable=False)
    purchase_price = db.Column(db.Float, nullable=False) # Assuming this is the price to buy the item
    available = db.Column(db.Boolean, default=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    rentals = db.relationship('Rental', backref='item', lazy=True)
    last_issued_date = db.Column(db.DateTime, nullable=True)
    sold_date = db.Column(db.DateTime, nullable=True)


class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    days = db.Column(db.Integer, default=7)  # Default rental period is 7 days
    user = db.relationship('User', backref='cart_items')
    item = db.relationship('Item', backref='cart_entries')
    daily_rate = db.Column(db.Float, nullable=False)
    total_cost = db.Column(db.Float, nullable=False)
# User loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Routes
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!', 'success')

            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user.role == 'clerk':
                return redirect(url_for('clerk_dashboard'))
            else:
                return redirect(url_for('customer_dashboard'))
        else:
            flash('Login unsuccessful. Check email and password', 'danger')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        address = request.form.get('address')
        phone = request.form.get('phone')

        user_exists = User.query.filter_by(email=email).first()
        if user_exists:
            flash('Email already registered', 'danger')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        new_user = User(
            name=name,
            email=email,
            password=hashed_password,
            role='customer',
            address=address,
            phone=phone
        )

        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! You can now login and make a deposit to activate your membership.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

"""
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Access denied: You do not have admin privileges', 'danger')
        return redirect(url_for('home'))

    users = User.query.all()
    items = Item.query.all()
    rentals = Rental.query.all()

    return render_template('admin_dashboard.html', users=users, items=items, rentals=rentals)
"""

@app.route('/cart', methods=['GET', 'POST'])
@login_required
def view_cart():
    if current_user.role != 'customer':
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))

    from datetime import datetime, timedelta

    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    total_cost = 0

    # Calculate total cost with discounts applied
    for cart_item in cart_items:
        item = cart_item.item
        if item.date_added and (item.date_added + timedelta(days=365)) < datetime.now():
            daily_rate = item.daily_rate / 2  # Apply 50% discount
        else:
            daily_rate = item.daily_rate
        total_cost += daily_rate * cart_item.days

    if request.method == 'POST':
        # Check if total cost exceeds deposit
        if total_cost > current_user.deposit:
            flash('You cannot checkout items worth more than your deposit.', 'danger')
            return redirect(url_for('view_cart'))

        # Check if user already has 5 active rentals
        active_rentals = Rental.query.filter_by(user_id=current_user.id, status='approved').count()
        if active_rentals + len(cart_items) > 5:
            flash('You cannot rent more than 5 items at a time.', 'danger')
            return redirect(url_for('view_cart'))

        # Process checkout
        for cart_item in cart_items:
            item = cart_item.item
            if item.date_added and (item.date_added + timedelta(days=365)) < datetime.now():
                daily_rate = item.daily_rate / 2  # Apply 50% discount
            else:
                daily_rate = item.daily_rate

            total_charge = daily_rate * cart_item.days  # Calculate total charge
            rental = Rental(
                user_id=current_user.id,
                item_id=cart_item.item_id,
                due_date=datetime.utcnow() + timedelta(days=cart_item.days),
                total_charge=total_charge,
                status='pending'
            )
            cart_item.item.available = False  # Mark item as unavailable
            db.session.add(rental)
            db.session.delete(cart_item)  # Remove item from cart

        db.session.commit()
        flash('Rental request submitted successfully.', 'success')
        return redirect(url_for('customer_dashboard'))

    return render_template('cart.html', cart_items=cart_items, total_cost=total_cost,timedelta=timedelta,now=datetime.now())


@app.route('/cart/edit/<int:cart_id>', methods=['POST'])
@login_required
def edit_cart(cart_id):
    cart_item = Cart.query.get_or_404(cart_id)

    if cart_item.user_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('view_cart'))

    from datetime import datetime, timedelta

    new_days = int(request.form.get('days', 7))
    item = cart_item.item
    if item.date_added and (item.date_added + timedelta(days=365)) < datetime.now():
        daily_rate = item.daily_rate / 2  # Apply 50% discount
    else:
        daily_rate = item.daily_rate

    cart_item.days = new_days
    cart_item.daily_rate = daily_rate
    cart_item.total_cost = daily_rate * new_days  # Update total cost
    db.session.commit()
    flash('Rental period updated.', 'success')

    return redirect(url_for('view_cart'))


"""@app.route('/cart/add/<int:item_id>', methods=['POST'])
@login_required
def add_to_cart(item_id):
    days = int(request.form.get('days', 7))  # Default to 7 days if not specified
    existing_cart_item = Cart.query.filter_by(user_id=current_user.id, item_id=item_id).first()

    if existing_cart_item:
        flash('Item is already in your cart.', 'info')
    else:
        cart_item = Cart(user_id=current_user.id, item_id=item_id, days=days)
        db.session.add(cart_item)
        db.session.commit()
        flash('Item added to cart.', 'success')

    return redirect(url_for('browse_items'))"""

@app.route('/cart/add/<int:item_id>', methods=['POST'])
@login_required
def add_to_cart(item_id):
    from datetime import datetime, timedelta

    days = int(request.form.get('days', 7))  # Default to 7 days if not specified
    item = Item.query.get_or_404(item_id)  # Fetch the item from the database

    # Check if the item is already in the cart
    existing_cart_item = Cart.query.filter_by(user_id=current_user.id, item_id=item_id).first()

    if existing_cart_item:
        flash('Item is already in your cart.', 'info')
    else:
        # Determine if the item is eligible for a discount
        if item.date_added and (item.date_added + timedelta(days=365)) < datetime.now():
            daily_rate = item.daily_rate / 2  # Apply 50% discount
        else:
            daily_rate = item.daily_rate

        # Calculate the total cost for the rental period
        total_cost = daily_rate * days

        # Add the item to the cart
        cart_item = Cart(user_id=current_user.id, item_id=item_id, days=days, daily_rate=daily_rate, total_cost=total_cost)
        db.session.add(cart_item)
        db.session.commit()
        flash(f'Item added to cart for Rs. {total_cost:.2f}', 'success')

    return redirect(url_for('browse_items'))

"""@app.route('/cart/edit/<int:cart_id>', methods=['POST'])
@login_required
def edit_cart(cart_id):
    cart_item = Cart.query.get_or_404(cart_id)

    if cart_item.user_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('view_cart'))

    new_days = int(request.form.get('days', 7))
    cart_item.days = new_days
    db.session.commit()
    flash('Rental period updated.', 'success')

    return redirect(url_for('view_cart'))"""

@app.route('/cart/remove/<int:cart_id>', methods=['POST'])
@login_required
def remove_from_cart(cart_id):
    cart_item = Cart.query.get_or_404(cart_id)
    if cart_item.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('view_cart'))

    db.session.delete(cart_item)
    db.session.commit()
    flash('Item removed from cart.', 'success')
    return redirect(url_for('view_cart'))


@app.route('/request_early_return/<int:rental_id>', methods=['POST'])
@login_required
def request_early_return(rental_id):
    rental = Rental.query.get_or_404(rental_id)

    if rental.user_id != current_user.id or rental.status != 'approved':
        flash('Invalid request.', 'danger')
        return redirect(url_for('customer_dashboard'))

    rental.early_return_requested = True
    rental.early_return_status = 'pending'
    db.session.commit()

    flash('Early return request submitted successfully.', 'success')
    return redirect(url_for('customer_dashboard'))

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Access denied: You do not have admin privileges', 'danger')
        return redirect(url_for('home'))

    users = User.query.all()
    items = Item.query.all()
    rentals = Rental.query.all()

    # Fetch user and item details for rentals
    rental_details = []
    for rental in rentals:
        user = User.query.get(rental.user_id)
        item = Item.query.get(rental.item_id)
        rental_details.append({
            'id': rental.id,
            'user_name': user.name if user else 'Unknown',
            'item_title': item.title if item else 'Unknown',
            'rental_date': rental.rental_date,
            'due_date': rental.due_date,
            'return_date': rental.return_date,
            'status': rental.status,
            'total_charge': rental.total_charge
        })

    # Query all sold items
    sold_items = Item.query.filter_by(available=False).all()

    return render_template('admin_dashboard.html', users=users, items=items, rentals=rental_details,sold_items=sold_items,timedelta=timedelta,now=datetime.utcnow())

"""@app.route('/clerk/dashboard')
@login_required
def clerk_dashboard():
    if current_user.role != 'clerk':
        flash('Access denied: You are not a store clerk', 'danger')
        return redirect(url_for('home'))

    pending_rentals = Rental.query.filter_by(status='pending').all()
    active_rentals = Rental.query.filter_by(status='approved').all()

    return render_template('clerk_dashboard.html', pending_rentals=pending_rentals, active_rentals=active_rentals)
"""

"""@app.route('/sell_item/<int:item_id>', methods=['POST'])
@login_required
def sell_item(item_id):
    if current_user.role != 'admin':
        flash("Unauthorized access", "danger")
        return redirect(url_for('admin_dashboard'))

    item = Item.query.get_or_404(item_id)
    if item.last_issued_date and (item.last_issued_date + timedelta(days=365)) < datetime.utcnow():
        db.session.delete(item)
        db.session.commit()
        flash(f"Item '{item.title}' sold and removed from inventory.", "success")
    else:
        flash("Item is not eligible for sale.", "warning")

    return redirect(url_for('admin_dashboard'))"""

@app.route('/sell_item/<int:item_id>', methods=['POST'])
@login_required
def sell_item(item_id):
    if current_user.role != 'admin':
        return redirect(url_for('home'))

    item = Item.query.get_or_404(item_id)
    if item.available:
        item.available = False
        item.sold_date = datetime.utcnow()
        db.session.commit()
        flash(f'Item "{item.title}" has been sold.', 'success')
    else:
        flash(f'Item "{item.title}" is already sold.', 'warning')

    return redirect(url_for('admin_dashboard'))

@app.route('/clerk/dashboard')
@login_required
def clerk_dashboard():
    if current_user.role != 'clerk':
        flash('Access denied: You are not a store clerk', 'danger')
        return redirect(url_for('home'))

    pending_rentals = Rental.query.filter_by(status='pending').all()
    active_rentals = Rental.query.filter_by(status='approved').all()

    # Fetch user and item details for pending rentals
    pending_rental_details = []
    for rental in pending_rentals:
        user = User.query.get(rental.user_id)
        item = Item.query.get(rental.item_id)
        pending_rental_details.append({
            'id': rental.id,
            'user_name': user.name if user else 'Unknown',
            'item_title': item.title if item else 'Unknown',
            'rental_date': rental.rental_date,
            'due_date': rental.due_date,
            'total_charge': rental.total_charge
        })

    # Fetch user and item details for active rentals
    active_rental_details = []
    for rental in active_rentals:
        user = User.query.get(rental.user_id)
        item = Item.query.get(rental.item_id)
        active_rental_details.append({
            'id': rental.id,
            'user_name': user.name if user else 'Unknown',
            'item_title': item.title if item else 'Unknown',
            'rental_date': rental.rental_date,
            'due_date': rental.due_date
        })

    # Fetch early return requests
    early_returns = Rental.query.filter_by(early_return_requested=True).all()

    return render_template(
        'clerk_dashboard.html',
        pending_rentals=pending_rentals,
        active_rentals=active_rentals,
        early_returns=early_returns
    )

    return render_template('clerk_dashboard.html', pending_rentals=pending_rental_details, active_rentals=active_rental_details)


"""@app.route('/customer/dashboard')
@login_required
def customer_dashboard():
    if current_user.role != 'customer':
        flash('Access denied', 'danger')
        return redirect(url_for('home'))

    user_rentals = Rental.query.filter_by(user_id=current_user.id).all()

    return render_template('customer_dashboard.html', user_rentals=user_rentals)
"""


@app.route('/customer/dashboard')
@login_required
def customer_dashboard():
    if current_user.role != 'customer':
        flash('Access denied', 'danger')
        return redirect(url_for('home'))

    # Fetch the latest user data
    user = User.query.get(current_user.id)
    user_rentals = Rental.query.filter_by(user_id=current_user.id).all()

    return render_template('customer_dashboard.html', user=user, user_rentals=user_rentals)

@app.route('/make_deposit', methods=['GET', 'POST'])
@login_required
def make_deposit():
    if current_user.role != 'customer':
        flash('Only customers can make deposits', 'danger')
        return redirect(url_for('home'))

    if request.method == 'POST':
        deposit_amount = float(request.form.get('amount'))

        if deposit_amount < 1000 and not current_user.membership_active:
            flash('Initial deposit must be at least Rs. 1000', 'danger')
            return redirect(url_for('make_deposit'))

        current_user.deposit += deposit_amount

        if deposit_amount >= 1000 and not current_user.membership_active:
            current_user.membership_active = True
            flash('Membership activated successfully!', 'success')
        else:
            flash('Deposit successful!', 'success')

        db.session.commit()
        return redirect(url_for('customer_dashboard'))

    return render_template('make_deposit.html')

@app.route('/report_lost_damaged/<int:rental_id>', methods=['POST'])
@login_required
def report_lost_damaged(rental_id):
    if current_user.role != 'clerk':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('clerk_dashboard'))

    # Fetch rental, item, and user details
    rental = Rental.query.get_or_404(rental_id)
    item = Item.query.get_or_404(rental.item_id)
    user = User.query.get_or_404(rental.user_id)

    # Check if the rental is already marked as lost or damaged
    if rental.lost_or_damaged:
        flash('This rental has already been reported as lost or damaged.', 'warning')
        return redirect(url_for('clerk_dashboard'))

    # Mark the rental as lost or damaged
    rental.lost_or_damaged = True
    rental.status = 'lost/damaged'

    # Make the item unavailable
    item.available = False

    # Charge the user the full purchase price
    purchase_price = item.daily_rate * 30  # Assuming 30 days as the purchase price multiplier
    if user.deposit >= purchase_price:
        user.deposit -= purchase_price
        flash(f'The user has been charged Rs. {purchase_price} for the lost/damaged item.', 'success')
    else:
        flash('The user does not have enough deposit to cover the cost of the lost/damaged item.', 'danger')

    # Commit changes to the database
    db.session.commit()

    flash('The rental has been marked as lost or damaged, and the item is now unavailable.', 'success')
    return redirect(url_for('clerk_dashboard'))

"""@app.route('/cancel_membership', methods=['GET', 'POST'])
@login_required
def cancel_membership():
    if current_user.role != 'customer':
        flash('Only customers can cancel membership', 'danger')
        return redirect(url_for('home'))

    active_rentals = Rental.query.filter_by(user_id=current_user.id, status='approved').all()

    if active_rentals:
        flash('You have outstanding rentals. Please return all items before cancelling membership.', 'danger')
        return redirect(url_for('customer_dashboard'))

    if request.method == 'POST':
        current_user.membership_active = False
        flash(f'Membership cancelled. Rs. {current_user.deposit} will be refunded.', 'info')
        current_user.deposit = 0
        db.session.commit()
        return redirect(url_for('customer_dashboard'))

    # Pass the current_user object to the template
    return render_template('cancel_membership.html', user=current_user)
"""

@app.route('/cancel_membership', methods=['GET', 'POST'])
@login_required
def cancel_membership():
    if current_user.role != 'customer':
        flash('Only customers can cancel membership', 'danger')
        return redirect(url_for('home'))

    active_rentals = Rental.query.filter_by(user_id=current_user.id, status='approved').all()

    if active_rentals:
        flash('You have outstanding rentals. Please return all items before cancelling membership.', 'danger')
        return redirect(url_for('customer_dashboard'))

    if request.method == 'POST':
        refund_amount = current_user.deposit
        current_user.membership_active = False
        current_user.deposit = 0
        db.session.commit()

        # Send cancellation email
        try:
            msg = Message(
                subject="Membership Cancellation Confirmation",
                recipients=[current_user.email],
                body=f"Dear {current_user.name},\n\nYour membership has been successfully cancelled. "
                     f"A refund of Rs. {refund_amount:.2f} has been processed.\n\nThank you."
            )
            mail.send(msg)
            flash('Membership cancelled and confirmation email sent.', 'info')
        except Exception as e:
            flash('Membership cancelled, but failed to send confirmation email.', 'warning')

        return redirect(url_for('customer_dashboard'))

    return render_template('cancel_membership.html', user=current_user)

@app.route('/browse', methods=['GET'])
def browse_items():
    query = request.args.get('query', '').strip()
    item_type = request.args.get('type', '').strip()

    # Base query to fetch items that are not sold
    items_query = Item.query.filter((Item.sold_date == None))

    # Apply search filter if a query is provided
    if query:
        items_query = items_query.filter(Item.title.ilike(f'%{query}%'))

    # Apply type filter if a type is provided
    if item_type:
        items_query = items_query.filter_by(type=item_type)

    # Fetch the filtered items
    items = items_query.all()
    # Render different templates based on user role
    if current_user.role in ['admin', 'clerk']:
        return render_template('browse_admin_clerk.html', items=items, query=query, item_type=item_type,timedelta=timedelta,now=datetime.now())
    else:
        return render_template('browse.html', items=items, query=query, item_type=item_type,timedelta=timedelta,now=datetime.now())


@app.route('/rent/<int:item_id>', methods=['GET', 'POST'])
@login_required
def rent_item(item_id):
    if current_user.role != 'customer':
        flash('Only customers can rent items', 'danger')
        return redirect(url_for('home'))

    if not current_user.membership_active:
        flash('You need to activate your membership first by making a deposit', 'warning')
        return redirect(url_for('make_deposit'))

    item = Item.query.get_or_404(item_id)

    # Check if item is available
    if not item.available:
        flash('Sorry, this item is currently unavailable', 'warning')
        return redirect(url_for('browse_items'))

    # Check if customer already has a video CD or music CD rented
    has_video = Rental.query.filter_by(user_id=current_user.id, status='approved').join(Item).filter_by(
        type='video_cd').first()
    has_music = Rental.query.filter_by(user_id=current_user.id, status='approved').join(Item).filter_by(
        type='music_cd').first()

    if (item.type == 'video_cd' and has_video) or (item.type == 'music_cd' and has_music):
        flash(f'You already have a {item.type} rented. Please return it before renting another.', 'warning')
        return redirect(url_for('customer_dashboard'))

    if request.method == 'POST':
        days = int(request.form.get('days', 1))

        due_date = datetime.utcnow().replace(hour=23, minute=59, second=59) + timedelta(days=days)

        new_rental = Rental(
            user_id=current_user.id,
            item_id=item.id,
            due_date=due_date,
            total_charge=item.daily_rate * days
        )

        # Mark item as unavailable
        item.available = False
        db.session.add(new_rental)
        db.session.commit()

        flash('Rental request submitted and awaiting clerk approval', 'success')
        return redirect(url_for('customer_dashboard'))

    return render_template('rent_item.html', item=item)


"""@app.route('/clerk/approve/<int:rental_id>', methods=['GET', 'POST'])
@login_required
def approve_rental(rental_id):
    if current_user.role != 'clerk' and current_user.role != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('home'))

    rental = Rental.query.get_or_404(rental_id)

    if rental.status != 'pending':
        flash('This rental is not pending approval', 'warning')
        return redirect(url_for('clerk_dashboard'))

    if request.method == 'POST':
        rental.status = 'approved'
        rental.approved_by = current_user.id
        db.session.commit()

        # Send email to customer
        user = User.query.get(rental.user_id)
        item = Item.query.get(rental.item_id)

        try:
            msg = Message(
                subject='Rental Approved - Receipt',
                recipients=[user.email],
                body=f'''
                Dear {user.name},

                Your rental request has been approved!

                Item: {item.title}
                Type: {item.type}
                Format: {item.format}
                Daily Rate: Rs. {item.daily_rate}
                Total Charge: Rs. {rental.total_charge}
                Due Date: {rental.due_date.strftime('%Y-%m-%d')}

                Thank you for using our Video Rental Service!
                '''
            )
            mail.send(msg)
            flash('Rental approved and receipt emailed to customer', 'success')
        except Exception as e:
            flash(f'Rental approved but email failed to send: {str(e)}', 'warning')

        return redirect(url_for('clerk_dashboard'))

    return render_template('approve_rental.html', rental=rental)
"""

@app.route('/approve_rental/<int:rental_id>', methods=['GET', 'POST'])
@login_required
def approve_rental(rental_id):
    if current_user.role not in ['clerk', 'admin']:
        flash('Access denied: You are not authorized to approve rentals.', 'danger')
        return redirect(url_for('clerk_dashboard'))

    rental = Rental.query.get_or_404(rental_id)
    user = User.query.get(rental.user_id)
    item = Item.query.get(rental.item_id)

    if rental.status != 'pending':
        flash('Rental request is not pending.', 'warning')
        return redirect(url_for('clerk_dashboard'))

    if request.method == 'POST':
        action = request.form.get('action')
        note = request.form.get('note', '')

        if action == 'approve':
            rental.status = 'approved'
            rental.approved_by = current_user.id
            rental.approved_date = datetime.utcnow()
            # Update the last_issued_date for the item
            rental.item.last_issued_date = datetime.utcnow()
            # Calculate total charge and deduct from user's deposit
            rental_days = max((rental.due_date - rental.rental_date).days, 1)
            total_charge = item.daily_rate * rental_days
            rental.total_charge = total_charge
            user.deposit -= total_charge

            if user.deposit < 0:
                flash('User does not have enough deposit to approve this rental.', 'danger')
                return redirect(url_for('clerk_dashboard'))

            item.available = False  # Mark item as unavailable
            db.session.commit()

            # Send approval email
            try:
                msg = Message(
                    subject='Rental Approved - Receipt',
                    recipients=[user.email],
                    body=f'''
                        Dear {user.name},

                        Your rental request has been approved!

                        Item: {item.title}
                        Type: {item.type}
                        Format: {item.format}
                        Daily Rate: Rs. {item.daily_rate}
                        Total Charge: Rs. {rental.total_charge}
                        Due Date: {rental.due_date.strftime('%Y-%m-%d')}

                        Thank you for using our Video Rental Service!
                    '''
                )
                mail.send(msg)
                flash('Rental approved and receipt emailed to customer', 'success')
            except Exception as e:
                flash(f'Rental approved but email failed to send: {str(e)}', 'warning')

        elif action == 'deny':
            rental.status = 'declined'
            rental.note = note  # Save the clerk's note
            item.available = True
            db.session.commit()

            # Send denial email
            try:
                msg = Message(
                    subject='Rental Declined',
                    recipients=[user.email],
                    body=f'''
                        Dear {user.name},

                        Your rental request has been declined.

                        Item: {item.title}
                        Type: {item.type}
                        Note from Clerk: {note}

                        If you have any questions, please contact us.

                        Thank you for using our Video Rental Service!
                    '''
                )
                mail.send(msg)
                flash('Rental declined and email sent to customer', 'success')
            except Exception as e:
                flash(f'Rental declined but email failed to send: {str(e)}', 'warning')

        return redirect(url_for('clerk_dashboard'))

    return render_template('approve_rental.html', rental=rental, user=user, item=item)


"""@app.route('/approve_rental/<int:rental_id>', methods=['GET', 'POST'])
@login_required
def approve_rental(rental_id):
    if current_user.role not in ['clerk', 'admin']:
        flash('Access denied: You are not authorized to approve rentals.', 'danger')
        return redirect(url_for('clerk_dashboard'))

    rental = Rental.query.get_or_404(rental_id)
    user = User.query.get(rental.user_id)
    item = Item.query.get(rental.item_id)

    if rental.status != 'pending':
        flash('Rental request is not pending.', 'warning')
        return redirect(url_for('clerk_dashboard'))

    if request.method == 'POST':
        rental.status = 'approved'
        rental.approved_by = current_user.id

        # Calculate total charge and deduct from user's deposit
        rental_days = max((rental.due_date - rental.rental_date).days, 1)
        total_charge = item.daily_rate * rental_days
        rental.total_charge = total_charge
        user.deposit -= total_charge

        if user.deposit < 0:
            flash('User does not have enough deposit to approve this rental.', 'danger')
            return redirect(url_for('clerk_dashboard'))

        item.available = False  # Mark item as unavailable
        db.session.commit()

        # Send email to customer
        user = User.query.get(rental.user_id)
        item = Item.query.get(rental.item_id)

        try:
            msg = Message(
                subject='Rental Approved - Receipt',
                recipients=[user.email],
                body=f'''
                            Dear {user.name},

                            Your rental request has been approved!

                            Item: {item.title}
                            Type: {item.type}
                            Format: {item.format}
                            Daily Rate: Rs. {item.daily_rate}
                            Total Charge: Rs. {rental.total_charge}
                            Due Date: {rental.due_date.strftime('%Y-%m-%d')}

                            Thank you for using our Video Rental Service!
                            '''
            )
            mail.send(msg)
            flash('Rental approved and receipt emailed to customer', 'success')
        except Exception as e:
            flash(f'Rental approved but email failed to send: {str(e)}', 'warning')

        return redirect(url_for('clerk_dashboard'))
    return render_template('approve_rental.html', rental=rental, user=user, item=item)
"""
"""@app.route('/approve_rental/<int:rental_id>', methods=['GET', 'POST'])
@login_required
def approve_rental(rental_id):
    if current_user.role != 'clerk' or current_user.role != 'admin':
        flash('Access denied: You are not authorized to approve rentals.', 'danger')
        return redirect(url_for('clerk_dashboard'))

    rental = Rental.query.get_or_404(rental_id)
    user = User.query.get(rental.user_id)  # Fetch the user associated with the rental
    item = Item.query.get(rental.item_id)  # Fetch the item associated with the rental

    if request.method == 'POST':
        rental.status = 'approved'
        rental.approved_by = current_user.id
        
        # Calculate total charge and deduct from user's deposit
        total_charge = rental.item.daily_rate * ((rental.due_date - rental.rental_date).days or 1)
        rental.total_charge = total_charge
        rental.user.deposit -= total_charge
        
        if rental.user.deposit < 0:
            flash('User does not have enough deposit to approve this rental.', 'danger')
            return redirect(url_for('clerk_dashboard'))

        db.session.commit()
        flash('Rental request approved successfully.', 'success')

        # Send email to customer
        user = User.query.get(rental.user_id)
        item = Item.query.get(rental.item_id)

        try:
            msg = Message(
                subject='Rental Approved - Receipt',
                recipients=[user.email],
                body=f'''
                    Dear {user.name},

                    Your rental request has been approved!

                    Item: {item.title}
                    Type: {item.type}
                    Format: {item.format}
                    Daily Rate: Rs. {item.daily_rate}
                    Total Charge: Rs. {rental.total_charge}
                    Due Date: {rental.due_date.strftime('%Y-%m-%d')}

                    Thank you for using our Video Rental Service!
                    '''
            )
            mail.send(msg)
            flash('Rental approved and receipt emailed to customer', 'success')
        except Exception as e:
            flash(f'Rental approved but email failed to send: {str(e)}', 'warning')

        return redirect(url_for('clerk_dashboard'))

    # Pass the user and item objects to the template
    return render_template('approve_rental.html', rental=rental, user=user, item=item)
"""
"""@app.route('/clerk/return/<int:rental_id>', methods=['GET', 'POST'])
@login_required
def return_item(rental_id):
    if current_user.role != 'clerk' and current_user.role != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('home'))

    rental = Rental.query.get_or_404(rental_id)

    if rental.status != 'approved':
        flash('This rental is not active', 'warning')
        return redirect(url_for('clerk_dashboard'))

    if request.method == 'POST':
        rental.status = 'returned'
        rental.return_date = datetime.utcnow()

        # Make item available again
        item = Item.query.get(rental.item_id)
        item.available = True

        db.session.commit()
        flash('Item returned successfully', 'success')
        return redirect(url_for('clerk_dashboard'))

    return render_template('return_item.html', rental=rental)
"""

@app.route('/clerk/early_returns', methods=['GET', 'POST'])
@login_required
def manage_early_returns():
    if current_user.role != 'clerk':
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))

    early_returns = Rental.query.filter_by(early_return_requested=True, early_return_status='pending').all()

    return render_template('manage_early_returns.html', early_returns=early_returns)

@app.route('/process_early_return/<int:rental_id>', methods=['POST'])
@login_required
def process_early_return(rental_id):
    if current_user.role != 'clerk':
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))

    rental = Rental.query.get_or_404(rental_id)
    action = request.form.get('action')

    if action == 'approve':
        rental.early_return_status = 'approved'
        rental.status = 'returned'
        rental.return_date = datetime.utcnow()
        rental.item.available = True
        flash('Early return approved.', 'success')
    elif action == 'deny':
        rental.early_return_status = 'denied'
        flash('Early return denied.', 'info')

    rental.early_return_requested = False
    db.session.commit()

    return redirect(url_for('manage_early_returns'))

@app.route('/return_item/<int:rental_id>', methods=['GET', 'POST'])
@login_required
def return_item(rental_id):
    if current_user.role not in ['clerk', 'admin']:
        flash('Access denied: You are not authorized to process returns.', 'danger')
        return redirect(url_for('clerk_dashboard'))

    rental = Rental.query.get_or_404(rental_id)
    user = User.query.get(rental.user_id)
    item = Item.query.get(rental.item_id)

    if rental.status != 'approved':
        flash('Rental is not active.', 'warning')
        return redirect(url_for('clerk_dashboard'))

    if request.method == 'POST':
        rental.return_date = datetime.utcnow()
        actual_days = max((rental.return_date - rental.rental_date).days, 1)
        actual_charge = item.daily_rate * actual_days

        # Adjust the user's deposit
        refund = rental.total_charge - actual_charge
        user.deposit += refund
        rental.status = 'returned'
        item.available = True  # Mark item as available

        db.session.commit()
        flash('Item returned successfully. Deposit adjusted.', 'success')
        return redirect(url_for('clerk_dashboard'))

    return render_template('return_item.html', rental=rental, user=user, item=item)

"""
@app.route('/clerk/return/<int:rental_id>', methods=['GET', 'POST'])
@login_required
def return_item(rental_id):
    if current_user.role != 'clerk':
        flash('Access denied: You are not authorized to process returns.', 'danger')
        return redirect(url_for('clerk_dashboard'))

    rental = Rental.query.get_or_404(rental_id)
    user = User.query.get(rental.user_id)  # Fetch the user associated with the rental
    item = Item.query.get(rental.item_id)  # Fetch the item associated with the rental

    if request.method == 'POST':
        rental.return_date = datetime.utcnow()
        rental.status = 'returned'
        item.available = True  # Mark the item as available

        # Calculate the rental duration in days
        rental_duration = (rental.return_date - rental.rental_date).days
        if rental_duration < 1:
            rental_duration = 1  # Minimum charge for one day

        # Update the total charge
        rental.total_charge = rental_duration * item.daily_rate

        print(f"Calculated Total Charge: {rental.total_charge}")
        user.deposit = user.deposit - rental.total_charge
        # Commit changes to the database
        db.session.commit()

        flash(f'Item returned successfully. Total charge: Rs. {rental.total_charge}', 'success')
        return redirect(url_for('clerk_dashboard'))

    # Pass the user and item objects to the template
    return render_template('return_item.html', rental=rental, user=user, item=item)
"""
@app.route('/admin/add_item', methods=['GET', 'POST'])
@login_required
def add_item():
    if current_user.role != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('home'))

    if request.method == 'POST':
        title = request.form.get('title')
        item_type = request.form.get('type')
        format = request.form.get('format')
        genre = request.form.get('genre')
        daily_rate = request.form.get('daily_rate')
        purchase_price = request.form.get('purchase_price')

        # Validate input fields
        if not title or not item_type or not format or not genre or not daily_rate or not purchase_price:
            flash('All fields are required.', 'danger')
            return redirect(url_for('add_item'))

        try:
            daily_rate = float(daily_rate)
            purchase_price = float(purchase_price)
        except ValueError:
            flash('Daily rate and purchase price must be valid numbers.', 'danger')
            return redirect(url_for('add_item'))

        # Add the new item to the database
        new_item = Item(
            title=title,
            type=item_type,
            format=format,
            genre=genre,
            daily_rate=daily_rate,
            purchase_price=purchase_price,
            available=True
        )

        db.session.add(new_item)
        db.session.commit()
        flash('Item added successfully.', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('add_item.html')

@app.route('/admin/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    if current_user.role != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('home'))

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')

        user_exists = User.query.filter_by(email=email).first()
        if user_exists:
            flash('Email already registered', 'danger')
            return redirect(url_for('add_user'))

        hashed_password = generate_password_hash(password)
        new_user = User(
            name=name,
            email=email,
            password=hashed_password,
            role=role
        )

        db.session.add(new_user)
        db.session.commit()
        flash('User added successfully', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('add_user.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        # Create admin user if not exists
        admin = User.query.filter_by(email='admin@example.com').first()
        if not admin:
            admin = User(
                name='Admin',
                email='admin@example.com',
                password=generate_password_hash('admin123'),
                role='admin'
            )
            db.session.add(admin)

        # Create clerk user if not exists
        clerk = User.query.filter_by(email='clerk@example.com').first()
        if not clerk:
            clerk = User(
                name='Clerk',
                email='clerk@example.com',
                password=generate_password_hash('clerk123'),
                role='clerk'
            )
            db.session.add(clerk)

        db.session.commit()

    app.run(debug=True)