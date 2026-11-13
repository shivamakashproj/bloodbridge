from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.actions import action
from markupsafe import Markup
from models import db, User, Donor, BloodRequest, Campaign, CampaignRegistration, ContactMessage, NewsletterSubscriber
import os
import re
import html
import time
from datetime import datetime, timedelta

# ─────────────────────────────────────────────────────────────
#  SECURITY & REGEX VALIDATORS
# ─────────────────────────────────────────────────────────────
# Standard Email Regex (RFC 5322 compatible format)
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')

# Phone Regex: Accepts 10-digit Indian numbers with optional +91 or 0 prefix, or 10-15 digit standard numbers
PHONE_REGEX = re.compile(r'^(\+91[\-\s]?)?[0]?[6-9]\d{9}$')

# Password Criteria Regex:
# - Minimum 8 characters
# - At least one uppercase letter [A-Z]
# - At least one lowercase letter [a-z]
# - At least one digit [0-9]
# - At least one special symbol [@$!%*?&#^_\-+=<>.,]
PASSWORD_REGEX = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#^_\-+=<>.,])[A-Za-z\d@$!%*?&#^_\-+=<>.,]{8,}$')

def is_valid_email(email):
    """Validates email format using regex."""
    if not email or not isinstance(email, str):
        return False
    return bool(EMAIL_REGEX.match(email.strip()))

def is_valid_phone(phone):
    """Validates 10-digit mobile number using regex."""
    if not phone or not isinstance(phone, str):
        return False
    cleaned = re.sub(r'[\s\-\(\)]', '', phone.strip())
    return bool(PHONE_REGEX.match(cleaned) or (cleaned.isdigit() and 10 <= len(cleaned) <= 15))

def is_valid_password(password):
    """Validates password strength criteria using regex."""
    if not password or not isinstance(password, str):
        return False
    return bool(PASSWORD_REGEX.match(password))

# ─────────────────────────────────────────────────────────────
#  IN-MEMORY IP RATE LIMITER & SANITIZER
# ─────────────────────────────────────────────────────────────
RATE_LIMIT_STORE = {}

def check_rate_limit(action_name, limit=5, window_seconds=60):
    """
    Checks if client IP has exceeded the threshold within window_seconds.
    Returns (True, retry_after) if blocked, (False, 0) if allowed.
    """
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr or '127.0.0.1').split(',')[0].strip()
    key = f"{action_name}:{client_ip}"
    now = time.time()
    history = [t for t in RATE_LIMIT_STORE.get(key, []) if now - t < window_seconds]
    if len(history) >= limit:
        oldest = history[0]
        retry_after = int(window_seconds - (now - oldest)) + 1
        return True, retry_after
    history.append(now)
    RATE_LIMIT_STORE[key] = history
    return False, 0

def clear_rate_limit(action_name):
    """Clears rate limit records upon successful authentication/action."""
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr or '127.0.0.1').split(',')[0].strip()
    key = f"{action_name}:{client_ip}"
    RATE_LIMIT_STORE.pop(key, None)

def sanitize_input(text, max_length=1000):
    """Sanitizes text against Stored XSS and excessive payload sizes."""
    if not text or not isinstance(text, str):
        return ''
    cleaned = html.escape(text.strip())
    return cleaned[:max_length]


from config import config_by_name

app = Flask(__name__)
env_mode = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config_by_name.get(env_mode, config_by_name['development']))

db.init_app(app)

# ── OWASP SECURITY HEADERS ───────────────────────────────────────────────────
@app.after_request
def apply_security_headers(response):
    """Applies OWASP-recommended security headers to all responses."""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=(self)'
    return response

# ── CUSTOM ERROR HANDLERS ───────────────────────────────────────────────────
@app.errorhandler(400)
def bad_request_error(e):
    return render_template('error.html', error_code='400', error_title='Bad Request', error_message='The server could not understand the request due to invalid or malformed data.'), 400

@app.errorhandler(403)
def forbidden_error(e):
    return render_template('error.html', error_code='403', error_title='Access Forbidden', error_message='You do not have administrative clearance or authority to access this protected area.'), 403

@app.errorhandler(404)
def not_found_error(e):
    return render_template('error.html', error_code='404', error_title='Page Not Found', error_message='The requested endpoint or resource was not found on this server.'), 404

