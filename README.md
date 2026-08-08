# 🚨 Crowd Movement Detection & Direction Analysis

> **An intelligent computer-vision system for real-time crowd monitoring, movement analysis, density estimation, and abnormal behavior detection.**

[![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-Frontend-61DAFB?logo=react)](https://react.dev/)
[![YOLOv11](https://img.shields.io/badge/YOLOv11-Object%20Detection-111111)](https://github.com/ultralytics/ultralytics)
[![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-5C3EE8?logo=opencv)](https://opencv.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](#-license)

---

## 📌 Overview

**Crowd Movement Detection & Direction Analysis** is an AI-powered computer vision system designed to automatically monitor and analyze the movement of people in crowded environments.

The system processes **live webcam feeds or recorded videos**, detects individual people, tracks their movement, estimates crowd density, identifies the dominant direction of movement, and generates alerts when potentially abnormal movement patterns are detected.

Instead of relying entirely on manual CCTV monitoring, the system provides an automated analytical layer that can help authorities and security personnel identify potentially dangerous crowd situations more quickly.

---

## 🎯 Problem Statement

Monitoring large crowds through CCTV cameras manually can be difficult, especially in situations involving:

* 🧍 Large numbers of people
* 🚶 Rapid changes in crowd movement
* ⚠️ Overcrowding
* 🔄 Conflicting movement directions
* 🚨 Potential emergency situations

Continuous manual monitoring can also be affected by **human fatigue, limited attention, and delayed response**.

This project aims to address these challenges by using computer vision and automated movement analysis to provide real-time insights into crowd behavior.

---

## ✨ Key Features

### 👤 Person Detection

Detects people in video frames using **YOLOv11**.

### 🎯 Multi-Object Tracking

Uses **ByteTrack**, integrated with Ultralytics, to assign persistent IDs to detected individuals.

### 🧭 Movement Direction Analysis

Calculates movement vectors from tracked trajectories and determines the **dominant direction of crowd movement**.

### 👥 Crowd Density Estimation

Estimates the number of people present in the monitored area and identifies potentially overcrowded regions.

### 🚨 Abnormal Movement Detection

Rule-based analysis identifies potentially unusual situations such as:

* Wrong-way movement
* Sudden movement changes
* Conflicting movement directions
* Overcrowding

### 📊 Real-Time Dashboard

A React-based dashboard provides:

* Live annotated video
* Crowd statistics
* Movement information
* Density information
* Alerts and warnings

### 🎥 Multiple Input Sources

The system supports:

* 📷 Live webcam
* 🎞️ Recorded video
* 📁 Uploaded video files

---

# 🏗️ System Architecture

```text
                 ┌──────────────────────┐
                 │   Video Input        │
                 │                      │
                 │  📷 Webcam           │
                 │  🎞️ Recorded Video   │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │   OpenCV             │
                 │ Frame Acquisition    │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │   YOLOv11            │
                 │ Person Detection     │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │   ByteTrack          │
                 │ Person Tracking      │
                 └──────────┬───────────┘
                            │
                            ▼
              ┌─────────────────────────────┐
              │      Movement Analysis      │
              │                             │
              │ • Movement Vectors         │
              │ • Direction Analysis        │
              │ • Density Estimation        │
              │ • Anomaly Detection         │
              └─────────────┬───────────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │      FastAPI         │
                 │      Backend         │
                 └──────────┬───────────┘
                            │
                  ┌─────────┴─────────┐
                  │                   │
                  ▼                   ▼
           📺 MJPEG Stream      📡 WebSocket
                  │                   │
                  └─────────┬─────────┘
                            ▼
                 ┌──────────────────────┐
                 │   React Dashboard    │
                 │                      │
                 │ 📊 Statistics        │
                 │ 🧭 Direction         │
                 │ 👥 Density           │
                 │ 🚨 Alerts            │
                 └──────────────────────┘
```

---

# 🛠️ Technology Stack

| Component            | Technology         |
| -------------------- | ------------------ |
| Programming Language | Python             |
| Computer Vision      | OpenCV             |
| Object Detection     | YOLOv11            |
| Object Tracking      | ByteTrack          |
| Deep Learning        | PyTorch            |
| Backend              | FastAPI            |
| API Communication    | WebSockets / MJPEG |
| Frontend             | React.js           |
| Build Tool           | Vite               |
| HTTP Client          | Axios              |
| Data Visualization   | Recharts           |
| UI Icons             | Lucide React       |

---

# 📂 Project Structure

```text
Crowd_movement_detection/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── ...
│   │   └── ...
│   │
│   ├── requirements.txt
│   └── ...
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── ...
│
├── videos/
│   └── ...
│
├── datasets/
│   └── ...
│
├── models/
│   └── ...
│
├── .gitignore
└── README.md
```

> **Note:** Large datasets, virtual environments, generated outputs, and model files should generally not be committed directly to GitHub.

---

# ⚙️ Installation

## 1️⃣ Clone the Repository

```bash
git clone https://github.com/Atharva-Tangadi/Crowd_movement_detection.git
cd Crowd_movement_detection
```

---

## 2️⃣ Backend Setup

Navigate to the backend directory:

```bash
cd backend
```

Create a Python virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment.

### Windows

```powershell
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

---

## 3️⃣ Frontend Setup

Open another terminal and navigate to the frontend:

```bash
cd frontend
```

Install the required Node.js packages:

```bash
npm install
```

---

# ▶️ Running the Project

The project requires **two terminals**.

### Terminal 1 — Backend

```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The FastAPI backend will run on:

```text
http://localhost:8000
```

### Terminal 2 — Frontend

```bash
cd frontend
npm run dev
```

Open the URL provided by Vite, usually:

```text
http://localhost:5173
```

---

# 🎥 Using the Application

Once the dashboard is running:

### 📷 Webcam

Click **Start Camera** to begin processing your default webcam feed.

### 🎞️ Recorded Video

Click **Upload Video** and select a supported video file such as:

```text
.mp4
.avi
```

The backend will process the video and stream the annotated results to the dashboard.

### ⏹️ Stop Processing

Click **Stop Processing** to stop the active video-processing pipeline.

---

# 🤖 YOLOv11 Model

The project uses:

```text
yolo11n.pt
```

as the default YOLOv11 model.

When running the backend for the first time, **Ultralytics can automatically download the required model**.

> ⚠️ If the project needs to operate in a completely offline environment, download the model beforehand and place it in the appropriate `models/` directory.

---

# ⚙️ Configuration

Important analysis parameters can be configured from:

```text
backend/app/config.py
```

Examples include:

```text
Confidence Threshold
Movement Threshold
Alert Sensitivity
Density Threshold
```

These parameters can be adjusted depending on the camera environment and crowd conditions.

---

# 🧠 How the Analysis Works

The system follows a simple processing pipeline:

```text
Video Frame
     ↓
Person Detection
     ↓
Person Tracking
     ↓
Track History
     ↓
Movement Vector Calculation
     ↓
Direction Analysis
     ↓
Crowd Density Estimation
     ↓
Abnormal Movement Detection
     ↓
Dashboard + Alerts
```

### Movement Vector

For each tracked person, the system compares their current position with their previous position:

```text
Previous Position ─────────► Current Position
                    Movement
                     Vector
```

The collection of individual movement vectors is then used to estimate the **dominant crowd direction**.

---

# 🚨 Abnormal Movement Detection

The current system uses **rule-based analysis** to identify potentially abnormal situations.

Examples include:

| Condition                                    | Possible Alert                 |
| -------------------------------------------- | ------------------------------ |
| High number of people                        | ⚠️ Overcrowding                |
| Person moving opposite to dominant direction | 🔄 Wrong-way movement          |
| Multiple conflicting directions              | ⚠️ Irregular movement          |
| Sudden movement changes                      | 🚨 Potential abnormal activity |

> **Important:** These alerts are indicators of potentially unusual behavior and should not be interpreted as definitive predictions of panic or emergencies.

---

# 📊 Dashboard

The dashboard is designed to provide a centralized view of the current crowd situation.

It can display:

* 👥 Current people count
* 🧭 Dominant movement direction
* 📈 Crowd density
* 🚨 Active alerts
* 🎥 Annotated video stream
* 📡 Real-time telemetry

---

# ⚠️ Limitations

Although the system provides automated crowd analysis, several limitations remain:

### 1. Heavy Occlusion

Extremely dense crowds can make individual people difficult to detect and track accurately.

### 2. Camera Movement

Rapid camera movement can negatively affect movement-vector calculations.

### 3. Rule-Based Anomaly Detection

The current abnormal behavior detection system uses predefined rules rather than a dedicated machine-learning anomaly detection model.

Therefore, alerts should be treated as **risk indicators rather than definitive conclusions**.

### 4. Environmental Conditions

Lighting, camera angle, video quality, and scene complexity can influence detection and tracking performance.

---

# 🚀 Future Enhancements

Several improvements can be added in future versions:

* 🔮 Machine-learning-based trajectory prediction
* 📹 Multi-camera tracking
* 🧠 Advanced crowd behavior recognition
* 📈 Historical crowd analytics
* 🗺️ Crowd heatmap generation
* 🚨 Improved emergency detection
* 🔔 SMS / Email / Notification-based alerts
* 🏢 Integration with existing Video Management Systems (VMS)
* ☁️ Cloud-based deployment
* 📱 Mobile monitoring application

---

# 🎯 Applications

The system can potentially be adapted for:

* 🏟️ Stadiums
* 🚉 Railway stations
* 🛕 Religious gatherings
* 🎪 Festivals and events
* 🏫 College campuses
* 🛍️ Shopping malls
* 🚨 Emergency evacuation monitoring
* 🏛️ Public spaces

---

# 🔐 Privacy & Responsible Use

This project is intended for **crowd movement analysis and safety monitoring**.

The system focuses on detecting and tracking people for movement analysis rather than identifying individuals.

For real-world deployment, appropriate privacy, security, data-retention, and legal requirements should be considered.

---

# 👨‍💻 Author

**Atharva Tangadi**

B.Tech Information Technology
Walchand College of Engineering, Sangli

---

# ⭐ Support

If you find this project useful or interesting, consider giving the repository a ⭐ on GitHub!

Your feedback and suggestions are always welcome. 🚀

---

