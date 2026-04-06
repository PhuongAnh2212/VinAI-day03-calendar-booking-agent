import os
from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Load cấu hình
load_dotenv()
USER_B = os.getenv('USER_B_EMAIL')
SCOPES = ['https://www.googleapis.com/auth/calendar']
CREDENTIALS_FILE = 'credentials.json'  # File JSON Desktop App từ Google Cloud

app = FastAPI(title="Calendar Booking Agent (Auto-Auth)")


class BookingRequest(BaseModel):
    start_time: str
    end_time: str
    summary: Optional[str] = "Họp đặt bởi AI Agent"


# --- CORE LOGIC ---

def get_calendar_service():
    """Lấy service, tự động yêu cầu đăng nhập nếu chưa có token"""
    creds = None

    # 1. Kiểm tra nếu đã có file token cũ
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # 2. Nếu không có token hoặc token không hợp lệ (hết hạn)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                print("🔄 Đang làm mới token...")
                creds.refresh(Request())
            except Exception:
                # Nếu refresh thất bại (ví dụ: bị thu hồi quyền), xóa file để login lại
                creds = None

                # 3. Nếu vẫn không có creds hợp lệ -> Bắt đầu luồng đăng nhập trình duyệt
        if not creds:
            print("🔑 Không tìm thấy danh tính hợp lệ. Đang mở trình duyệt để đăng nhập...")
            if not os.path.exists(CREDENTIALS_FILE):
                raise Exception(f"Thiếu file {CREDENTIALS_FILE}! Hãy tải từ Google Cloud Console.")

            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)  # Mở trình duyệt máy đang chạy code

            # Lưu lại token cho lần sau (máy ai người đó dùng)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
                print("✅ Đã lưu danh tính mới vào token.json")

    # Lưu ý: Sửa lỗi typo 'vs3' thành 'v3' trong code cũ của bạn
    return build('calendar', 'v3', credentials=creds)


def check_availability_logic(service, start_time, end_time):
    body = {
        "timeMin": start_time,
        "timeMax": end_time,
        "items": [{"id": "primary"}, {"id": USER_B}]
    }
    res = service.freebusy().query(body=body).execute()
    for user_id in ["primary", USER_B]:
        if res['calendars'][user_id]['busy']:
            return False
    return True


def create_event_with_invite(service, start_time, end_time, summary):
    event_body = {
        'summary': summary,
        'description': 'Lịch hẹn tự động từ Chatbot Agent.',
        'start': {'dateTime': start_time, 'timeZone': 'Asia/Ho_Chi_Minh'},
        'end': {'dateTime': end_time, 'timeZone': 'Asia/Ho_Chi_Minh'},
        'attendees': [{'email': USER_B}],
        'reminders': {'useDefault': True},
    }
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
        is_free = check_availability_logic(service, req.start_time, req.end_time)
        return {"available": is_free}
    except Exception as e:
        print(f"Lỗi: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/calendar/book")
async def api_book_calendar(req: BookingRequest):
    try:
        service = get_calendar_service()
        if check_availability_logic(service, req.start_time, req.end_time):
            result = create_event_with_invite(service, req.start_time, req.end_time, req.summary)
            return {"status": "success", "link": result.get('htmlLink')}
        return {"status": "failed", "message": "Bận rồi."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)