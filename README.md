# GeoPV
_A solar potential analyzer for Indian rooftops._

A robust full-stack application that analyzes satellite imagery to detect rooftops and calculate their solar energy generation potential.

---

## Check out the demo
![Demo](Frontend/src/assets/Demo.gif)

## Overview

**GeoPV** uses a YOLO-based machine learning model to automatically identify rooftops from satellite/aerial imagery. The system calculates solar energy generation potential and provides insights like:

- **Total rooftop coverage percentage**
- **Area measurement (in square meters)**
- **Estimated annual energy generation potential**
- **Individual analysis for each detected rooftop**

The backend employs a distributed architecture with a Redis queue system to manage computational workloads efficiently.

---

## Features

- Flexible image input options:
  - Search for a city or use current location to open Google Maps at the correct zoom level (115m)
  - Once Google Maps opens, take a screenshot of the desired area
  - Upload the screenshot directly for analysis
- View results for each detected rooftop along with visualizations
- Polling-based job progress tracker
- Redis queue for sequential request processing
- Modern UI built with React

---

## Installation

### Prerequisites

- Python 3.8+
- Node.js and npm
- Redis server
- CUDA-compatible GPU (recommended)

### Setup

```bash
# Clone the repository
$ git clone https://github.com/GentleClash/GeoPV.git
$ cd GeoPV

# Setup Backend
$ cd Backend

# Create and activate a virtual environment
$ python -m venv venv

# Optional: If using staticMaps branch
$ git checkout staticMaps
# Create .env file with Google Maps API key
$ echo "GOOGLE_MAPS_API_KEY=your_api_key_here" > .env
# Note: API key needs Geocoding API, Maps JavaScript API, and Maps Static API enabled
$ source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
$ pip install -r requirements.txt

# Go back to root directory
$ cd ..

# Setup Frontend
$ cd Frontend
$ npm install

# Go back to root directory for starting services
$ cd ..
```

### Start Redis Server

```bash
# Start Redis server (in a separate terminal)
$ redis-server
```

---

## Usage

### 1. Start the Worker (for ML model processing)

```bash
# From the GeoPV root directory
$ cd Backend
$ source venv/bin/activate  # On Windows: venv\Scripts\activate
$ python worker.py
```

### 2. Start the Flask App (API + Backend)

```bash
# From the GeoPV root directory (in a new terminal)
$ cd Backend
$ source venv/bin/activate  # On Windows: venv\Scripts\activate
$ gunicorn app:app -b 0.0.0:5000 --workers 4
```

### 3. Start the Frontend (React App)

```bash
# From the GeoPV root directory (in a new terminal)
$ cd Frontend
$ npm run dev
```

### Access the Application

Once all services are running:
- Frontend will be available at: `http://localhost:5173` (or the port shown in your terminal)
- Backend API will be available at: `http://localhost:5000`

---

## Tech Stack

- **Frontend**: React, Vite
- **Backend**: Flask (Python)
- **ML Model**: YOLOv12 (custom-trained)
- **Task Queue**: Redis
- **Image Processing**: OpenCV, NumPy

## Authors
- Harsh Anand (@harshrox)
- Ajay Tiwari (@AjaiTiwarii)
- Ayush Bajpai (@GentleClash) 

---

> Contributions are welcome. Star the repo and help promote sustainable tech!