# 🇮🇳 JanSankalpAI

> **AI-powered Civic Complaint Management Platform**

## 🌐 Live Demo

🔗 https://jansankalpai.onrender.com

JanSankalpAI is an AI-powered civic grievance platform designed to bridge the gap between citizens and government authorities. It enables users to report public issues through **text, images, or voice**, while AI automatically analyzes, categorizes, and prioritizes complaints to help departments respond more efficiently.

---

## 🚀 Why JanSankalpAI?

Citizens often struggle to report civic problems such as potholes, garbage accumulation, water leakage, broken streetlights, and sanitation issues. Existing systems can be difficult to use and lack transparency.

JanSankalpAI simplifies this process by providing a centralized platform where:

* Citizens can easily submit complaints.
* AI processes and validates reports.
* Government departments receive categorized complaints.
* Citizens can track complaint progress.

---

## ✨ Features

### 👥 Citizen Portal

* User Registration & Login
* Email OTP Verification
* Password Reset
* Submit Complaints

  * 📝 Text
  * 📷 Image
  * 🎤 Voice Recording
* Live Complaint Status Tracking
* Follow Complaints
* Comment on Public Complaints
* Public Dashboard

### 🤖 AI Features

* AI Complaint Analysis
* Complaint Categorization
* Severity Detection
* Department Recommendation
* AI-generated Complaint Summary
* Voice-to-Text Processing
* Image Understanding using Gemini AI

### 🏛 Government Dashboard

* Complaint Management
* Filter by Department
* Search & Analytics
* Complaint Verification
* Status Updates
* Government-only Complaint View

---

# 🛠 Tech Stack

### Backend

* Python
* Django
* Django REST Framework

### Database

* PostgreSQL

### Background Tasks

* Celery
* Redis

### AI

* Google Gemini API

### Cloud

* Cloudinary
* Render

### Authentication

* Email OTP
* Brevo SMTP

### Deployment

* Docker
* Docker Compose

---

# 📂 Project Structure

```text
JanSankalpAI/
│
├── accounts/
├── complaints/
├── api/
├── dashboard/
├── config/
├── templates/
├── static/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── manage.py
```

---

# ⚙️ Installation

Clone the repository

```bash
git clone https://github.com/yourusername/JanSankalpAI.git
cd JanSankalpAI
```

Create a virtual environment

```bash
python -m venv venv
```

Activate the environment

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Create a `.env` file and configure:

```env
SECRET_KEY=
DATABASE_URL=
REDIS_URL=
GEMINI_API_KEY=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
CLOUDINARY_URL=
```

Run migrations

```bash
python manage.py migrate
```

Start the development server

```bash
python manage.py runserver
```

---

# 🐳 Docker

Build and run the application

```bash
docker compose up --build
```

---

# 🌐 Deployment

The project is deployed using:

* Render
* PostgreSQL
* Redis
* Cloudinary
* Brevo SMTP

---

# 📸 Screenshots

* Home Page
* Complaint Submission
* AI Analysis
* Public Dashboard
* Government Dashboard

---

# 🚀 Future Improvements

* Mobile Application
* Multi-language Support
* Real-time Notifications
* GIS Heatmaps
* Duplicate Complaint Detection
* Advanced Analytics Dashboard
* Government API Integration

---

# 🤝 Contributing

Contributions are welcome! Feel free to fork the repository, create a feature branch, and submit a pull request.

---

# 📄 License

This project is licensed under the MIT License.

---

## 👨‍💻 Author

**Amit**

If you found this project interesting, consider giving it a ⭐ on GitHub!
