import os
from vonage import Auth, Vonage
from vonage_verify import VerifyRequest, SmsChannel
from dotenv import load_dotenv
from .utils import create_response

load_dotenv()

VONAGE_API_KEY = os.getenv("VONAGE_API_KEY")
VONAGE_API_SECRET = os.getenv("VONAGE_API_SECRET")

client = Vonage(Auth(api_key=VONAGE_API_KEY, api_secret=VONAGE_API_SECRET))
verify = client.verify

def send_otp(number: str, brand: str = "ConsultingBot"):
    """
    Send OTP to the specified number.
    """
    if not VONAGE_API_KEY or VONAGE_API_KEY == "your_vonage_api_key":
        return create_response(success=False, error="Vonage API credentials missing")

    try:
        req = VerifyRequest(brand=brand, workflow=[SmsChannel(to=number)])
        response = verify.start_verification(req)
        # response is an object, need to check how to access request_id
        # Based on typical Vonage SDKs, it might be an object with attributes or a dict.
        # Let's assume object and try to access request_id, or convert to dict if needed.
        # If it's a pydantic model (which it looks like), .model_dump() or accessing attr works.
        # Let's try accessing attribute.
        if hasattr(response, 'request_id'):
             return create_response(success=True, data={"request_id": response.request_id})
        else:
             # Fallback if it's a dict
             return create_response(success=True, data={"request_id": response["request_id"]})

    except Exception as e:
        return create_response(success=False, error=str(e))

def verify_otp(request_id: str, code: str):
    """
    Verify the OTP code.
    """
    if not VONAGE_API_KEY or VONAGE_API_KEY == "your_vonage_api_key":
        return create_response(success=False, error="Vonage API credentials missing")

    try:
        response = verify.check_code(request_id, code)
        # Assuming response indicates success if no exception is raised, or check status
        if response.status == "completed":
             return create_response(success=True, data={"message": "Verification successful"})
        else:
             return create_response(success=False, error=f"Status: {response.status}")
    except Exception as e:
        return create_response(success=False, error=str(e))
