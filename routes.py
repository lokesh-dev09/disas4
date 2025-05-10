import os
import logging
from flask import render_template, request, jsonify, redirect, url_for
from app import app, db
from models import Disaster, DisasterType, State, RiskAssessment, DisasterAlert
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Add now function for templates
@app.template_global()
def now():
    return datetime.utcnow()

@app.route('/')
def index():
    """Home page route"""
    # Get statistics for the dashboard
    total_disasters = Disaster.query.count()
    active_disasters = Disaster.query.filter_by(is_active=True).count()
    alerts = DisasterAlert.query.filter_by(is_active=True).count()
    
    # Get recent disasters
    recent_disasters = Disaster.query.order_by(Disaster.start_date.desc()).limit(5).all()
    
    # Get disaster types for statistics
    disaster_types = DisasterType.query.all()
    
    # Prepare disaster data by type
    disasters_by_type = {}
    for dt in disaster_types:
        count = Disaster.query.filter_by(disaster_type_id=dt.id).count()
        disasters_by_type[dt.name] = count
    
    # Get high risk areas
    high_risk_areas = RiskAssessment.query.filter(RiskAssessment.risk_level >= 4).limit(5).all()
    
    return render_template('index.html', 
                           total_disasters=total_disasters,
                           active_disasters=active_disasters,
                           alerts=alerts,
                           recent_disasters=recent_disasters,
                           disasters_by_type=disasters_by_type,
                           high_risk_areas=high_risk_areas,
                           DisasterType=DisasterType)

@app.route('/map')
def map_page():
    """Interactive map page"""
    # Get disaster types and states for filtering
    disaster_types = DisasterType.query.all()
    states = State.query.all()
    
    # Get filter parameters
    disaster_type_id = request.args.get('disaster_type', type=int)
    state_id = request.args.get('state', type=int)
    
    return render_template('map.html', 
                           disaster_types=disaster_types,
                           states=states,
                           selected_disaster_type=disaster_type_id,
                           selected_state=state_id)

@app.route('/alerts')
def alerts_page():
    """Alerts listing page"""
    # Get disaster types and states for filtering
    disaster_types = DisasterType.query.all()
    states = State.query.all()
    
    # Get filter parameters
    disaster_type_id = request.args.get('disaster_type', type=int)
    state_id = request.args.get('state', type=int)
    active_only = request.args.get('active_only', type=bool, default=True)
    
    # Base query - exclude test alerts and check if disasters are actually active
    query = DisasterAlert.query.join(Disaster).filter(DisasterAlert.is_test == False)
    
    # Apply filters
    if disaster_type_id:
        query = query.filter(Disaster.disaster_type_id == disaster_type_id)
    
    if state_id:
        query = query.filter(Disaster.state_id == state_id)
    
    if active_only:
        # Make sure both the alert is active and the disaster is still active
        query = query.filter(DisasterAlert.is_active == True)
        query = query.filter(Disaster.is_active == True)
    
    # Order by issued date
    alerts = query.order_by(DisasterAlert.issued_at.desc()).all()
    
    # If expired alert has a related disaster that's no longer active, 
    # and that info isn't reflected in the alert, update it
    for alert in alerts:
        if alert.is_active and not alert.disaster.is_active:
            with app.app_context():
                alert.is_active = False
                db.session.commit()
    
    return render_template('alerts.html', 
                           alerts=alerts,
                           disaster_types=disaster_types,
                           states=states,
                           selected_disaster_type=disaster_type_id,
                           selected_state=state_id,
                           active_only=active_only)

@app.route('/about')
def about_page():
    """About page with information about the project"""
    return render_template('about.html')

@app.route('/who-we-are')
def who_we_are_page():
    """Who We Are page with team information"""
    return render_template('who_we_are.html')

# API endpoints for fetching data for the frontend
@app.route('/api/disasters')
def get_disasters():
    """API endpoint to get disaster data for map"""
    # Get filter parameters
    disaster_type_id = request.args.get('disaster_type', type=int)
    state_id = request.args.get('state', type=int)
    active_only = request.args.get('active_only', type=bool, default=False)
    
    # Base query
    query = Disaster.query
    
    # Apply filters
    if disaster_type_id:
        query = query.filter_by(disaster_type_id=disaster_type_id)
    
    if state_id:
        query = query.filter_by(state_id=state_id)
    
    if active_only:
        query = query.filter_by(is_active=True)
    
    # Get disasters
    disasters = query.all()
    
    # Format data for frontend
    data = []
    for disaster in disasters:
        data.append({
            'id': disaster.id,
            'title': disaster.title,
            'type': disaster.type.name,
            'state': disaster.state.name,
            'start_date': disaster.start_date.strftime('%Y-%m-%d'),
            'end_date': disaster.end_date.strftime('%Y-%m-%d') if disaster.end_date else None,
            'is_active': disaster.is_active,
            'severity': disaster.severity,
            'latitude': disaster.latitude,
            'longitude': disaster.longitude,
            'description': disaster.description
        })
    
    return jsonify(data)

