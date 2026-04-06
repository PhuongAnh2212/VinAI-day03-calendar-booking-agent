import os
from datetime import datetime
from typing import Optional, List
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

load_dotenv()
SCOPES = ['https://www.googleapis.com/auth/calendar']
CREDENTIALS_FILE = 'credentials.json'

app = FastAPI(title="Calendar Booking Agent - Team Edition")


class BookingRequest(BaseModel):
    start_time: str
    end_time: str
    summary: Optional[str] = "Họp đặt bởi AI Agent"
    # Chuyển thành mảng để mời nhiều người (ví dụ: ["a@gmail.com", "b@gmail.com"])
    target_email: Optional[List[str]] = []


# --- CORE LOGIC ---

def get_calendar_service():
    """Tự động xử lý đăng nhập OAuth2 và trả về service"""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except:
                creds = None

        if not creds:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

    return build('calendar', 'v3', credentials=creds)


def check_availability_logic(service, start_time, end_time, emails):
    """Kiểm tra rảnh/bận của chính mình và danh sách email gửi lên"""
    # 'primary' là người đang chạy code
    items = [{"id": "primary"}]
    for email in emails:
        items.append({"id": email})

    body = {
        "timeMin": start_time,
        "timeMax": end_time,
        "items": items
    }
    res = service.freebusy().query(body=body).execute()

    # Duyệt qua từng user để check mảng 'busy'
    for item in items:
        user_id = item["id"]
        if res['calendars'].get(user_id) and res['calendars'][user_id]['busy']:
            print(f"DEBUG: {user_id} đang bận.")
            return False
    return True


def create_event_logic(service, start_time, end_time, summary, emails):
    """Tạo lịch và gửi lời mời cho toàn bộ danh sách email"""
    attendees = [{'email': email} for email in emails]

    event_body = {
        'summary': summary,
        'description': 'Lịch hẹn tự động từ Chatbot Agent.',
        'start': {'dateTime': start_time, 'timeZone': 'Asia/Ho_Chi_Minh'},
        'end': {'dateTime': end_time, 'timeZone': 'Asia/Ho_Chi_Minh'},
        'attendees': attendees,
        'reminders': {'useDefault': True},
    }
    # Tạo trên lịch của chính mình và mời những người khác
    return service.events().insert(
        calendarId='primary',
        body=event_body,
        sendUpdates='all'
    ).execute()


# --- API ENDPOINTS ---

@app.post("/calendar/check")
async def api_check_availability(req: BookingRequest):
    try:
        service = get_calendar_service()
        is_free = check_availability_logic(service, req.start_time, req.end_time, req.target_email)
        return {"available": is_free}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/calendar/book")
async def api_book_calendar(req: BookingRequest):
    try:
        service = get_calendar_service()
        # Luôn check lại rảnh bận trước khi ghi đè lịch
        if check_availability_logic(service, req.start_time, req.end_time, req.target_email):
            result = create_event_logic(service, req.start_time, req.end_time, req.summary, req.target_email)
            return {"status": "success", "link": result.get('htmlLink'), "sent": True}
        return {"status": "failed", "message": "Có người bận trong khung giờ này.", "sent": False}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)