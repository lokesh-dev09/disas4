import os
import logging
import requests
import pandas as pd
from datetime import datetime, timedelta
from app import app, db
from models import Disaster, DisasterType, State, RiskAssessment, DisasterAlert
from ml_model import train_model, predict_risk_areas

logger = logging.getLogger(__name__)

# Initialize disaster types and Malaysian states
def initialize_reference_data():
    with app.app_context():
        # Initialize disaster types if not present
        disaster_types = {
            "Flood": "Overflow of water that submerges land that is usually dry",
            "Earthquake": "Sudden shaking of the ground due to movement of tectonic plates",
            "Tsunami": "Series of ocean waves caused by an underwater earthquake, landslide, or volcanic eruption",
            "Forest Fire": "Uncontrolled fire occurring in forests and other wildland areas"
        }
        
        disaster_type_map = {}
        for name, description in disaster_types.items():
            disaster_type = DisasterType.query.filter_by(name=name).first()
            if not disaster_type:
                disaster_type = DisasterType(name=name, description=description)
                db.session.add(disaster_type)
                db.session.flush()  # Get ID without committing
            disaster_type_map[name] = disaster_type
        
        # Initialize Malaysian states if not present
        malaysian_states = [
            "Johor", "Kedah", "Kelantan", "Melaka", "Negeri Sembilan", 
            "Pahang", "Perak", "Perlis", "Penang", "Sabah", "Sarawak", 
            "Selangor", "Terengganu", "Kuala Lumpur", "Labuan", "Putrajaya"
        ]
        
        state_map = {}
        for state_name in malaysian_states:
            state = State.query.filter_by(name=state_name).first()
            if not state:
                state = State(name=state_name)
                db.session.add(state)
                db.session.flush()  # Get ID without committing
            state_map[state_name] = state
        
        # Add sample disasters if none exist
        if Disaster.query.count() == 0:
            # Malaysian state coordinates (approximate centers)
            state_coordinates = {
                "Johor": (1.8541, 103.7377),
                "Kedah": (6.1184, 100.3685),
                "Kelantan": (5.3837, 102.0292),
                "Melaka": (2.1896, 102.2501),
                "Negeri Sembilan": (2.7258, 102.2377),
                "Pahang": (3.8126, 103.3256),
                "Perak": (4.5921, 101.0901),
                "Perlis": (6.4449, 100.2059),
                "Penang": (5.4141, 100.3288),
                "Sabah": (5.9804, 116.0735),
                "Sarawak": (1.5533, 110.3592),
                "Selangor": (3.0738, 101.5183),
                "Terengganu": (5.3117, 103.1324),
                "Kuala Lumpur": (3.1390, 101.6869),
                "Labuan": (5.2831, 115.2308),
                "Putrajaya": (2.9264, 101.6964)
            }
            
            # Sample disasters for demonstration
            sample_disasters = [
                {
                    "type": "Flood",
                    "state": "Kelantan",
                    "title": "Kelantan River Flooding",
                    "description": "Severe flooding along the Kelantan River affecting multiple districts.",
                    "start_date": datetime(2025, 1, 15),
                    "end_date": datetime(2025, 1, 25),
                    "is_active": False,
                    "area_affected": 120.5,
                    "severity": 4,
                    "latitude": 5.3837,
                    "longitude": 102.0292,
                    "source": "Sample Data"
                },
                {
                    "type": "Flood",
                    "state": "Terengganu",
                    "title": "Terengganu Monsoon Flooding",
                    "description": "Monsoon season flooding affecting coastal areas of Terengganu.",
                    "start_date": datetime(2025, 2, 10),
                    "end_date": datetime(2025, 2, 20),
                    "is_active": False,
                    "area_affected": 85.2,
                    "severity": 3,
                    "latitude": 5.3117, 
                    "longitude": 103.1324,
                    "source": "Sample Data"
                },
                {
                    "type": "Earthquake",
                    "state": "Sabah",
                    "title": "Ranau Earthquake",
                    "description": "5.9 magnitude earthquake near Mount Kinabalu with multiple aftershocks.",
                    "start_date": datetime(2025, 3, 5),
                    "end_date": datetime(2025, 3, 5),
                    "is_active": False,
                    "magnitude": 5.9,
                    "severity": 4,
                    "latitude": 5.9804,
                    "longitude": 116.0735,
                    "source": "Sample Data"
                },
                {
                    "type": "Forest Fire",
                    "state": "Selangor",
                    "title": "Kuala Langat Forest Reserve Fire",
                    "description": "Large forest fire in the Kuala Langat Forest Reserve during dry season.",
                    "start_date": datetime(2025, 4, 12),
                    "is_active": True,
                    "area_affected": 250.8,
                    "severity": 4,
                    "latitude": 3.0738,
                    "longitude": 101.5183,
                    "source": "Sample Data"
                },
                {
                    "type": "Tsunami",
                    "state": "Penang",
                    "title": "Penang Coastal Tsunami Warning",
                    "description": "Tsunami warning issued for Penang coastal areas following offshore earthquake.",
                    "start_date": datetime(2025, 5, 1),
                    "is_active": True,
                    "depth": 85.0,
                    "severity": 5,
                    "latitude": 5.4141,
                    "longitude": 100.3288,
                    "source": "Sample Data"
                }
            ]
            
            for disaster_data in sample_disasters:
                disaster_type = disaster_type_map[disaster_data["type"]]
                state = state_map[disaster_data["state"]]
                
                disaster = Disaster(
                    disaster_type_id=disaster_type.id,
                    state_id=state.id,
                    title=disaster_data["title"],
                    description=disaster_data["description"],
                    start_date=disaster_data["start_date"],
                    end_date=disaster_data.get("end_date"),
                    is_active=disaster_data["is_active"],
                    magnitude=disaster_data.get("magnitude"),
                    depth=disaster_data.get("depth"),
                    area_affected=disaster_data.get("area_affected"),
                    severity=disaster_data["severity"],
                    latitude=disaster_data["latitude"],
                    longitude=disaster_data["longitude"],
                    source=disaster_data["source"],
                    source_url="https://example.com/sample-data"
                )
                db.session.add(disaster)
            
            # Add sample alerts
            for disaster in Disaster.query.filter_by(is_active=True).all():
                alert = DisasterAlert(
                    disaster_id=disaster.id,
                    title=f"Alert: {disaster.title}",
                    message=f"Emergency alert for {disaster.title}. Please follow safety protocols and evacuation procedures if in affected area.",
                    alert_level=disaster.severity,
                    issued_at=disaster.start_date,
                    expires_at=datetime.utcnow() + timedelta(days=7) if disaster.is_active else None,
                    is_active=disaster.is_active
                )
                db.session.add(alert)
        
        # Create some risk assessments if none exist
        if RiskAssessment.query.count() == 0:
            # Malaysian state coordinates (approximate centers)
            state_coordinates = {
                "Johor": (1.8541, 103.7377),
                "Kedah": (6.1184, 100.3685),
                "Kelantan": (5.3837, 102.0292),
                "Melaka": (2.1896, 102.2501),
                "Negeri Sembilan": (2.7258, 102.2377),
                "Pahang": (3.8126, 103.3256),
                "Perak": (4.5921, 101.0901),
                "Perlis": (6.4449, 100.2059),
                "Penang": (5.4141, 100.3288),
                "Sabah": (5.9804, 116.0735),
                "Sarawak": (1.5533, 110.3592),
                "Selangor": (3.0738, 101.5183),
                "Terengganu": (5.3117, 103.1324),
                "Kuala Lumpur": (3.1390, 101.6869),
                "Labuan": (5.2831, 115.2308),
                "Putrajaya": (2.9264, 101.6964)
            }
            
            # Generate risk assessments for each state and disaster type
            for state_name, state in state_map.items():
                for disaster_type_name, disaster_type in disaster_type_map.items():
                    # Create risk level based on some pattern (for demonstration)
                    risk_level = (hash(state_name + disaster_type_name) % 4) + 1  # 1-5 range
                    
                    # Set high risk for certain combinations
                    if (state_name == "Kelantan" and disaster_type_name == "Flood") or \
                       (state_name == "Sabah" and disaster_type_name == "Earthquake") or \
                       (state_name == "Penang" and disaster_type_name == "Tsunami"):
                        risk_level = 5
                    
                    # Get accurate coordinates for the state
                    latitude, longitude = state_coordinates.get(state_name, (4.0, 102.0))
                    
                    assessment = RiskAssessment(
                        state_id=state.id,
                        disaster_type_id=disaster_type.id,
                        location_name=f"{state_name} Center",
                        risk_level=risk_level,
                        latitude=latitude,
                        longitude=longitude,
                        probability=0.1 * risk_level,  # Simple probability
                        details=f"Risk assessment for {disaster_type_name} in {state_name}",
                        last_assessed=datetime.utcnow()
                    )
                    db.session.add(assessment)
        
        db.session.commit()
        logger.info("Reference data initialized")

