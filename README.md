# Consulting Bot Backend

This is a production-ready FastAPI backend for a Consulting Services chatbot. It integrates with Zoho SalesIQ, Google Calendar, Gmail, and Vonage.

## Prerequisites

- Python 3.8+
- Valid Google Cloud Console credentials (client ID, secret) with Calendar and Gmail scopes enabled.
- Valid Vonage API credentials (key, secret) for SMS/OTP.

## Setup

1.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure environment variables:**
    Copy `.env.sample` to `.env` and fill in the **required** values.
    > **Note:** The application will fail to start or execute specific functions if valid credentials are not provided.

3.  **Run the application:**
    ```bash
    uvicorn app.main:app --reload
    ```

## API Endpoints

-   **Chat**: `/chat` (Interact with the bot using natural language)
-   **Auth**: `/auth/init`, `/auth/callback`
-   **OTP**: `/otp/send`, `/otp/verify`
-   **Slots**: `/slots/get`
-   **Appointments**: `/appointment/create`, `/appointment/list`, `/appointment/update`, `/appointment/cancel`
-   **Email**: `/email/send-confirmation`

## Database

The project uses SQLAlchemy. By default, it uses SQLite (`consulting_bot.db`).
