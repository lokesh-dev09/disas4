# disas4

## Project Description
Disas4 is a disaster management and alert system designed to track and manage natural disasters such as wildfires, floods, earthquakes, and tsunamis. It provides real-time data visualization, alerts, and risk assessments to help users stay informed and prepared.

## Features
- Real-time disaster tracking using NASA's EONET API.
- Interactive map for visualizing disaster locations.
- Alerts and notifications for active disasters.
- Risk assessment for high-risk areas.
- Data visualization and statistics.

## Installation
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd disas4
   ```
2. Install dependencies:
   ```bash
   pip install .
   ```

## Usage
1. Start the application:
   ```bash
   python3 main.py --port 5000
   ```
2. Open your browser and navigate to `http://localhost:5000`.

## Project Structure
- `app.py`: Application initialization.
- `routes.py`: Defines the application routes.
- `data_collection.py`: Handles data fetching from external APIs.
- `ml_model.py`: Machine learning models for risk assessment.
- `models.py`: Database models.
- `templates/`: HTML templates for the web interface.
- `static/`: Static assets like CSS, JavaScript, and images.

## License
This project is licensed under the MIT License.