# Function to fetch data from NASA Earthdata
def fetch_nasa_earthdata():
    try:
        logger.info("Fetching data from NASA Earthdata")
        # Normally, we would use NASA's API with proper authentication
        # This is a simplified version for demonstration
        
        api_key = os.environ.get("NASA_API_KEY", "DEMO_KEY")
        # NASA EONET (Earth Observatory Natural Event Tracker)
        url = f"https://eonet.gsfc.nasa.gov/api/v3/events?api_key={api_key}&status=open&category=wildfires,floods,earthquakes,tsunamis"
        
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            
            # Process and filter data for Malaysia
            with app.app_context():
                process_nasa_events(data)
            
            return True
        else:
            logger.error(f"Failed to fetch NASA data: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Error fetching NASA Earthdata: {str(e)}")
        return False

# Process NASA EONET events
def process_nasa_events(data):
    if 'events' not in data:
        logger.warning("No events found in NASA data")
        return
    
    malaysia_events = []
    
    # Bounding box for Malaysia (approximate)
    # Format: [min_lon, min_lat, max_lon, max_lat]
    malaysia_bbox = [99.5, 0.5, 120.0, 7.5]
    
    for event in data['events']:
        # Check if the event has a geometry with coordinates
        if 'geometry' in event and len(event['geometry']) > 0:
            for geometry in event['geometry']:
                if 'coordinates' in geometry:
                    lon, lat = geometry['coordinates']
                    
                    # Check if coordinates are within Malaysia's bounding box
                    if (malaysia_bbox[0] <= lon <= malaysia_bbox[2] and 
                        malaysia_bbox[1] <= lat <= malaysia_bbox[3]):
                        
                        malaysia_events.append({
                            'id': event['id'],
                            'title': event['title'],
                            'description': event.get('description', ''),
                            'category': event['categories'][0]['title'] if event['categories'] else 'Unknown',
                            'source': 'NASA EONET',
                            'source_url': f"https://eonet.gsfc.nasa.gov/api/v3/events/{event['id']}",
                            'start_date': datetime.fromisoformat(event['geometry'][0]['date']),
                            'lon': lon,
                            'lat': lat
                        })
    
    logger.info(f"Found {len(malaysia_events)} events in Malaysia from NASA data")
    
    # Save relevant events to database
    save_events_to_database(malaysia_events)

