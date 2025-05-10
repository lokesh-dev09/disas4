import logging
import json
import requests
import trafilatura
import pandas as pd
from datetime import datetime
from io import BytesIO
from app import app

# Configure logging
logger = logging.getLogger(__name__)

def get_website_text_content(url: str) -> str:
    """
    This function takes a url and returns the main text content of the website.
    The text content is extracted using trafilatura and easier to understand.
    The results should be processed further before being used.
    
    Args:
        url: The website URL to scrape
        
    Returns:
        Extracted text content from the website
    """
    try:
        # Send a request to the website
        downloaded = trafilatura.fetch_url(url)
        text = trafilatura.extract(downloaded)
        
        if not text:
            logger.warning(f"No content extracted from {url}")
            return ""
            
        return text
    except Exception as e:
        logger.error(f"Error extracting content from {url}: {str(e)}")
        return ""

def extract_pdf_text(pdf_url: str) -> str:
    """
    Extracts text from a PDF URL.
    
    Args:
        pdf_url: URL to the PDF file
        
    Returns:
        Extracted text from the PDF
    """
    try:
        # Import here to avoid loading these libraries unless needed
        import PyPDF2
        
        # Download the PDF
        response = requests.get(pdf_url)
        
        if response.status_code != 200:
            logger.error(f"Failed to download PDF from {pdf_url}, status code: {response.status_code}")
            return ""
            
        # Read PDF content from response
        with BytesIO(response.content) as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            
            # Extract text from each page
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text += page.extract_text() + "\n\n"
                
            return text.strip()
    except Exception as e:
        logger.error(f"Error extracting PDF content from {pdf_url}: {str(e)}")
        return ""

def search_news_articles(query: str, max_results: int = 5) -> list:
    """
    Searches for news articles related to a disaster query.
    
    Args:
        query: Search term (e.g., "Malaysia flood Kelantan")
        max_results: Maximum number of results to return
        
    Returns:
        List of article information dictionaries
    """
    try:
        # In a production environment, you would use a proper news API with authentication
        # This is a simplified demonstration version
        
        # Example APIs that could be used (requires API keys):
        # - NewsAPI: https://newsapi.org/
        # - GNews: https://gnews.io/
        # - New York Times API: https://developer.nytimes.com/
        
        # Simulated response structure
        logger.info(f"Searching for news articles about: {query}")
        
        # The API key would be loaded from environment variables in a real app
        # api_key = os.environ.get("NEWS_API_KEY")
        
        # Since we don't have actual API keys in this demo, return empty list
        return []
    except Exception as e:
        logger.error(f"Error searching news articles for {query}: {str(e)}")
        return []

def analyze_disaster_reports(disaster_type: str, location: str) -> dict:
    """
    Analyzes multiple data sources to gather information about a disaster.
    
    Args:
        disaster_type: Type of disaster (flood, earthquake, etc.)
        location: Location of the disaster (state, city, etc.)
        
    Returns:
        Dictionary with analysis results and sources
    """
    query = f"{location} {disaster_type} Malaysia"
    sources = []
    
    logger.info(f"Analyzing disaster reports for {disaster_type} in {location}")
    
    # This would call various data sources in a real implementation
    # For demonstration, we'll return a simulated result
    
    return {
        "summary": f"Analysis of {disaster_type} in {location}",
        "risk_factors": [
            f"{location} has historical patterns of {disaster_type}",
            "Climate conditions increasing probability",
            "Geographical features of the area"
        ],
        "sources": sources,
        "timestamp": datetime.utcnow().isoformat()
    }

def load_historical_data(disaster_type: str, format: str = "json") -> dict:
    """
    Loads historical disaster data from various sources, either
    from files or online resources.
    
    Args:
        disaster_type: Type of disaster to find data for
        format: Format of the data (json, csv, etc.)
        
    Returns:
        Dictionary with the data and source information
    """
    logger.info(f"Loading historical data for {disaster_type}")
    
    try:
        # In a real application, this would access actual data sources
        # For demonstration, we'll return simulated historical data
        
        if disaster_type.lower() == "flood":
            data = {
                "events": [
                    {"year": 2023, "location": "Kelantan", "severity": 4, "affected_area_km2": 120.5},
                    {"year": 2022, "location": "Selangor", "severity": 3, "affected_area_km2": 85.2},
                    {"year": 2021, "location": "Pahang", "severity": 5, "affected_area_km2": 210.8}
                ],
                "source": "Department of Irrigation and Drainage, Malaysia",
                "last_updated": "2025-03-15"
            }
        elif disaster_type.lower() == "earthquake":
            data = {
                "events": [
                    {"year": 2024, "location": "Sabah", "magnitude": 5.2, "depth_km": 10},
                    {"year": 2021, "location": "Ranau", "magnitude": 4.8, "depth_km": 8},
                    {"year": 2018, "location": "Ranau", "magnitude": 5.9, "depth_km": 12}
                ],
                "source": "Malaysian Meteorological Department",
                "last_updated": "2025-04-01"
            }
        elif disaster_type.lower() == "tsunami":
            data = {
                "events": [
                    {"year": 2004, "location": "Penang", "wave_height_m": 4, "deaths": 68},
                    {"year": 2004, "location": "Langkawi", "wave_height_m": 3, "deaths": 12}
                ],
                "source": "National Tsunami Warning Center",
                "last_updated": "2025-02-10"
            }
        elif disaster_type.lower() == "forest fire":
            data = {
                "events": [
                    {"year": 2024, "location": "Selangor", "area_hectares": 250, "duration_days": 5},
                    {"year": 2023, "location": "Sarawak", "area_hectares": 320, "duration_days": 8},
                    {"year": 2022, "location": "Sabah", "area_hectares": 180, "duration_days": 4}
                ],
                "source": "Department of Environment, Malaysia",
                "last_updated": "2025-04-15"
            }
        else:
            data = {
                "events": [],
                "source": "Unknown",
                "last_updated": datetime.utcnow().isoformat()
            }
            
        if format.lower() == "csv":
            # Convert to CSV format
            if len(data["events"]) > 0:
                df = pd.DataFrame(data["events"])
                csv_data = df.to_csv(index=False)
                return {
                    "data": csv_data,
                    "source": data["source"],
                    "last_updated": data["last_updated"]
                }
            else:
                return {"data": "", "source": data["source"], "last_updated": data["last_updated"]}
        else:
            # Return as JSON
            return data
            
    except Exception as e:
        logger.error(f"Error loading historical data for {disaster_type}: {str(e)}")
        return {"events": [], "source": "Error", "last_updated": datetime.utcnow().isoformat()}