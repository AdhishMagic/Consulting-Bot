# 🚀 Consulting Services Bot – Backend (FastAPI + Google Calendar + Vonage + Razorpay + SalesIQ)

This is a production-ready FastAPI backend for a Consulting / Appointment Booking Chatbot.
It integrates with:

- **Zoho SalesIQ** (chatbot frontend)
- **Google Calendar API** (appointments)
- **Gmail API** (email confirmations)
- **Vonage Verify API** (OTP)
- **Razorpay Payments** (test/live mode supported)

This backend powers booking, rescheduling, cancellation, OTP, email alerts, and payment processing for any consulting-related service (hospital, showroom, coaching, legal, etc.).

## 📌 Features

### ✅ Appointment Booking
- Free/busy lookup from Google Calendar
- Slot generation (30-minute blocks)
- Create events in Google Calendar
- Store booking in local DB

### ✅ OTP Verification (Vonage)
- Send verification code
- Validate code
- Prevents spam/fake users

### ✅ Email Confirmation (Gmail API)
- Sends confirmation email upon successful booking/payment

### ✅ Payments (Razorpay)
- Create payment order
- Generate payment link
- Webhook for payment success/failure
- Update booking status

### ✅ SalesIQ Chatbot Integration
- Supports API Plug consumption
- JSON responses optimized for Zoho SalesIQ

## 📁 Tech Stack

| Component | Technology |
| :--- | :--- |
| **Backend Framework** | FastAPI |
| **Language** | Python 3.8+ |
| **Database** | SQLite (default) or PostgreSQL |
| **Authentication** | Google OAuth 2.0 |
| **OTP** | Vonage Verify API |
| **Email** | Gmail API |
| **Payments** | Razorpay API |
| **Deployment** | Uvicorn / Docker / Cloud Run / Railway |

## ⚙️ Prerequisites

Before running this backend, ensure you have:

- [x] **Python 3.8+**
- [x] **Google API Credentials (OAuth 2.0)**
    - Google Calendar API
    - Gmail API
    - OAuth Consent Screen configured
- [x] **Vonage Credentials**
    - `VONAGE_API_KEY`
    - `VONAGE_API_SECRET`
- [x] **Razorpay Credentials**
    - `RAZORPAY_KEY_ID`
    - `RAZORPAY_KEY_SECRET`
    - `RAZORPAY_WEBHOOK_SECRET`

## 📦 Installation

### 1️⃣ Clone the Repository
```bash
git clone <your_repo_url>
cd consulting_bot_backend
```

### 2️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 3️⃣ Configure Environment Variables

Duplicate `.env.sample`:
```bash
cp .env.sample .env
```

Fill fields:
```ini
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback
GOOGLE_REFRESH_TOKEN=

VONAGE_API_KEY=
VONAGE_API_SECRET=

RAZORPAY_KEY_ID=
RAZORPAY_KEY_SECRET=
RAZORPAY_WEBHOOK_SECRET=

DATABASE_URL=sqlite:///./consulting_bot.db
SECRET_KEY=some_random_string
```

### 4️⃣ Run the Server
```bash
uvicorn app.main:app --reload
```

### 5️⃣ Open API Docs
Go to:
👉 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## 🧭 API Endpoints

### 🔐 Auth
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/auth/init` | Generate Google OAuth URL |
| `GET` | `/auth/callback` | Google OAuth redirect handler |

### 📱 OTP (Vonage)
| Method | Endpoint |
| :--- | :--- |
| `POST` | `/otp/send` |
| `POST` | `/otp/verify` |

### 📅 Slots & Appointment Management
| Method | Endpoint |
| :--- | :--- |
| `POST` | `/slots/get` |
| `POST` | `/appointment/create` |
| `POST` | `/appointment/list` |
| `POST` | `/appointment/update` |
| `POST` | `/appointment/cancel` |

### ✉️ Email
| Method | Endpoint |
| :--- | :--- |
| `POST` | `/email/send-confirmation` |

### 💳 Payment (Razorpay)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/payment/create-order` | Creates Razorpay order & payment link |
| `POST` | `/payment/verify` | Verify signature received from client |
| `POST` | `/payment/webhook` | Razorpay webhook listener |

## 🤖 Zoho SalesIQ Bot Integration

### 1️⃣ Create Order via API Plug

**URL**: `https://your-domain.com/payment/create-order`
**Method**: `POST`

**Request Body**:
```json
{
  "amount": 500,
  "currency": "INR",
  "user_id": 123,
  "booking_id": 456
}
```

**Expected Response (SalesIQ-friendly)**:
```json
{
  "success": true,
  "data": {
    "order_id": "order_ABC123",
    "payment_link": "https://rzp.io/i/example",
    "amount": 500
  }
}
```

### 2️⃣ Bot UI Example
1.  Bot shows carousel → user selects service
2.  User enters details → OTP verified
3.  Slot selected → `/payment/create-order` called
4.  Bot displays “Click to Pay” button
5.  Payment completion triggers webhook
6.  Booking becomes `confirmed_paid`

## 🗃️ Database Schema

Tables include:
- `users`
- `bookings`
- `payments`
- `oauth_tokens`
- `otps`

Default DB: `sqlite:///./consulting_bot.db`

## 🧪 Testing Instructions

### ✔ Test Razorpay in Test Mode
- No charges
- No KYC required

### ✔ Test OTP
- Use real phone OR implement mock mode for development.

### ✔ Use Swagger UI
[http://localhost:8000/docs](http://localhost:8000/docs)

## 🚀 Deployment

Recommended hosting:
- Railway
- Render
- Google Cloud Run
- Fly.io
- Docker

**Production Command**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 🙌 Contributing
Pull requests and feature suggestions are welcome!
