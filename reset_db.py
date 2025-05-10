import os
import logging
from datetime import datetime, timedelta
from app import app, db
from models import Disaster, DisasterType, State, RiskAssessment, DisasterAlert

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def reset_database():
    """Clear all data and recreate the database with proper coordinates"""
    with app.app_context():
        logger.info("Resetting database...")
        
        # Drop all data
        try:
            DisasterAlert.__table__.drop(db.engine)
            RiskAssessment.__table__.drop(db.engine)
            Disaster.__table__.drop(db.engine)
            DisasterType.__table__.drop(db.engine)
            State.__table__.drop(db.engine)
            logger.info("Tables dropped")
        except Exception as e:
            logger.error(f"Error dropping tables: {str(e)}")
        
        # Create all tables
        db.create_all()
        logger.info("Tables recreated")
        
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
        
        # Initialize disaster types
        disaster_types = {
            "Flood": "Overflow of water that submerges land that is usually dry",
            "Earthquake": "Sudden shaking of the ground due to movement of tectonic plates",
            "Tsunami": "Series of ocean waves caused by an underwater earthquake, landslide, or volcanic eruption",
            "Forest Fire": "Uncontrolled fire occurring in forests and other wildland areas"
        }
        
        # Add disaster types
        disaster_type_map = {}
        for name, description in disaster_types.items():
            disaster_type = DisasterType(name=name, description=description)
            db.session.add(disaster_type)
            db.session.flush()  # Get ID without committing
            disaster_type_map[name] = disaster_type
            logger.info(f"Added disaster type: {name}")
        
        # Add Malaysian states
        state_map = {}
        for state_name, coordinates in state_coordinates.items():
            state = State(name=state_name)
            db.session.add(state)
            db.session.flush()  # Get ID without committing
            state_map[state_name] = state
            logger.info(f"Added state: {state_name}")
        
        # Add sample disasters with correct coordinates
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
                "source": "Sample Data"
            }
        ]
        
        # Add disasters with proper coordinates
        for disaster_data in sample_disasters:
            disaster_type = disaster_type_map[disaster_data["type"]]
            state = state_map[disaster_data["state"]]
            state_coords = state_coordinates[disaster_data["state"]]
            
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
                latitude=state_coords[0],  # Use correct coordinates
                longitude=state_coords[1],  # Use correct coordinates
                source=disaster_data["source"],
                source_url="https://example.com/sample-data"
            )
            db.session.add(disaster)
            logger.info(f"Added disaster: {disaster_data['title']} at {state_coords}")
        
        # Add alerts for active disasters
        for disaster in Disaster.query.filter_by(is_active=True).all():
            alert = DisasterAlert(
                disaster_id=disaster.id,
                title=f"Alert: {disaster.title}",
                message=f"Emergency alert for {disaster.title}. Please follow safety protocols and evacuation procedures if in affected area.",
                alert_level=disaster.severity,
                issued_at=disaster.start_date,
                expires_at=datetime.utcnow() + timedelta(days=7),
                is_active=True
            )
            db.session.add(alert)
            logger.info(f"Added alert for: {disaster.title}")
        
        # Add risk assessments for all states and disaster types
        for state_name, state in state_map.items():
            for disaster_type_name, disaster_type in disaster_type_map.items():
                # Determine risk level based on specific combinations
                risk_level = 2  # Default to low risk
                
                # Set known high-risk combinations
                if (state_name == "Kelantan" and disaster_type_name == "Flood") or \
                   (state_name == "Sabah" and disaster_type_name == "Earthquake") or \
                   (state_name == "Penang" and disaster_type_name == "Tsunami"):
                    risk_level = 5  # Life-threatening
                elif state_name in ["Terengganu", "Pahang"] and disaster_type_name == "Flood":
                    risk_level = 4  # High risk
                elif state_name in ["Sarawak", "Selangor"] and disaster_type_name == "Forest Fire":
                    risk_level = 4  # High risk
                
                state_coords = state_coordinates[state_name]
                
                assessment = RiskAssessment(
                    state_id=state.id,
                    disaster_type_id=disaster_type.id,
                    location_name=f"{state_name} Center",
                    risk_level=risk_level,
                    latitude=state_coords[0],
                    longitude=state_coords[1],
                    probability=0.1 * risk_level,  # Simple probability
                    details=f"Risk assessment for {disaster_type_name} in {state_name}",
                    last_assessed=datetime.utcnow()
                )
                db.session.add(assessment)
        
        db.session.commit()
        logger.info("Database reset and populated with correct coordinates")

if __name__ == "__main__":
    reset_database()