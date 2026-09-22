# Kabadiwala Connect

An application bridging the gap between informal e-waste collectors and formal recycling facilities.

## Features
- **Collector Dashboard:** Register e-waste lots with photos, weight, and condition.
- **Instant Price Estimation:** Real-time calculation of estimated value based on current material prices.
- **Recycler Matching:** Connect with verified recyclers nearby.
- **Offer System:** Recyclers can bid on available lots with optional pickup.
- **Digital Handover & Traceability:** Track the complete transaction from pickup to final recycling via a visual timeline.
- **Analytics:** Admin dashboard with system health metrics and charts.

## Technologies Used
- **Backend:** Python, Flask, Flask-SQLAlchemy, Flask-Login
- **Database:** SQLite
- **Frontend:** HTML5, CSS3, Vanilla JavaScript, Bootstrap 5, Chart.js
- **Styling:** Glassmorphism and light pastel themes.

## Installation & Setup

1. **Activate the Virtual Environment** (Windows):
   ```bash
   venv\Scripts\activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Seed the Database** (Run once to create demo accounts and data):
   ```bash
   python seed.py
   ```

4. **Run the Application**:
   ```bash
   python app.py
   ```

5. **Access the App**:
   Open a browser and navigate to `http://127.0.0.1:5000`

## Demo Accounts
- **Collector:** `collector@example.com` / `Collector@123`
- **Recycler:** `recycler@example.com` / `Recycler@123`
- **Admin:** `admin@example.com` / `Admin@123`
