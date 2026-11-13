from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='customer') # 'customer', 'hoster', 'admin'
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'

class Donor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    full_name = db.Column(db.String(100), nullable=False)
    blood_group = db.Column(db.String(5), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    last_donated = db.Column(db.Date, nullable=True)
    is_available = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Donor {self.full_name} ({self.blood_group})>'

class BloodRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) # Added for user tracking
    patient_name = db.Column(db.String(100), nullable=False)
    blood_group_required = db.Column(db.String(5), nullable=False)
    units_required = db.Column(db.Integer, nullable=False)
    hospital_name = db.Column(db.String(150), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    contact_phone = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='Pending') # Pending, Approved, Rejected, Fulfilled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<BloodRequest {self.blood_group_required} for {self.patient_name}>'

class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) # Added for user tracking
    title = db.Column(db.String(200), nullable=False)
    host_name = db.Column(db.String(200), nullable=True) # e.g. College/Hospital name
    host_type = db.Column(db.String(50), nullable=True) # College, Hospital, NGO
    contact_email = db.Column(db.String(120), nullable=True)
    contact_phone = db.Column(db.String(20), nullable=True)
    date = db.Column(db.Date, nullable=False)
    time_start = db.Column(db.Time, nullable=False)
    time_end = db.Column(db.Time, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='Pending') # Pending, Approved, Rejected

    def __repr__(self):
        return f'<Campaign {self.title}>'

class CampaignRegistration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    donor_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    blood_group = db.Column(db.String(10), nullable=False)
    address = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(50), nullable=False)
    medical_notes = db.Column(db.Text, nullable=True)
    registration_time = db.Column(db.DateTime, default=datetime.utcnow)

    campaign = db.relationship('Campaign', backref=db.backref('registrations', lazy=True))
    user = db.relationship('User', backref=db.backref('campaign_registrations', lazy=True))

class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    blood_group = db.Column(db.String(10), nullable=True)
    city = db.Column(db.String(50), nullable=True)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ContactMessage from {self.name}>'

class NewsletterSubscriber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    subscribed_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Subscriber {self.email}>'
