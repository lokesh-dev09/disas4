import logging
import numpy as np
import pandas as pd
import json
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from datetime import datetime

# Import our web scraper for enhanced data collection
import web_scraper

logger = logging.getLogger(__name__)

# Function to preprocess the data for ML model
def preprocess_data(df):
    """
    Preprocess the disaster data for machine learning
    """
    logger.info("Preprocessing data for ML model")
    
    # Check if we have enough data
    if len(df) < 10:
        logger.warning("Not enough data for reliable model training")
        # Return a simplified dataset for demonstration
        return df, None
    
    # Handle missing values
    df = df.fillna({
        'severity': 3,  # Default to medium severity
        'is_active': False,
    })
    
    # Feature engineering
    # Extract month from start_date for seasonality
    if 'start_date' in df.columns:
        df['month'] = df['start_date'].apply(lambda x: x.month)
    
    # Create features dataframe
    features = ['disaster_type_id', 'state_id', 'latitude', 'longitude']
    
    # Add month if available
    if 'month' in df.columns:
        features.append('month')
    
    # Add active status if available
    if 'is_active' in df.columns:
        features.append('is_active')
    
    # Select features that exist in the dataframe
    valid_features = [f for f in features if f in df.columns]
    
    # Prepare X and y
    X = df[valid_features]
    y = df['severity']
    
    # Convert boolean to int if needed
    if 'is_active' in X.columns:
        X['is_active'] = X['is_active'].astype(int)
    
    # Normalize numerical features
    scaler = StandardScaler()
    numeric_features = ['latitude', 'longitude']
    valid_numeric = [f for f in numeric_features if f in X.columns]
    
    if valid_numeric:
        X[valid_numeric] = scaler.fit_transform(X[valid_numeric])
    
    return X, y

# Train the ML model
def train_model(df):
    """
    Train a machine learning model on disaster data
    """
    logger.info("Training ML model")
    
    X, y = preprocess_data(df)
    
    # If we don't have enough processed data
    if y is None:
        logger.warning("Using simplified model due to insufficient data")
        return create_simple_model()
    
    # Split the data
    try:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train the model
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Evaluate the model
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        logger.info(f"Model accuracy: {accuracy:.2f}")
        
        # More detailed evaluation
        report = classification_report(y_test, y_pred)
        logger.debug(f"Classification report:\n{report}")
        
        return model
    except Exception as e:
        logger.error(f"Error training model: {str(e)}")
        return create_simple_model()

# Create a simple model when data is insufficient
def create_simple_model():
    """
    Create a simplified model when not enough data is available
    """
    logger.info("Creating simplified risk model")
    
    # Simple Random Forest with default behavior
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    
    # Minimal feature set (just need something that can predict)
    X_minimal = np.array([[1, 1, 0, 0], [2, 2, 1, 1], [3, 3, 0, 1], [4, 4, 1, 0], [5, 5, 0, 0]])
    y_minimal = np.array([1, 2, 3, 4, 5])
    
    model.fit(X_minimal, y_minimal)
    return model

# Predict risk areas using the trained model
def predict_risk_areas(model, data):
    """
    Use the trained model to predict risk levels for different areas
    """
    logger.info("Predicting risk areas")
    
    # For a real application, we would:
    # 1. Generate a grid of points covering Malaysia
    # 2. For each point, create features similar to our training data
    # 3. Run predictions on these points
    # 4. Aggregate results into risk zones
    
    # For this demonstration, we'll use a simplified approach
    try:
        X, _ = preprocess_data(data)
        
        if X is None:
            logger.warning("Cannot predict with insufficient data")
            return None
        
        # Make predictions on the existing data points
        predictions = model.predict(X)
        
        # Combine predictions with original location data
        prediction_df = pd.DataFrame({
            'latitude': data['latitude'],
            'longitude': data['longitude'],
            'disaster_type_id': data['disaster_type_id'],
            'state_id': data['state_id'],
            'predicted_risk': predictions
        })
        
        logger.info(f"Generated {len(prediction_df)} risk predictions")
        return prediction_df
    
    except Exception as e:
        logger.error(f"Error predicting risk areas: {str(e)}")
        return None

