# Yogonet News Scraper

A Python-based web scraping application that extracts news articles from Yogonet, processes the data using pandas, and uploads it to Google BigQuery. The application is containerized and deployed as a job on Google Cloud Run.

## Features

- Automated web scraping of Yogonet news articles
- Headless Firefox browser automation using Selenium
- HTML parsing with BeautifulSoup4
- Data processing with pandas
- Google Cloud Natural Language API integration
- BigQuery data upload functionality
- Docker containerization support

## Prerequisites

- Python 3.11
- Docker
- Google Cloud SDK
- Google Cloud credentials

## Installation

1. Clone the repository:
```bash
git clone https://github.com/samusoler22/challenge
cd challenge
```

2. Set up Google Cloud credentials:
- Place your Google Cloud service account JSON key inside challenge `Folder` with file name `gc_user.json`
- Ensure you have the necessary permissions for BigQuery and Natural Language API

## Local Usage

1. Run the scraper:
```bash
python scrapper.py
```

The scraper will:
- Fetch news articles from Yogonet
- Process and analyze the content
- Upload the results to BigQuery

## Docker Support

The application is containerized using Docker for consistent deployment and execution. The Dockerfile:
- Uses Python 3.11 slim-buster as the base image
- Installs Firefox ESR and Geckodriver
- Sets up all necessary dependencies
- Configures Google Cloud credentials

Build the Docker image locally:
```bash
docker build -t challenge-image .
docker run challenge-image
```

## Cloud Deployment

The project is designed to run as a job on Google Cloud Run. The deployment process is automated using `deploy.sh`, which:

1. Sets up Google Cloud environment:
   - Enables required services (Artifact Registry, Cloud Run, IAM)
   - Configures Docker authentication
   - Creates an Artifact Registry repository if it doesnt exist

2. Builds and pushes the Docker image:
   - Builds the container image
   - Pushes it to Google Artifact Registry

3. Deploys to Cloud Run:
   - Creates/updates a Cloud Run job
   - Configures job settings (memory, timeout, retries)
   - Sets up service account permissions

To deploy to Google Cloud Run:

1. Run the deployment script:
```bash
chmod +x deploy.sh
./deploy.sh
```

The script will:
- Build and push the Docker image
- Create a Cloud Run job
- Execute the job automatically

Job Configuration:
- Memory: 2GB
- Timeout: 1200 seconds
- Max retries: 3
- Region: us-central1

## Project Structure

- `scrapper.py`: Main application file containing the YogonetScrapper class
- `requirements.txt`: Python dependencies
- `Dockerfile`: Docker configuration
- `deploy.sh`: Deployment script
- `gc_user.json`: Google Cloud credentials file
- `.gitignore`: Git ignore configuration

## Configuration

The scraper is configured to use:
- Firefox ESR browser in headless mode
- Geckodriver for browser automation
- Google Cloud services for natural language processing and data storage 

SAMUEL SOLER 