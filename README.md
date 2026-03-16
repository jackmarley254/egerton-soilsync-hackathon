# 🌱 SoilSync AI 

**Empowering smallholder farmers with AI-driven, location-specific fertilizer recommendations.**

*Built for the Soil Health Deep Dive Hackathon at Egerton University.*

## 📖 The Problem
Smallholder farmers often lack access to affordable, accurate soil testing. Without knowing their soil's specific pH and nutrient levels, fertilizer application is a guessing game, leading to poor yields and environmental degradation.

## 🚀 Our Solution
SoilSync AI bridges the gap by combining live satellite soil data (SoilGrids), climate insights, and Machine Learning to deliver simple, actionable fertilizer recommendations directly to the farmer. 

## 🛠 Tech Stack
* **Backend:** Python, Django, Django REST Framework (DRF)
* **Database:** PostgreSQL / SQLite (for local MVP)
* **Machine Learning:** Scikit-learn (Random Forest Classifier)
* **External APIs:** SoilGrids REST API, OpenWeatherMap (Agro)
* **Frontend:** (To be added - Mobile-responsive Web App)

## 👥 The Team
1. **Backend/Systems Dev:** Architecture, APIs, and Database Routing
2. **Frontend Dev:** UI/UX implementation and user flows
3. **Data/AI Specialist:** Data pipeline and Random Forest training
4. **Agronomist/Domain Expert:** Scientific validation of recommendations
5. **UI/UX Designer:** Prototyping and user journey mapping
6. **Product Manager:** Business logic and pitch delivery

---

## 💻 Local Setup Instructions

Follow these steps to get the backend running on your local machine for prototyping.

### 1. Clone the Repository
```bash
git clone [https://github.com/our-team/soilsync-ai.git](https://github.com/our-team/soilsync-ai.git)
cd soilsync-ai
```
### 2. Set Up a Virtual Environment
It is highly recommended to use a virtual environment to manage dependencies.

```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```
### 3. Install Dependencies
```bash
pip install -r requirements.txt
```
### 4. Train the AI Model
Before running the server, you must generate the Machine Learning model file (soilsync_model.joblib).
```bash
python train_model.py
```
### 5. Setup the Database
Run the standard Django migrations to build the local database schema.
```bash
python manage.py makemigrations
python manage.py migrate
```
### 6. Run the Development Server
```bash
python manage.py runserver
**The API will now be available at http://127.0.0.1:8000/api/v1/recommendation/.**

```
* Built with ☕ and 💻 in Nakuru County.