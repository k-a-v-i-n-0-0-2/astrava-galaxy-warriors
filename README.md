# 🎭 Instagram AI Deepfake Detector 🔍
### Hackathon Submission Project

A full-stack AI system that detects **deepfake videos, AI-generated media, and coordinated bot amplification campaigns** on social media using behavioral analytics and machine learning.

---

## 🧩 Problem Statement

Social media platforms face a rapid rise in:

- AI-generated deepfake videos  
- Synthetic influencer content  
- Coordinated bot amplification  
- Fake advertisements & scam campaigns  

These threats manipulate public opinion, spread misinformation, and damage platform trust.

Current detection systems focus mainly on **pixel-level media forensics**, ignoring behavioral interaction signals.

---

## 💡 Our Solution

We built an AI-powered detection platform that combines:

- Behavioral interaction analytics  
- Graph network analysis  
- Entropy & synchronization modeling  
- AI content risk scoring  

All integrated into a **fully functional Instagram-style interface** for real-world simulation and analysis.

---

## 🚀 Key Innovations

- Detects deepfakes without requiring raw video training datasets  
- Uses behavioral signals instead of visual artifacts  
- Identifies coordinated amplification campaigns  
- Works across reels, posts, and advertisements  
- Provides explainable AI detection signals  

---

## 🧠 Detection Methodology

Our engine analyzes **6 behavioral signals**:

1. **Spread Speed Analysis**  
   Detects abnormally rapid engagement spikes  

2. **Early Burst Detection**  
   Flags concentrated interactions immediately after posting  

3. **Synchronization Analysis**  
   Finds coordinated actions within 2-second windows  

4. **User Diversity Score**  
   Measures ratio of unique users vs interactions  

5. **Behavioral Entropy**  
   Evaluates randomness in engagement timing  

6. **Graph Clustering**  
   Detects densely connected bot networks  

---

## 📊 Confidence Scoring Model

| Score Range | Classification |
|------------|----------------|
| 92%+ | AI-Generated · High Confidence |
| 85%+ | AI-Generated · High Confidence |
| 78%+ | Medium Confidence |
| 55%+ | Low Confidence |
| <35% | Likely Human Content |

---

## 📱 Application Modules

### 🏠 Home Feed
- Instagram-style posts  
- AI authenticity analysis  
- Engagement trust score  

### 🎬 Reels Detector
- Vertical reels viewer  
- Deepfake probability scoring  
- Amplification risk indicators  

### 📢 Ad Detector
- Fake advertisement detection  
- Scam probability scoring  
- AI branding analysis  

### 📊 Analytics Dashboard
- Engagement spike graphs  
- Bot cluster distribution  
- Coordination heatmaps  
- Hashtag spam tracking  

### 👤 Profile Risk View
- User authenticity score  
- Content risk summary  

---

## 🛠️ Tech Stack

### Frontend
- React.js (JavaScript)  
- React Router DOM  
- Bootstrap 5  
- Recharts  
- CSS3  

### Backend
- Flask (Python)  
- Pandas  
- NumPy  
- NetworkX  
- SciPy  

### AI Integration
- Google Gemini API (Insight augmentation)

---

## 🏗️ System Architecture

User Interaction Data
↓
Feature Extraction Engine
↓
Behavioral Signal Analysis
↓
Graph Network Modeling
↓
Entropy & Synchronization Metrics
↓
AI Risk Scoring Engine
↓
Frontend Visualization Dashboard


---

## 🚀 Installation & Setup

### 1️⃣ Clone Repository

```bash
git clone https://github.com/yourusername/instagram-ai-deepfake-detector.git
cd instagram-ai-deepfake-detector
2️⃣ Frontend Setup
cd my-app
npm install
npm install react-router-dom bootstrap react-icons recharts
npm start
Frontend runs on:
http://localhost:3000

3️⃣ Backend Setup
cd backend

python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt

python app.py
Backend runs on:
http://localhost:5000/api

🔐 Demo Credentials
Username: demo_user
Password: any
📁 Project Structure
instagram-ai-deepfake-detector/
│
├── my-app/        → React Frontend
├── backend/       → Flask Detection Engine
├── analytics/     → Graph & Signal Analysis
└── README.md
📈 Impact & Use Cases
Social media moderation

Election misinformation detection

Influencer authenticity verification

Scam advertisement detection

Brand safety monitoring

🔮 Future Enhancements
Real-time live stream detection

Cross-platform monitoring

Mobile app deployment

Advanced video transformer models

Law-enforcement dashboards