@app.errorhandler(429)
def too_many_requests_error(e):
    return render_template('error.html', error_code='429', error_title='Rate Limit Exceeded', error_message='Too many requests detected. Please wait a moment before trying again.'), 429

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', error_code='500', error_title='Internal Server Error', error_message='An unexpected error occurred. Technical administrators have been alerted.'), 500

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this feature.'
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# ─────────────────────────────────────────────────────────────
#  ADMIN PANEL
# ─────────────────────────────────────────────────────────────
class SecureAdminIndex(AdminIndexView):
    @expose('/')
    def index(self):
        if not (current_user.is_authenticated and current_user.is_admin):
            return redirect(url_for('login', next=request.url))
        stats = {
            'total_donors': Donor.query.count(),
            'total_requests': BloodRequest.query.count(),
            'pending_campaigns': Campaign.query.filter_by(status='Pending').count(),
            'pending_requests': BloodRequest.query.filter_by(status='Pending').count(),
            'total_campaigns': Campaign.query.count(),
            'total_users': User.query.count(),
        }
        recent_requests = BloodRequest.query.order_by(BloodRequest.created_at.desc()).limit(5).all()
        recent_campaigns = Campaign.query.order_by(Campaign.id.desc()).limit(5).all()
        return self.render('admin/dashboard.html', stats=stats,
                           recent_requests=recent_requests,
                           recent_campaigns=recent_campaigns)

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login', next=request.url))


class BaseAdminView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))


class CampaignAdminView(BaseAdminView):
    column_list = ('id', 'title', 'host_name', 'host_type', 'city', 'date', 'status', 'actions')
    column_searchable_list = ['title', 'host_name', 'city']
    column_filters = ['status', 'host_type', 'city']
    can_create = True
    can_edit = True
    can_delete = True

    def _status_formatter(view, context, model, name):
        colors = {'Pending': 'warning', 'Approved': 'success', 'Rejected': 'danger'}
        color = colors.get(model.status, 'secondary')
        return Markup(f'<span class="badge badge-{color}">{model.status}</span>')

    def _actions_formatter(view, context, model, name):
        approve_url = url_for('admin_approve_campaign', campaign_id=model.id)
        reject_url  = url_for('admin_reject_campaign',  campaign_id=model.id)
        return Markup(
            f'<a href="{approve_url}" class="btn btn-sm btn-success me-1">✓ Approve</a>'
            f'<a href="{reject_url}"  class="btn btn-sm btn-danger">✗ Reject</a>'
        )

    column_formatters = {
        'status': _status_formatter,
        'actions': _actions_formatter,
    }


class BloodRequestAdminView(BaseAdminView):
    column_list = ('id', 'patient_name', 'blood_group_required', 'units_required',
                   'hospital_name', 'city', 'contact_phone', 'status', 'created_at', 'actions')
    column_searchable_list = ['patient_name', 'hospital_name', 'city']
    column_filters = ['status', 'blood_group_required', 'city']
    can_create = True
    can_edit = True
    can_delete = True

    def _status_formatter(view, context, model, name):
        colors = {'Pending': 'warning', 'Approved': 'success', 'Rejected': 'danger', 'Fulfilled': 'info'}
        color = colors.get(model.status, 'secondary')
        return Markup(f'<span class="badge badge-{color}">{model.status}</span>')

    def _actions_formatter(view, context, model, name):
        approve_url  = url_for('admin_approve_blood_request', req_id=model.id)
        reject_url   = url_for('admin_reject_blood_request',  req_id=model.id)
        fulfill_url  = url_for('admin_fulfill_blood_request', req_id=model.id)
        return Markup(
            f'<a href="{approve_url}"  class="btn btn-sm btn-success me-1">✓ Approve</a>'
            f'<a href="{reject_url}"   class="btn btn-sm btn-danger me-1">✗ Reject</a>'
            f'<a href="{fulfill_url}"  class="btn btn-sm btn-info">✔ Fulfill</a>'
        )

    column_formatters = {
        'status': _status_formatter,
        'actions': _actions_formatter,
    }


class CampaignRegistrationAdminView(BaseAdminView):
    column_list = ('id', 'campaign', 'donor_name', 'phone', 'age', 'blood_group', 'city', 'medical_notes', 'registration_time')
    column_searchable_list = ['donor_name', 'phone', 'city', 'blood_group']
    column_filters = ['blood_group', 'city', 'campaign_id']