# Fetch and incorporate additional data from external sources
def enrich_data_from_external_sources(base_data):
    """
    Enhances the base dataset with additional data from web sources
    
    Args:
        base_data: DataFrame with base disaster data
        
    Returns:
        Enhanced DataFrame with additional features
    """
    if base_data is None or len(base_data) == 0:
        return base_data
        
    logger.info("Enriching data from external sources")
    
    # Create a copy to avoid modifying the original
    enhanced_data = base_data.copy()
    
    # Add new columns for additional data
    enhanced_data['historical_frequency'] = 0
    enhanced_data['external_risk_factor'] = 0
    enhanced_data['news_mention_count'] = 0
    
    # For each disaster type, load historical data
    for disaster_type_id in enhanced_data['disaster_type_id'].unique():
        try:
            # Get disaster type name (in real app, would fetch from DB)
            disaster_type = "flood" if disaster_type_id == 1 else \
                           "earthquake" if disaster_type_id == 2 else \
                           "tsunami" if disaster_type_id == 3 else \
                           "forest fire"
            
            # Load historical data for this disaster type
            historical_data = web_scraper.load_historical_data(disaster_type)
            
            # Calculate historical frequency for each state
            if 'events' in historical_data and len(historical_data['events']) > 0:
                for idx, row in enhanced_data[enhanced_data['disaster_type_id'] == disaster_type_id].iterrows():
                    # Count historical events in this state
                    state_events = sum(1 for event in historical_data['events'] 
                                    if 'location' in event and str(event['location']).lower() in str(row['state_id']).lower())
                    
                    # Update the frequency
                    enhanced_data.at[idx, 'historical_frequency'] = state_events
                    
                    # Set external risk factor based on historical data
                    if state_events > 2:
                        enhanced_data.at[idx, 'external_risk_factor'] = 0.8
                    elif state_events > 0:
                        enhanced_data.at[idx, 'external_risk_factor'] = 0.5
                    else:
                        enhanced_data.at[idx, 'external_risk_factor'] = 0.2
        
        except Exception as e:
            logger.error(f"Error enriching data for disaster type {disaster_type_id}: {str(e)}")
    
    logger.info(f"Data enrichment complete, added {len(enhanced_data.columns) - len(base_data.columns)} new features")
    return enhanced_data

# Process data through deep learning model with external data integration
def deep_learning_prediction(data=None, disaster_type=None, location=None):
    """
    Deep learning model for more complex prediction with web data integration
    In a real application, this would use TensorFlow and more sophisticated models
    
    Args:
        data: Optional DataFrame with existing data
        disaster_type: Optional disaster type to focus on
        location: Optional location to analyze
        
    Returns:
        Prediction results and data sources used
    """
    logger.info("Running enhanced deep learning prediction with web data integration")
    
    try:
        # Collect data for analysis
        sources_used = []
        
        # If we have specific disaster type and location, analyze reports
        if disaster_type and location:
            # Search for news articles
            logger.info(f"Searching for information about {disaster_type} in {location}")
            
            # This would call the web scraper to get real-time data
            analysis = web_scraper.analyze_disaster_reports(disaster_type, location)
            sources_used.extend(analysis.get('sources', []))
            
            # Would integrate with TensorFlow for prediction in a real app
            prediction = {
                "disaster_type": disaster_type,
                "location": location,
                "risk_level": 4,  # Example value (would be from actual model)
                "confidence": 0.85,
                "factors": analysis.get('risk_factors', []),
                "sources_used": sources_used,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return prediction
        else:
            # With no specific focus, return generic message
            logger.info("Deep learning prediction requires specific disaster type and location")
            return None
            
    except Exception as e:
        logger.error(f"Error in deep learning prediction: {str(e)}")
        return None
