import os
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Load biến môi trường từ file .env
load_dotenv()

SERVICE_ACCOUNT_FILE = os.getenv('SERVICE_ACCOUNT_FILE')
USER_A = os.getenv('USER_A_EMAIL')
USER_B = os.getenv('USER_B_EMAIL')

# SCOPES cần quyền ghi để tạo được event
SCOPES = ['https://www.googleapis.com/auth/calendar']


def get_service():
    """Khởi tạo kết nối với Google Calendar API bằng Service Account"""
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build('calendar', 'v3', credentials=creds)


def check_availability(service, start_time, end_time):
    """
    Kiểm tra xem cả User A và User B có rảnh trong khoảng thời gian này không.
    Trả về True nếu cả hai đều rảnh.
    """
    print(f"\n--- ĐANG KIỂM TRA LỊCH TRONG KHOẢNG: ---")
    print(f"Bắt đầu: {start_time}")
    print(f"Kết thúc: {end_time}\n")

    body = {
        "timeMin": start_time,
        "timeMax": end_time,
        "items": [{"id": USER_A}, {"id": USER_B}]
    }

    res = service.freebusy().query(body=body).execute()

    all_free = True
    for user in [USER_A, USER_B]:
        busy_slots = res['calendars'][user]['busy']
        if busy_slots:
            all_free = False
            print(f"❌ {user}: ĐANG BẬN")
            for slot in busy_slots:
                print(f"   - Khoảng bận: {slot['start']} đến {slot['end']}")
        else:
            print(f"✅ {user}: ĐANG RẢNH")

    return all_free


def create_dual_events(service, start_time, end_time, summary="Họp đặt bởi AI Agent"):
    """
    Tạo 2 sự kiện riêng biệt trên lịch của User A và User B.
    Cách này lách được lỗi 403 'Domain-Wide Delegation'.
    """
    event_body = {
        'summary': summary,
        'description': 'Lịch hẹn tự động từ Chatbot Agent.',
        'start': {'dateTime': start_time, 'timeZone': 'Asia/Ho_Chi_Minh'},
        'end': {'dateTime': end_time, 'timeZone': 'Asia/Ho_Chi_Minh'},
        'reminders': {'useDefault': True},
    }

    results = []
    # Lặp qua cả 2 user để ghi lịch riêng cho từng người
    for user_email in [USER_A, USER_B]:
        try:
            event_result = service.events().insert(
                calendarId=user_email,
                body=event_body
            ).execute()
            print(f"✅ Đã ghi lịch cho: {user_email}")
            results.append(event_result.get('htmlLink'))
        except Exception as e:
            print(f"❌ Lỗi khi ghi lịch cho {user_email}: {e}")

    if len(results) == 2:
        print(f"\n🚀 TẤT CẢ ĐÃ XONG! Lịch đã xuất hiện trên cả 2 tài khoản.")
        print(f"Link xem lại (User A): {results[0]}")
    return results


if __name__ == "__main__":
    calendar_service = get_service()

    # Nhớ chỉnh giờ test phù hợp với thời điểm hiện tại của bạn
    test_start = "2026-04-06T15:00:00+07:00"
    test_end = "2026-04-06T16:00:00+07:00"

    if check_availability(calendar_service, test_start, test_end):
        print("\n=> KẾT LUẬN: CẢ HAI ĐỀU RẢNH. Đang ghi lịch song song...")
        create_dual_events(calendar_service, test_start, test_end, "Meeting: AI Agent x Backend")
    else:
        print("\n=> KẾT LUẬN: KHÔNG THỂ ĐẶT LỊCH DO CÓ NGƯỜI BẬN.")