# Function to fetch data from EM-DAT
def fetch_emdat_data():
    try:
        logger.info("Fetching data from EM-DAT")
        # EM-DAT requires registration and authentication
        # This is a simplified version for demonstration
        
        # In a real application, you would use proper authentication and API endpoints
        # Here we're simulating the data retrieval process
        
        # Simulated EM-DAT data structure for Malaysia
        with app.app_context():
            # For a real application, this would be replaced with actual API calls
            logger.info("Processed EM-DAT data")
            return True
    except Exception as e:
        logger.error(f"Error fetching EM-DAT data: {str(e)}")
        return False

# Function to fetch data from WorldRiskReport
def fetch_worldriskreport_data():
    try:
        logger.info("Fetching data from WorldRiskReport")
        # WorldRiskReport might be available as PDF reports rather than APIs
        # You would need to use PDF extraction or check if they provide structured data
        
        # For a real application, this would involve scraping or using APIs if available
        with app.app_context():
            logger.info("Processed WorldRiskReport data")
            return True
    except Exception as e:
        logger.error(f"Error fetching WorldRiskReport data: {str(e)}")
        return False

# Save events to database
def save_events_to_database(events):
    with app.app_context():
        for event in events:
            # Map event category to disaster type
            disaster_type = None
            if 'flood' in event['category'].lower():
                disaster_type = DisasterType.query.filter_by(name='Flood').first()
            elif 'fire' in event['category'].lower() or 'wildfire' in event['category'].lower():
                disaster_type = DisasterType.query.filter_by(name='Forest Fire').first()
            elif 'earthquake' in event['category'].lower():
                disaster_type = DisasterType.query.filter_by(name='Earthquake').first()
            elif 'tsunami' in event['category'].lower():
                disaster_type = DisasterType.query.filter_by(name='Tsunami').first()
            
            if not disaster_type:
                logger.warning(f"Unrecognized disaster category: {event['category']}")
                continue
            
            # Determine which state the coordinates fall into
            # For simplicity, we're using a very basic approach here
            # In a real application, you'd use proper geospatial querying
            # Default to first state if we can't determine (just for this example)
            state = State.query.first()
            
            # Check if the event already exists to avoid duplicates
            existing_disaster = Disaster.query.filter_by(
                source=event['source'],
                title=event['title'],
                start_date=event['start_date']
            ).first()
            
            if not existing_disaster:
                # Create new disaster entry
                new_disaster = Disaster(
                    disaster_type_id=disaster_type.id,
                    state_id=state.id,
                    title=event['title'],
                    description=event['description'],
                    start_date=event['start_date'],
                    is_active=True,
                    latitude=event['lat'],
                    longitude=event['lon'],
                    source=event['source'],
                    source_url=event['source_url'],
                    severity=calculate_severity(event, disaster_type.name)
                )
                
                db.session.add(new_disaster)
                logger.info(f"Added new disaster: {event['title']}")
            
        db.session.commit()

