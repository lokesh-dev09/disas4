import logging
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from datetime import datetime

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

# Process deep learning model (simplified for this demo)
def deep_learning_prediction():
    """
    Deep learning model for more complex prediction
    In a real application, this would be implemented with TensorFlow
    """
    logger.info("Deep learning prediction not fully implemented")
    # This would be expanded in a real implementation
    return None
