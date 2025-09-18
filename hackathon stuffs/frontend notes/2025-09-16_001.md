# Food Rescue Matchmaker - 24H Hackathon Plan

## 🎯 Problem Statement
**Food waste meets food insecurity** - Connect restaurants/cafes with surplus food to NGOs/volunteers for redistribution.

## 🏗️ Architecture Overview

### Backend: Python FastAPI
```
food-rescue-backend/
├── app/
│   ├── main.py              # FastAPI app entry
│   ├── models.py            # SQLAlchemy models
│   ├── database.py          # DB connection
│   ├── schemas.py           # Pydantic models
│   ├── crud.py              # Database operations
│   └── websocket.py         # Real-time updates
├── uploads/                 # Photo storage
├── requirements.txt
└── .env
```

### Frontend: React + TypeScript
```
food-rescue-frontend/
├── src/
│   ├── components/
│   │   ├── DonorDashboard.tsx    # Post donations
│   │   ├── NGODashboard.tsx      # Accept/track
│   │   ├── ImpactDashboard.tsx   # Charts & metrics
│   │   └── PhotoUpload.tsx       # Camera/upload
│   ├── hooks/
│   │   ├── useWebSocket.ts       # Real-time
│   │   └── useGeolocation.ts     # GPS
│   ├── services/
│   │   └── api.ts                # Backend calls
│   └── App.tsx
└── package.json
```

## 🚀 Core Features (MVP)

### 1. Donation Flow
- **Donor**: Post surplus food with photo + GPS location
- **NGO**: View available donations on map/list
- **NGO**: Accept donation (status: pending → accepted)
- **NGO**: Update pickup status (accepted → picked up → delivered)

### 2. Real-time Updates
- WebSocket for live donation status changes
- Push notifications for new donations
- Live tracking of pickup progress

### 3. Impact Dashboard
- **Metrics**: Meals saved, daily beneficiaries, waste prevented
- **Charts**: Bar chart (daily donations), Pie chart (food types), Line chart (weekly trends)
- **NGO Impact**: Individual NGO statistics

## 📊 Database Schema (SQLite for speed)

```sql
-- Donations table
CREATE TABLE donations (
    id INTEGER PRIMARY KEY,
    restaurant_name VARCHAR(100),
    food_description TEXT,
    quantity INTEGER,
    photo_url VARCHAR(255),
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    status ENUM('available', 'accepted', 'picked_up', 'delivered'),
    created_at TIMESTAMP,
    expires_at TIMESTAMP
);

-- NGOs table
CREATE TABLE ngos (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    contact_phone VARCHAR(20),
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8)
);

-- Pickups table
CREATE TABLE pickups (
    id INTEGER PRIMARY KEY,
    donation_id INTEGER,
    ngo_id INTEGER,
    pickup_time TIMESTAMP,
    delivery_time TIMESTAMP,
    beneficiaries_count INTEGER,
    FOREIGN KEY (donation_id) REFERENCES donations(id),
    FOREIGN KEY (ngo_id) REFERENCES ngos(id)
);
```

## 🔧 Tech Stack

### Backend
- **FastAPI** - Fast API development
- **SQLAlchemy** - ORM for database
- **SQLite** - Quick database setup
- **WebSockets** - Real-time updates
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server

### Frontend
- **React 18** - Component-based UI
- **TypeScript** - Type safety
- **Chart.js** - Impact charts
- **WebSocket API** - Real-time updates
- **Browser Geolocation** - GPS coordinates
- **File API** - Photo uploads

## ⏱️ 24-Hour Timeline

### Phase 1: Backend Foundation (2 hours)
- [ ] FastAPI setup with CORS
- [ ] SQLite database + models
- [ ] Basic CRUD endpoints
- [ ] Photo upload endpoint

### Phase 2: Frontend Core (3 hours)
- [ ] React app setup
- [ ] Donor dashboard (post donations)
- [ ] NGO dashboard (view/accept)
- [ ] Basic routing between views

### Phase 3: Real-time Features (2 hours)
- [ ] WebSocket implementation
- [ ] Live donation updates
- [ ] Status change notifications

### Phase 4: GPS & Photos (2 hours)
- [ ] Geolocation API integration
- [ ] Photo upload with preview
- [ ] Map view for donations

### Phase 5: Impact Dashboard (2 hours)
- [ ] Chart.js integration
- [ ] Metrics calculation
- [ ] Dashboard visualizations

### Phase 6: Testing & Polish (1 hour)
- [ ] End-to-end testing
- [ ] Bug fixes
- [ ] UI improvements

### Phase 7: Deployment (1 hour)
- [ ] Backend: Railway/Heroku
- [ ] Frontend: Vercel/Netlify
- [ ] Demo preparation

## 🎪 Demo Flow

1. **Restaurant** posts surplus food with photo and location
2. **NGO** sees new donation notification in real-time
3. **NGO** accepts donation, status updates live
4. **NGO** tracks pickup progress (accepted → picked up → delivered)
5. **Impact dashboard** shows updated metrics and beneficiaries count
6. **Charts** display daily/weekly food rescue statistics

## 🔥 Competitive Advantages

1. **Real-time coordination** - Instant updates reduce food waste
2. **GPS integration** - Location-based matching efficiency
3. **Impact visualization** - Clear metrics motivate participation
4. **Simple UX** - Quick posting and acceptance flow
5. **Mobile-first** - Works on any device with camera/GPS

## 🚨 Risk Mitigation

- **SQLite** over PostgreSQL for zero setup time
- **Local file storage** over cloud storage initially
- **Minimal styling** - Focus on functionality
- **Pre-built UI components** for speed
- **Simple authentication** (just names, no complex auth)

## 📱 Mobile Features

- **Camera access** for food photos
- **GPS location** for automatic coordinates
- **Push notifications** (web notifications)
- **Responsive design** for mobile screens
- **Touch-friendly** buttons and forms

---

**Total Estimated Time: 13 hours** (with 11 hours buffer for debugging, testing, and presentation prep)

**Success Criteria**: Working donation flow from post → accept → pickup → impact dashboard with real-time updates.