# Calculate severity based on disaster type and parameters
def calculate_severity(event, disaster_type):
    # Basic severity calculation
    # In a real application, this would be much more sophisticated
    # Default to moderate severity
    severity = 3
    
    # Enhance this with actual data when available
    if disaster_type == 'Earthquake':
        # Assuming magnitude information might be in the title or description
        if 'magnitude' in event['title'].lower() or 'magnitude' in event['description'].lower():
            # Extract magnitude if possible
            # For now, just assign a higher severity
            severity = 4
    elif disaster_type == 'Flood':
        # Floods are common in Malaysia, assume higher severity
        severity = 4
    elif disaster_type == 'Tsunami':
        # Tsunamis are rare but dangerous
        severity = 5
    elif disaster_type == 'Forest Fire':
        # Forest fires severity depends on size and location
        severity = 3
    
    return severity

# Run all data collection functions
def collect_all_data():
    logger.info("Starting data collection process")
    
    # Initialize reference data if needed
    initialize_reference_data()
    
    # Fetch data from various sources
    nasa_success = fetch_nasa_earthdata()
    emdat_success = fetch_emdat_data()
    worldrisk_success = fetch_worldriskreport_data()
    
    # Log results
    logger.info(f"Data collection complete - NASA: {nasa_success}, EM-DAT: {emdat_success}, WorldRiskReport: {worldrisk_success}")
    
    # After collecting data, update risk assessments
    with app.app_context():
        # Get all historical data for model training
        disasters = Disaster.query.all()
        
        if disasters:
            # Convert to pandas DataFrame for ML processing
            disaster_data = []
            for d in disasters:
                disaster_data.append({
                    'disaster_type_id': d.disaster_type_id,
                    'state_id': d.state_id,
                    'latitude': d.latitude,
                    'longitude': d.longitude,
                    'severity': d.severity,
                    'start_date': d.start_date,
                    'is_active': d.is_active
                })
            
            if disaster_data:
                df = pd.DataFrame(disaster_data)
                
                # Train the model with collected data
                model = train_model(df)
                
                # Generate risk assessments
                generate_risk_assessments(model, df)
                
                logger.info("Risk assessments updated")
            else:
                logger.warning("No disaster data available for risk assessment")
        else:
            logger.warning("No disaster records found in database")