class ContactMessageAdminView(BaseAdminView):
    column_list = ('id', 'name', 'email', 'phone', 'blood_group', 'city', 'message', 'created_at')
    column_searchable_list = ['name', 'email', 'city', 'message']
    column_filters = ['blood_group', 'city']


class NewsletterAdminView(BaseAdminView):
    column_list = ('id', 'email', 'subscribed_at')
    column_searchable_list = ['email']


admin_panel = Admin(app, name='BloodBridge Admin', index_view=SecureAdminIndex())
admin_panel.add_view(BaseAdminView(User, db, name='Users'))
admin_panel.add_view(BaseAdminView(Donor, db, name='Donors'))
admin_panel.add_view(BloodRequestAdminView(BloodRequest, db, name='Blood Requests'))
admin_panel.add_view(CampaignAdminView(Campaign, db, name='Campaigns'))
admin_panel.add_view(CampaignRegistrationAdminView(CampaignRegistration, db, name='Registrations'))
admin_panel.add_view(ContactMessageAdminView(ContactMessage, db, name='Inquiries'))
admin_panel.add_view(NewsletterAdminView(NewsletterSubscriber, db, name='Subscribers'))


# ─────────────────────────────────────────────────────────────
#  ADMIN ACTION ROUTES
# ─────────────────────────────────────────────────────────────
@app.route('/admin/campaign/approve/<int:campaign_id>')
@login_required
def admin_approve_campaign(campaign_id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
    c = Campaign.query.get_or_404(campaign_id)
    c.status = 'Approved'
    db.session.commit()
    flash(f'Campaign "{c.title}" has been approved and is now live!', 'success')
    return redirect(url_for('admin.index'))

@app.route('/admin/campaign/reject/<int:campaign_id>')
@login_required
def admin_reject_campaign(campaign_id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
    c = Campaign.query.get_or_404(campaign_id)
    c.status = 'Rejected'
    db.session.commit()
    flash(f'Campaign "{c.title}" has been rejected.', 'danger')
    return redirect(url_for('admin.index'))

@app.route('/admin/blood-request/approve/<int:req_id>')
@login_required
def admin_approve_blood_request(req_id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
    br = BloodRequest.query.get_or_404(req_id)
    br.status = 'Approved'
    db.session.commit()
    flash(f'Blood request for {br.patient_name} has been approved!', 'success')
    return redirect(url_for('admin.index'))

@app.route('/admin/blood-request/reject/<int:req_id>')
@login_required
def admin_reject_blood_request(req_id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
    br = BloodRequest.query.get_or_404(req_id)
    br.status = 'Rejected'
    db.session.commit()
    flash(f'Blood request for {br.patient_name} has been rejected.', 'danger')
    return redirect(url_for('admin.index'))

@app.route('/admin/blood-request/fulfill/<int:req_id>')
@login_required
def admin_fulfill_blood_request(req_id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
    br = BloodRequest.query.get_or_404(req_id)
    br.status = 'Fulfilled'
    db.session.commit()
    flash(f'Blood request for {br.patient_name} marked as Fulfilled!', 'info')
    return redirect(url_for('admin.index'))


# ─────────────────────────────────────────────────────────────
#  GATEWAY & PUBLIC ROUTES
# ─────────────────────────────────────────────────────────────
@app.route('/home')
@app.route('/landing')
@app.route('/')
def index():
    campaigns = Campaign.query.filter_by(status='Approved').order_by(Campaign.date.asc()).limit(4).all()
    stats = {
        'donors': Donor.query.count(),
        'requests': BloodRequest.query.count(),
        'campaigns': Campaign.query.filter_by(status='Approved').count(),
    }
    return render_template('index.html', campaigns=campaigns, stats=stats)


@app.route('/welcome')
def welcome():
    """Redirect legacy /welcome gateway to main landing page."""
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    role = request.args.get('role', 'donor')
    if role not in ['admin', 'hoster', 'donor']:
        role = 'donor'

    # If already logged in and opening login page via GET, log out previous session
    # so the user can enter new credentials for the selected role without auto-redirect loop
    if request.method == 'GET' and current_user.is_authenticated:
        logout_user()

    if request.method == 'POST':
        # Brute-force protection: Max 5 attempts per minute per IP
        blocked, wait_time = check_rate_limit('login_attempt', limit=5, window_seconds=60)
        if blocked:
            flash(f'⚠️ Too many failed attempts. For security reasons, please wait {wait_time} seconds before trying again.', 'danger')
            return redirect(url_for('login', role=role))

        username = sanitize_input(request.form.get('username'), max_length=80)
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            user_actual_role = getattr(user, 'role', 'customer')
            if user.is_admin:
                user_actual_role = 'admin'

            # 1. Admin Portal Check
            if role == 'admin':
                if not (user.is_admin or user_actual_role == 'admin'):
                    flash('⛔ Access Denied! This portal is strictly for System Administrators. Standard users cannot log in here. Please use the Customer or Hoster Portal.', 'danger')
                    return redirect(url_for('login', role='admin'))

            # 2. Hoster Portal Check
            elif role == 'hoster':
                if user_actual_role != 'hoster':
                    if user.is_admin:
                        flash('⛔ Access Denied! Administrator accounts must log in via the Admin Control Center.', 'warning')
                    else:
                        flash('⛔ Access Denied! This portal is strictly for Drive Organizers (Colleges/Hospitals/NGOs). Please log in via the Customer / Donor Portal or create a Hoster account.', 'danger')
                    return redirect(url_for('login', role='hoster'))

            # 3. Donor/Customer Portal Check
            elif role == 'donor':
                if user_actual_role != 'customer':
                    if user.is_admin:
                        flash('⛔ Access Denied! Administrator accounts must log in via the Admin Control Center.', 'warning')
                    else:
                        flash('⛔ Access Denied! Organization / Hoster accounts must log in via the Drive Organizer Portal.', 'warning')
                    return redirect(url_for('login', role='donor'))

            # Successful Authentication -> Clear failed rate limits
            clear_rate_limit('login_attempt')
            login_user(user)
            flash(f'Welcome back, {user.username}!', 'success')
            
            if user.is_admin or user_actual_role == 'admin':
                return redirect(url_for('admin.index'))
            if user_actual_role == 'hoster':
                return redirect(url_for('my_campaigns'))
            return redirect(url_for('profile'))

        flash('Invalid username or password. Please check your credentials.', 'danger')

    return render_template('login.html', role=role)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('index'))

# ─────────────────────────────────────────────────────────────
#  PASSWORD RESET FEATURE
# ─────────────────────────────────────────────────────────────

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password_request():
    """Handle password reset requests by email."""
    if request.method == 'POST':
        email = sanitize_input(request.form.get('email'), max_length=120)
        if not is_valid_email(email):
            flash('⚠️ Invalid email format.', 'danger')
            return redirect(url_for('reset_password_request'))
        user = User.query.filter_by(email=email).first()
        if user:
            token = URLSafeTimedSerializer(app.config['SECRET_KEY']).dumps(
                user.email, salt='password-reset-salt')
            # In production, send this link via email. Here we flash for demonstration.
            reset_link = url_for('reset_password_token', token=token, _external=True)
            flash(f'Password reset link: {reset_link}', 'info')
        else:
            flash('If an account with that email exists, a reset link has been sent.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password_token(token):
    """Validate reset token and allow the user to set a new password."""
    try:
        email = URLSafeTimedSerializer(app.config['SECRET_KEY']).loads(
            token, salt='password-reset-salt', max_age=3600)
    except SignatureExpired:
        flash('⚠️ The password reset link has expired.', 'danger')
        return redirect(url_for('reset_password_request'))
    except BadSignature:
        flash('⚠️ Invalid password reset token.', 'danger')
        return redirect(url_for('reset_password_request'))

    user = User.query.filter_by(email=email).first()
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('reset_password_request'))

    if request.method == 'POST':
        password = request.form.get('password')
        if not is_valid_password(password):
            flash('⚠️ Weak password! Please follow the password policy.', 'danger')
            return redirect(url_for('reset_password_token', token=token))
        user.password_hash = generate_password_hash(password)
        db.session.commit()
        flash('Your password has been reset. You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('reset_password.html', token=token)

@app.route('/register', methods=['GET', 'POST'])
def register():
    role = request.args.get('role', 'customer')
    if request.method == 'GET' and current_user.is_authenticated:
        logout_user()

    if request.method == 'POST':
        # Registration rate limiter (max 5 accounts per minute per IP)
        blocked, wait_time = check_rate_limit('register_attempt', limit=5, window_seconds=60)
        if blocked:
            flash(f'⚠️ Too many registration attempts. Please wait {wait_time} seconds.', 'danger')
            return redirect(url_for('register', role=role))

        username = sanitize_input(request.form.get('username'), max_length=80)
        email = sanitize_input(request.form.get('email'), max_length=120)
        password = request.form.get('password')
        account_role = request.form.get('role', 'customer')
        if account_role not in ['customer', 'hoster']:
            account_role = 'customer'

        # Regex Validations
        if not is_valid_email(email):
            flash('⚠️ Invalid email format. Example: user@example.com', 'danger')
            return redirect(url_for('register', role=account_role))

        if not is_valid_password(password):
            flash('⚠️ Weak Password! Password must be at least 8 characters long and include at least 1 uppercase letter, 1 lowercase letter, 1 digit, and 1 special symbol (@$!%*?&#^_-+=<>.,).', 'danger')
            return redirect(url_for('register', role=account_role))

        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose another.', 'danger')
            return redirect(url_for('register', role=account_role))
        if User.query.filter_by(email=email).first():
            flash('Email already registered. Please sign in.', 'danger')
            return redirect(url_for('register', role=account_role))

        new_user = User(
            username=username, email=email,
            password_hash=generate_password_hash(password),
            role=account_role,
            is_admin=False
        )
        db.session.add(new_user)
        db.session.commit()
        clear_rate_limit('register_attempt')
        login_user(new_user)
        flash(f'Account created! Welcome, {new_user.username}!', 'success')
        
        if account_role == 'hoster':
            return redirect(url_for('my_campaigns'))
        return redirect(url_for('profile'))

    return render_template('register.html', role=role)


@app.route('/become_donor', methods=['GET', 'POST'])
@login_required
def become_donor():
    # Check if user already registered as donor
    existing = Donor.query.filter_by(user_id=current_user.id).first()
    if existing:
        flash('You are already registered as a donor!', 'info')
        return redirect(url_for('profile'))

    if request.method == 'POST':
        phone = sanitize_input(request.form.get('phone'), max_length=15)
        if not is_valid_phone(phone):
            flash('⚠️ Invalid phone number! Please enter a valid 10-digit mobile number.', 'danger')
            return redirect(url_for('become_donor'))

        donor = Donor(
            user_id=current_user.id,
            full_name=sanitize_input(request.form.get('full_name'), max_length=100),
            blood_group=sanitize_input(request.form.get('blood_group'), max_length=5),
            phone=phone,
            city=sanitize_input(request.form.get('city'), max_length=50),
            is_available=True
        )
        db.session.add(donor)
        db.session.commit()
        flash('🎉 You are now registered as a blood donor! Thank you for saving lives.', 'success')
        return redirect(url_for('profile'))
    return render_template('become_donor.html')


@app.route('/request_blood', methods=['GET', 'POST'])
@login_required
def request_blood():
    if request.method == 'POST':
        contact_phone = sanitize_input(request.form.get('contact_phone'), max_length=15)
        if not is_valid_phone(contact_phone):
            flash('⚠️ Invalid emergency contact phone number! Please provide a valid 10-digit number.', 'danger')
            return redirect(url_for('request_blood'))

        blood_req = BloodRequest(
            user_id=current_user.id,
            patient_name=sanitize_input(request.form.get('patient_name'), max_length=100),
            blood_group_required=sanitize_input(request.form.get('blood_group_required'), max_length=5),
            units_required=int(request.form.get('units_required', 1)),
            hospital_name=sanitize_input(request.form.get('hospital_name'), max_length=150),
            city=sanitize_input(request.form.get('city'), max_length=50),
            contact_phone=contact_phone,
            status='Pending'
        )
        db.session.add(blood_req)
        db.session.commit()
        flash('🩸 Your blood request has been submitted. Our team will review and connect you with donors shortly.', 'success')
        return redirect(url_for('my_requests'))
    return render_template('request_blood.html')


@app.route('/my_requests')
@login_required
def my_requests():
    blood_requests = BloodRequest.query.filter_by(user_id=current_user.id).order_by(BloodRequest.created_at.desc()).all()
    return render_template('my_requests.html', blood_requests=blood_requests)


@app.route('/host_drive', methods=['GET', 'POST'])
@login_required
def host_drive():
    if request.method == 'POST':
        contact_email = sanitize_input(request.form.get('contact_email'), max_length=120)
        contact_phone = sanitize_input(request.form.get('contact_phone'), max_length=15)

        if not is_valid_email(contact_email):
            flash('⚠️ Invalid coordinator email address format.', 'danger')
            return redirect(url_for('host_drive'))

        if not is_valid_phone(contact_phone):
            flash('⚠️ Invalid coordinator phone number! Please provide a valid 10-digit number.', 'danger')
            return redirect(url_for('host_drive'))

        campaign = Campaign(
            user_id=current_user.id,
            title=sanitize_input(request.form.get('title'), max_length=150),
            host_name=sanitize_input(request.form.get('host_name'), max_length=100),
            host_type=sanitize_input(request.form.get('host_type'), max_length=50),
            contact_email=contact_email,
            contact_phone=contact_phone,
            date=datetime.strptime(request.form.get('date'), '%Y-%m-%d').date(),
            time_start=datetime.strptime(request.form.get('time_start'), '%H:%M').time(),
            time_end=datetime.strptime(request.form.get('time_end'), '%H:%M').time(),
            location=sanitize_input(request.form.get('location'), max_length=255),
            city=sanitize_input(request.form.get('city'), max_length=50),
            description=sanitize_input(request.form.get('description'), max_length=2000),
            status='Pending'
        )
        db.session.add(campaign)
        db.session.commit()
        flash('✅ Your drive request has been submitted! It will appear on the site once approved by admin.', 'success')
        return redirect(url_for('my_campaigns'))
    return render_template('host_drive.html')


@app.route('/my_campaigns')
@login_required
def my_campaigns():
    campaigns = Campaign.query.filter_by(user_id=current_user.id).order_by(Campaign.id.desc()).all()
    return render_template('my_campaigns.html', campaigns=campaigns)





@app.route('/register_campaign/<int:campaign_id>', methods=['GET', 'POST'])
@login_required
def register_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    donor = Donor.query.filter_by(user_id=current_user.id).first()
    existing = CampaignRegistration.query.filter_by(
        campaign_id=campaign_id, user_id=current_user.id
    ).first()
    
    if request.method == 'POST':
        if existing:
            flash(f'You are already registered for "{campaign.title}"!', 'info')
            return redirect(url_for('profile'))
            
        phone = sanitize_input(request.form.get('phone'), max_length=15)
        if not is_valid_phone(phone):
            flash('⚠️ Invalid phone number! Please enter a valid 10-digit mobile number.', 'danger')
            return redirect(url_for('register_campaign', campaign_id=campaign_id))

        reg = CampaignRegistration(
            campaign_id=campaign_id,
            user_id=current_user.id,
            donor_name=sanitize_input(request.form.get('donor_name'), max_length=100),
            phone=phone,
            age=int(request.form.get('age', 18)),
            blood_group=sanitize_input(request.form.get('blood_group'), max_length=5),
            address=sanitize_input(request.form.get('address'), max_length=255),
            city=sanitize_input(request.form.get('city'), max_length=50),
            medical_notes=sanitize_input(request.form.get('medical_notes'), max_length=1000)
        )
        db.session.add(reg)
        db.session.commit()
        flash(f'🎉 You have successfully registered for "{campaign.title}"! Thank you.', 'success')
        return redirect(url_for('profile'))
        
    return render_template('register_campaign.html', campaign=campaign, donor=donor, existing=existing)


@app.route('/campaign/<int:campaign_id>/registrations')
@login_required
def view_campaign_registrations(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    # Ensure only hoster or admin can view donor list
    if campaign.user_id != current_user.id and not current_user.is_admin:
        flash('You are not authorized to view this drive\'s registrations.', 'danger')
        return redirect(url_for('my_campaigns'))
        
    registrations = CampaignRegistration.query.filter_by(campaign_id=campaign_id).order_by(CampaignRegistration.registration_time.desc()).all()
    return render_template('campaign_registrations.html', campaign=campaign, registrations=registrations)


@app.route('/profile')
@login_required
def profile():
    donor_profile = Donor.query.filter_by(user_id=current_user.id).first()
    blood_requests = BloodRequest.query.filter_by(user_id=current_user.id).order_by(BloodRequest.created_at.desc()).all()
    my_drives = Campaign.query.filter_by(user_id=current_user.id).order_by(Campaign.id.desc()).all()
    registrations = CampaignRegistration.query.filter_by(user_id=current_user.id).all()
    return render_template('profile.html',
                           donor_profile=donor_profile,
                           blood_requests=blood_requests,
                           my_drives=my_drives,
                           registrations=registrations)


@app.route('/blood_banks')
def blood_banks():
    return render_template('blood_banks.html')


@app.route('/contact', methods=['POST'])
def contact():
    # Rate limit spam bots: max 5 messages per 60 seconds
    blocked, wait_time = check_rate_limit('contact_attempt', limit=5, window_seconds=60)
    if blocked:
        flash(f'⚠️ Too many messages submitted. Please wait {wait_time} seconds before trying again.', 'danger')
        return redirect(url_for('index') + '#contact')

    name = sanitize_input(request.form.get('name'), max_length=100)
    email = sanitize_input(request.form.get('email'), max_length=120)
    phone = sanitize_input(request.form.get('phone'), max_length=15)
    blood_group = sanitize_input(request.form.get('blood_group'), max_length=10)
    city = sanitize_input(request.form.get('city'), max_length=50)
    message = sanitize_input(request.form.get('message'), max_length=2000)

    if not name or not email or not message:
        flash('Please fill in all required fields (Name, Email, Message).', 'danger')
        return redirect(url_for('index') + '#contact')

    if not is_valid_email(email):
        flash('⚠️ Please provide a valid email address format.', 'danger')
        return redirect(url_for('index') + '#contact')

    if phone and not is_valid_phone(phone):
        flash('⚠️ Please provide a valid 10-digit phone number.', 'danger')
        return redirect(url_for('index') + '#contact')

    msg = ContactMessage(
        name=name, email=email, phone=phone,
        blood_group=blood_group, city=city, message=message
    )
    db.session.add(msg)
    db.session.commit()
    flash('Thank you! Your message has been received. Our team will contact you shortly.', 'success')
    return redirect(url_for('index') + '#contact')


@app.route('/newsletter', methods=['POST'])
def newsletter():
    # Rate limit subscriptions: max 5 attempts per 60 seconds
    blocked, wait_time = check_rate_limit('newsletter_attempt', limit=5, window_seconds=60)
    if blocked:
        flash(f'⚠️ Too many subscription requests. Please wait {wait_time} seconds.', 'danger')
        return redirect(url_for('index') + '#newsletterForm')

    email = sanitize_input(request.form.get('email'), max_length=120)
    if not is_valid_email(email):
        flash('⚠️ Please enter a valid email address to subscribe.', 'danger')
        return redirect(url_for('index') + '#newsletterForm')

    existing = NewsletterSubscriber.query.filter_by(email=email).first()
    if not existing:
        sub = NewsletterSubscriber(email=email)
        db.session.add(sub)
        db.session.commit()
        flash('Thank you for subscribing to BloodBridge emergency alerts!', 'success')
    else:
        flash('You are already subscribed to our newsletter.', 'info')
    return redirect(url_for('index') + '#newsletterForm')


# ---------------------------------------------------
#  FIND DONOR ROUTE
# ---------------------------------------------------
@app.route('/find_donor', methods=['GET', 'POST'])
def find_donor():
    """Search for donors by blood group and city."""
    results = []
    searched = False
    selected_group = ''
    selected_city = ''
    if request.method == 'POST':
        selected_group = request.form.get('blood_group', '').strip()
        selected_city = request.form.get('city', '').strip()
        query = Donor.query
        if selected_group and selected_group != 'All':
            query = query.filter_by(blood_group=selected_group)
        if selected_city:
            query = query.filter(Donor.city.ilike(f"%{selected_city.lower()}%"))
        results = query.order_by(Donor.id.desc()).all()
        searched = True
    else:
        results = Donor.query.order_by(Donor.id.desc()).limit(12).all()
    return render_template('find_donor.html', donors=results, searched=searched, selected_group=selected_group, selected_city=selected_city)


# ─────────────────────────────────────────────────────────────
#  STARTUP
# ─────────────────────────────────────────────────────────────
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

