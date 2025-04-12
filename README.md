<p align="center">
  # GeoPV  
  _A solar potential analyzer for Indian rooftops._
</p>

A robust full-stack application that analyzes satellite imagery to detect rooftops and calculate their solar energy generation potential.

---

## Overview

**Rooftop Solar Analyzer** uses a YOLO-based machine learning model to automatically identify rooftops from satellite/aerial imagery. The system calculates solar energy generation potential and provides insights like:

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
- Redis server
- CUDA-compatible GPU (recommended)

### Setup

```bash
# Clone the repository
$ git clone https://github.com/harshrox/GeoPV.git
$ cd GeoPV
$ cd Backend

# Create and activate a virtual environment
$ python -m venv venv
$ source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
$ pip install -r requirements.txt

# Start Redis server
$ redis-server
```

---

## Usage

### Start the Worker (for ML model processing)

```bash
$ python worker.py
```

### Start the Flask App (API + Backend)

```bash
$ python app.py
```

### Start the Frontend (React App)

```bash
$ cd GeoPV/Frontend
$ npm install
$ npm run dev
```

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

