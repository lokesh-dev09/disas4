from app import db
from datetime import datetime

class DisasterType(db.Model):
    """Model for types of disasters"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text)
    
    disasters = db.relationship('Disaster', backref='type', lazy=True)
    
    def __repr__(self):
        return f"<DisasterType {self.name}>"


class State(db.Model):
    """Model for Malaysian states"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    
    disasters = db.relationship('Disaster', backref='state', lazy=True)
    risk_assessments = db.relationship('RiskAssessment', backref='state', lazy=True)
    
    def __repr__(self):
        return f"<State {self.name}>"


class Disaster(db.Model):
    """Model for historical disaster events"""
    id = db.Column(db.Integer, primary_key=True)
    disaster_type_id = db.Column(db.Integer, db.ForeignKey('disaster_type.id'), nullable=False)
    state_id = db.Column(db.Integer, db.ForeignKey('state.id'), nullable=False)
    
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    # Specific metrics for different disasters
    magnitude = db.Column(db.Float)  # For earthquakes
    depth = db.Column(db.Float)      # For tsunamis (in cm)
    area_affected = db.Column(db.Float)  # For floods, forest fires (in sq km)
    
    severity = db.Column(db.Integer)  # 1-5 (5 being most severe)
    
    # Geolocation
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    
    # Data source
    source = db.Column(db.String(100))
    source_url = db.Column(db.String(255))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Disaster {self.title}>"


class RiskAssessment(db.Model):
    """Model for risk assessments of different areas"""
    id = db.Column(db.Integer, primary_key=True)
    state_id = db.Column(db.Integer, db.ForeignKey('state.id'), nullable=False)
    disaster_type_id = db.Column(db.Integer, db.ForeignKey('disaster_type.id'), nullable=False)
    
    location_name = db.Column(db.String(100))
    risk_level = db.Column(db.Integer)  # 1-5 (5 being highest risk)
    
    # Geolocation
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    
    probability = db.Column(db.Float)  # Probability score from the ML model
    
    details = db.Column(db.Text)  # Additional information
    last_assessed = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<RiskAssessment {self.location_name} - Level {self.risk_level}>"


class DisasterAlert(db.Model):
    """Model for active alerts"""
    id = db.Column(db.Integer, primary_key=True)
    disaster_id = db.Column(db.Integer, db.ForeignKey('disaster.id'), nullable=False)
    disaster = db.relationship('Disaster')
    
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    alert_level = db.Column(db.Integer, nullable=False)  # 1-5 (5 being most severe)
    
    issued_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    is_test = db.Column(db.Boolean, default=False)  # Flag for test alerts
    
    # ML sources and external information
    sources_used = db.Column(db.Text)  # Comma-separated list of sources used by ML
    external_references = db.Column(db.Text)  # JSON string of external URLs and references
    
    def __repr__(self):
        return f"<DisasterAlert {self.title}>"