@app.route('/api/risk_assessments')
def get_risk_assessments():
    """API endpoint to get risk assessment data for map"""
    # Get filter parameters
    disaster_type_id = request.args.get('disaster_type', type=int)
    state_id = request.args.get('state', type=int)
    min_risk_level = request.args.get('min_risk_level', type=int, default=1)
    
    # Base query
    query = RiskAssessment.query
    
    # Apply filters
    if disaster_type_id:
        query = query.filter_by(disaster_type_id=disaster_type_id)
    
    if state_id:
        query = query.filter_by(state_id=state_id)
    
    if min_risk_level > 1:
        query = query.filter(RiskAssessment.risk_level >= min_risk_level)
    
    # Get risk assessments
    assessments = query.all()
    
    # Format data for frontend
    data = []
    for assessment in assessments:
        disaster_type = DisasterType.query.get(assessment.disaster_type_id)
        if disaster_type and assessment.state:
            data.append({
                'id': assessment.id,
                'location_name': assessment.location_name,
                'disaster_type': disaster_type.name,
                'state': assessment.state.name,
                'risk_level': assessment.risk_level,
                'latitude': assessment.latitude,
                'longitude': assessment.longitude,
                'details': assessment.details,
                'last_assessed': assessment.last_assessed.strftime('%Y-%m-%d')
            })
    
    return jsonify(data)

@app.route('/api/alerts')
def get_alerts():
    """API endpoint to get alert data"""
    # Get filter parameters
    disaster_type_id = request.args.get('disaster_type', type=int)
    state_id = request.args.get('state', type=int)
    active_only = request.args.get('active_only', type=bool, default=True)
    
    # Base query
    query = DisasterAlert.query.join(Disaster)
    
    # Apply filters
    if disaster_type_id:
        query = query.filter(Disaster.disaster_type_id == disaster_type_id)
    
    if state_id:
        query = query.filter(Disaster.state_id == state_id)
    
    if active_only:
        query = query.filter(DisasterAlert.is_active == True)
    
    # Order by issued date
    alerts = query.order_by(DisasterAlert.issued_at.desc()).all()
    
    # Format data for frontend
    data = []
    for alert in alerts:
        disaster = alert.disaster
        if disaster and disaster.type and disaster.state:
            data.append({
                'id': alert.id,
                'title': alert.title,
                'message': alert.message,
                'alert_level': alert.alert_level,
                'issued_at': alert.issued_at.strftime('%Y-%m-%d %H:%M'),
                'expires_at': alert.expires_at.strftime('%Y-%m-%d %H:%M') if alert.expires_at else None,
                'is_active': alert.is_active,
                'disaster': {
                    'id': disaster.id,
                    'title': disaster.title,
                    'type': disaster.type.name,
                    'state': disaster.state.name,
                    'latitude': disaster.latitude,
                    'longitude': disaster.longitude
                }
            })
    
    return jsonify(data)

@app.route('/api/statistics')
def get_statistics():
    """API endpoint to get statistics for charts"""
    # Get disasters by type
    disaster_types = DisasterType.query.all()
    disasters_by_type = {}
    for dt in disaster_types:
        count = Disaster.query.filter_by(disaster_type_id=dt.id).count()
        disasters_by_type[dt.name] = count
    
    # Get disasters by state
    states = State.query.all()
    disasters_by_state = {}
    for state in states:
        count = Disaster.query.filter_by(state_id=state.id).count()
        disasters_by_state[state.name] = count
    
    # Get disasters by month (for the current year)
    current_year = datetime.now().year
    start_of_year = datetime(current_year, 1, 1)
    disasters_by_month = {}
    for month in range(1, 13):
        month_start = datetime(current_year, month, 1)
        if month == 12:
            month_end = datetime(current_year+1, 1, 1) - timedelta(days=1)
        else:
            month_end = datetime(current_year, month+1, 1) - timedelta(days=1)
        
        count = Disaster.query.filter(
            Disaster.start_date >= month_start,
            Disaster.start_date <= month_end
        ).count()
        
        month_name = month_start.strftime('%b')
        disasters_by_month[month_name] = count
    
    # Get risk assessment distribution
    risk_levels = {}
    for level in range(1, 6):
        count = RiskAssessment.query.filter_by(risk_level=level).count()
        risk_levels[f"Level {level}"] = count
    
    return jsonify({
        'disasters_by_type': disasters_by_type,
        'disasters_by_state': disasters_by_state,
        'disasters_by_month': disasters_by_month,
        'risk_levels': risk_levels,
        'total_disasters': Disaster.query.count(),
        'active_disasters': Disaster.query.filter_by(is_active=True).count(),
        'active_alerts': DisasterAlert.query.filter_by(is_active=True).count()
    })
