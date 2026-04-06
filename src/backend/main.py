import os
from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Load cấu hình từ .env
load_dotenv()
USER_B = os.getenv('USER_B_EMAIL')
SCOPES = ['https://www.googleapis.com/auth/calendar']

app = FastAPI(title="Calendar Booking Agent (OAuth Edition)")


# Schema dữ liệu cho Request
class BookingRequest(BaseModel):
    start_time: str  # Format: "2026-04-06T15:00:00+07:00"
    end_time: str  # Format: "2026-04-06T16:00:00+07:00"
    summary: Optional[str] = "Họp đặt bởi AI Agent"


# --- CORE LOGIC ---

def get_calendar_service():
    """Lấy service từ file token.json đã có"""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # Nếu token hết hạn, tự động refresh
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        else:
            raise Exception("Không tìm thấy token.json hợp lệ. Hãy chạy lại script test_oauth.py")

    return build('calendar', 'v3', credentials=creds)


def check_availability_logic(service, start_time, end_time):
    """Check rảnh bận cho chính bạn (primary) và User B"""
    body = {
        "timeMin": start_time,
        "timeMax": end_time,
        "items": [{"id": "primary"}, {"id": USER_B}]
    }
    res = service.freebusy().query(body=body).execute()

    # Kiểm tra nếu bất kỳ ai bận
    for user_id in ["primary", USER_B]:
        if res['calendars'][user_id]['busy']:
            return False
    return True


def create_event_with_invite(service, start_time, end_time, summary):
    """Tạo lịch và mời User B (Sẽ có mail invitation xịn)"""
    event_body = {
        'summary': summary,
        'description': 'Lịch hẹn tự động từ Chatbot Agent.',
        'start': {'dateTime': start_time, 'timeZone': 'Asia/Ho_Chi_Minh'},
        'end': {'dateTime': end_time, 'timeZone': 'Asia/Ho_Chi_Minh'},
        'attendees': [{'email': USER_B}],  # Mời thoải mái không lo 403
        'reminders': {'useDefault': True},
    }

    # Tạo trên lịch 'primary' của bạn
    event = service.events().insert(
        calendarId='primary',
        body=event_body,
        sendUpdates='all'  # Tự động gửi mail mời
    ).execute()
    return event


# --- API ENDPOINTS ---

@app.post("/calendar/check")
async def api_check_availability(req: BookingRequest):
    try:
        service = get_calendar_service()
        is_free = check_availability_logic(service, req.start_time, req.end_time)
        return {"available": is_free}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/calendar/book")
async def api_book_calendar(req: BookingRequest):
    try:
        service = get_calendar_service()
        # Bước cuối: Check lại rồi mới chốt
        if check_availability_logic(service, req.start_time, req.end_time):
            result = create_event_with_invite(service, req.start_time, req.end_time, req.summary)
            return {
                "status": "success",
                "link": result.get('htmlLink'),
                "message": f"Đã gửi thư mời tới {USER_B}"
            }
        else:
            return {"status": "failed", "message": "Giờ này đã có người bận."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)