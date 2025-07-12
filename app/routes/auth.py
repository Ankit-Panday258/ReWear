from flask import render_template, Blueprint, redirect, url_for, request, flash, session, jsonify
from app import db
from app.models.users import User
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps

auth = Blueprint('auth', __name__)

def login_required(f):
    """Decorator to require login for protected routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        
        if not session.get('is_admin', False):
            flash('Admin privileges required to access this page.', 'danger')
            return redirect(url_for('listing.index'))
        
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Get the current logged-in user"""
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None

def logout_required(f):
    """Decorator to redirect logged-in users away from auth pages"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' in session:
            flash('You are already logged in.', 'info')
            return redirect(url_for('listing.index'))
        return f(*args, **kwargs)
    return decorated_function

@auth.route("/register")
@logout_required
def register():
    return render_template("user/register.html")

@auth.route("/register", methods=["POST"])
@logout_required
def register_post():
    try:
        # Get form data
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validate input
        if not all([username, email, password, confirm_password]):
            flash('Please fill in all fields.', 'danger')
            return render_template("user/register.html")
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template("user/register.html")
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template("user/register.html")
        
        if len(username) < 3:
            flash('Username must be at least 3 characters long.', 'danger')
            return render_template("user/register.html")
        
        # Basic email validation
        if '@' not in email or '.' not in email:
            flash('Please enter a valid email address.', 'danger')
            return render_template("user/register.html")
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email address already registered.', 'danger')
            return render_template("user/register.html")
        
        # Check if username is taken
        existing_username = User.query.filter_by(username=username).first()
        if existing_username:
            flash('Username already taken.', 'danger')
            return render_template("user/register.html")
        
        # Create new user
        new_user = User(
            username=username,
            email=email,
            password=generate_password_hash(password),
            points=100,  # Starting points
            is_admin=False
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
        
    except Exception as e:
        db.session.rollback()
        flash('An error occurred during registration. Please try again.', 'danger')
        return render_template("user/register.html")

@auth.route("/login")
@logout_required
def login():
    return render_template("user/login.html")

@auth.route("/login", methods=["POST"])
@logout_required
def login_post():
    try:
        # Get form data
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember_me = request.form.get('remember_me') == 'on'
        
        # Validate input
        if not email or not password:
            flash('Please enter both email and password.', 'danger')
            return render_template("user/login.html")
        
        # Find user
        user = User.query.filter_by(email=email).first()
        
        # Check credentials
        if not user or not check_password_hash(user.password, password):
            flash('Invalid email or password.', 'danger')
            return render_template("user/login.html")
        
        # Log in user
        session['user_id'] = user.user_id
        session['username'] = user.username
        session['is_admin'] = user.is_admin
        session['user_points'] = user.points
        
        # Set session to permanent if remember me is checked
        if remember_me:
            session.permanent = True
        
        flash(f'Welcome back, {user.username}!', 'success')
        
        # Redirect to next page or listings
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        
        return redirect(url_for('listing.index'))
        
    except Exception as e:
        flash('An error occurred during login. Please try again.', 'danger')
        return render_template("user/login.html")

@auth.route("/logout")
@login_required
def logout():
    username = session.get('username', 'User')
    # Clear session
    session.clear()
    flash(f'Goodbye {username}! You have been logged out successfully.', 'info')
    return redirect(url_for('home.index'))

@auth.route("/check-email")
def check_email():
    """AJAX endpoint to check if email is already registered"""
    email = request.args.get('email', '').strip().lower()
    
    if not email:
        return jsonify({'available': False, 'message': 'Email is required'})
    
    existing_user = User.query.filter_by(email=email).first()
    
    if existing_user:
        return jsonify({'available': False, 'message': 'Email already registered'})
    else:
        return jsonify({'available': True, 'message': 'Email available'})

@auth.route("/check-username")
def check_username():
    """AJAX endpoint to check if username is already taken"""
    username = request.args.get('username', '').strip()
    
    if not username:
        return jsonify({'available': False, 'message': 'Username is required'})
    
    if len(username) < 3:
        return jsonify({'available': False, 'message': 'Username must be at least 3 characters'})
    
    existing_user = User.query.filter_by(username=username).first()
    
    if existing_user:
        return jsonify({'available': False, 'message': 'Username already taken'})
    else:
        return jsonify({'available': True, 'message': 'Username available'})

@auth.route("/api/current-user")
def get_current_user_api():
    """API endpoint to get current user info"""
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            # Update session with latest user data
            session['user_points'] = user.points
            return jsonify(user.to_dict())
    
    return jsonify({'error': 'Not logged in'}), 401

@auth.route("/forgot-password")
@logout_required
def forgot_password():
    """Placeholder for forgot password functionality"""
    flash('Forgot password functionality will be implemented soon.', 'info')
    return redirect(url_for('auth.login'))

# Utility function to update user session data
def update_user_session(user_id):
    """Update session data for a user (useful after profile changes)"""
    user = User.query.get(user_id)
    if user and session.get('user_id') == user_id:
        session['username'] = user.username
        session['is_admin'] = user.is_admin
        session['user_points'] = user.points
        return True
    return False