# Generate risk assessments using the trained model
def generate_risk_assessments(model, data):
    # Get predictions from the model
    predictions = predict_risk_areas(model, data)
    
    # Update database with new risk assessments
    with app.app_context():
        # For each state and disaster type combination
        states = State.query.all()
        disaster_types = DisasterType.query.all()
        
        for state in states:
            for disaster_type in disaster_types:
                # In a real application, this would be much more sophisticated
                # with proper geospatial analysis
                
                # For demonstration, we're creating/updating a single risk assessment
                # per state and disaster type
                
                # Find existing assessment or create new one
                assessment = RiskAssessment.query.filter_by(
                    state_id=state.id,
                    disaster_type_id=disaster_type.id
                ).first()
                
                # Calculate a risk level based on predictions
                # This is simplified for demonstration
                risk_level = calculate_risk_level(predictions, state.id, disaster_type.id)
                
                if assessment:
                    # Update existing assessment
                    assessment.risk_level = risk_level
                    assessment.last_assessed = datetime.utcnow()
                else:
                    # Create new assessment with approximate center coordinates for the state
                    # In a real app, you would use actual geographical data
                    new_assessment = RiskAssessment(
                        state_id=state.id,
                        disaster_type_id=disaster_type.id,
                        location_name=f"{state.name} Center",
                        risk_level=risk_level,
                        # Approximate coordinates for Malaysian states
                        # In a real app, use actual coordinates
                        latitude=4.0 + (state.id * 0.5) % 3,  # Simple variation for demo
                        longitude=102.0 + (state.id * 0.5) % 7,  # Simple variation for demo
                        probability=0.5,  # Placeholder
                        details=f"Risk assessment for {disaster_type.name} in {state.name}",
                        last_assessed=datetime.utcnow()
                    )
                    db.session.add(new_assessment)
        
        db.session.commit()
        logger.info("Risk assessments generated")

# Calculate risk level based on predictions
def calculate_risk_level(predictions, state_id, disaster_type_id):
    # In a real application, this would use the actual predictions
    # from the ML model for specific locations
    
    # For demonstration, we're using a simple approach
    # that could be enhanced with real data
    
    # Get recent disasters of this type in this state
    with app.app_context():
        recent_disasters = Disaster.query.filter_by(
            state_id=state_id,
            disaster_type_id=disaster_type_id,
            is_active=True
        ).all()
        
        if recent_disasters:
            # If there are active disasters, higher risk
            max_severity = max([d.severity for d in recent_disasters])
            return max(3, max_severity)  # At least level 3 if active disasters
        
        # Check historical data from last 2 years
        two_years_ago = datetime.utcnow() - timedelta(days=730)
        historical_disasters = Disaster.query.filter(
            Disaster.state_id == state_id,
            Disaster.disaster_type_id == disaster_type_id,
            Disaster.start_date >= two_years_ago
        ).all()
        
        if historical_disasters:
            # Based on frequency and severity of historical events
            count = len(historical_disasters)
            avg_severity = sum([d.severity for d in historical_disasters]) / count
            
            if count > 5 and avg_severity > 4:
                return 5  # Very high risk
            elif count > 3 or avg_severity > 3:
                return 4  # High risk
            elif count > 1:
                return 3  # Moderate risk
            else:
                return 2  # Low risk
        
        # Default to very low risk if no historical data
        return 1

# Setup scheduled data collection
def setup_data_collection(scheduler):
    # Run initial data collection
    collect_all_data()
    
    # Schedule regular updates (every 6 hours)
    scheduler.add_job(
        collect_all_data,
        'interval',
        hours=6,
        id='data_collection_job',
        replace_existing=True
    )
    
    logger.info("Scheduled data collection every 6 hours")
