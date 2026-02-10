# Deployment Guide

## Option 1: Railway (Recommended)

### Prerequisites
- Railway account (https://railway.app)
- GitHub repository

### Steps

1. **Install Railway CLI**
```bash
npm i -g @railway/cli
```

2. **Login**
```bash
railway login
railway link
```

3. **Initialize Project**
```bash
railway init
```

4. **Add Environment Variables**
Go to Railway dashboard → Variables:
- `GEMINI_API_KEY`
- `GOOGLE_CREDENTIALS_PATH` (paste JSON content)
- `PILOT_ROSTER_SHEET_ID`
- `DRONE_FLEET_SHEET_ID`
- `MISSIONS_SHEET_ID`
- `PORT` = 5000

5. **Deploy**
```bash
railway up
```

6. **Get Public URL**
```bash
railway domain
```

---

## Option 2: Replit

### Steps

1. Import: Click "Create" → "Import from GitHub".
2. Secrets: Go to the Secrets Tool (Padlock icon).
3. Crucial: Replit's "Secrets" are now integrated with their Deployments tab. Ensure your GOOGLE_CREDENTIALS JSON is escaped properly if pasted as a single line.
4. Nix Config: Replit now uses .replit files to detect Flask/Vite projects. Ensure your run command is set to python backend/app.py.
5. Deploy: Use the Deploy button (top right) to get a permanent URL

---

## Option 3: Manual Deployment (VPS)

### Prerequisites

1. **Clone Repository**
```bash
git clone https://github.com/dishaskotian/drone-ops-coordinator.git
cd drone-ops-coordinator
```

2. **Setup Backend**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

4. **Setup Frontend**
```bash
cd ../frontend
npm install
npm run build
```

5. **Configure Nginx**
```bash
sudo nano /etc/nginx/sites-available/drone-ops
```

Add:
```nginx
server {
    listen 80;
    server_name drone-coordinator.yourdomain.com;

    # 1. Frontend (Vite Build)
    location / {
        root /var/www/drone-ops/frontend/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # 2. Backend API (Flask)
    location /api {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

6. **Start Services**
```bash
# Backend
cd backend
python app.py &

# Frontend
cd frontend
npm run dev