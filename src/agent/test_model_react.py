import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
# Cấu hình đường dẫn để import được logger từ thư mục telemetry
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ollama_provider import OllamaProvider
from agent import ReActAgent  # Giả sử file chứa class ReActAgent của bạn tên là agent.py
from telemetry.logger import logger
from google_calendar_tool import book_calendar_event

# # ==========================================
# # 1. ĐỊNH NGHĨA CÁC CÔNG CỤ (TOOLS) CHO AGENT
# # ==========================================
# def get_weather(location: str) -> str:
#     """Hàm giả lập việc lấy thời tiết."""
#     print(f"\n[Tool Execution] Đang lấy thời tiết cho: {location}...")
#     if "Hà Nội" in location or "hà nội" in location.lower():
#         return "Nhiệt độ hiện tại là 30 độ C, trời nắng đẹp."
#     elif "Tokyo" in location or "tokyo" in location.lower():
#         return "Nhiệt độ hiện tại là 15 độ C, có mưa rải rác."
#     return f"Không tìm thấy dữ liệu thời tiết cho {location}. Hãy thử Hà Nội hoặc Tokyo."

# def calculate(expression: str) -> str:
#     """Hàm tính toán biểu thức toán học đơn giản."""
#     print(f"\n[Tool Execution] Đang tính toán: {expression}...")
#     try:
#         # Lưu ý: Trong thực tế dùng eval() khá nguy hiểm, 
#         # nhưng ở đây chúng ta dùng tạm để test nhanh.
#         result = eval(expression)
#         return str(result)
#     except Exception as e:
#         return f"Lỗi khi tính toán: {str(e)}"

# # Đóng gói tools thành list các dictionary theo đúng chuẩn của ReActAgent
# # my_tools = [
# #     {
# #         "name": "get_weather",
# #         "description": "Dùng để tra cứu thời tiết của một thành phố. Tham số truyền vào là tên thành phố (ví dụ: Hà Nội).",
# #         "func": get_weather
# #     },
# #     {
# #         "name": "calculate",
# #         "description": "Dùng để tính toán các phép toán (+, -, *, /). Tham số truyền vào là một biểu thức (ví dụ: 30 * 2).",
# #         "func": calculate
# #     }
# # ]

# my_tools = [
#     # ... (giữ nguyên get_weather, calculate)
#     {
#         "name": "book_calendar_event",
#         "description": "Use this to schedule appointments or events in Google Calendar. You MUST provide the parameters in the exact string format: 'Title | YYYY-MM-DDTHH:MM:SS+07:00 | YYYY-MM-DDTHH:MM:SS+07:00 | Location'. The vertical bar '|' must be used as the separator.",
#         "func": book_calendar_event
#     }
# ]

# # ==========================================
# # 2. CHẠY THỬ NGHIỆM AGENT
# # ==========================================
# def run_test():
#     # Khởi tạo LLM
#     print("Đang khởi tạo model...")
#     llm = OllamaProvider(model_name="gemma3:1b", temperature=0.2) 
#     # Mẹo: set temperature thấp (0.1 - 0.2) giúp Agent tuân thủ format ReAct tốt hơn
    
#     # Khởi tạo Agent
#     agent = ReActAgent(llm=llm, tools=my_tools, max_steps=5)
    
#     # Câu hỏi hóc búa để ép Agent phải dùng cả 2 tools
#     # Nó phải: 1. Tìm thời tiết Hà Nội -> 2. Lấy con số đó nhân 3 -> 3. Trả lời
#     user_query = "Schedule a meeting tomorrow"
    
#     print(f"\n[User Query]: {user_query}")
#     print("="*60)
#     print("Agent đang suy nghĩ... (Bạn có thể mở thư mục logs để xem chi tiết từng bước)")
#     print("="*60)
    
#     # Chạy vòng lặp ReAct
#     final_result = agent.run(user_query)
    
#     print("\n" + "="*60)
#     print("[FINAL ANSWER TỪ AGENT]:")
#     print(final_result)
#     print("="*60)

# if __name__ == "__main__":
#     run_test()

import sys
import os
import json

# 1. Force UTF-8 encoding for Terminal (Fixes UnicodeEncodeError on Windows)
sys.stdout.reconfigure(encoding='utf-8')

# 2. Add parent directory to path to import from the 'telemetry' folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ollama_provider import OllamaProvider
from agent import ReActAgent
from telemetry.logger import logger
from google_calendar_tool import book_calendar_event

# ==========================================
# 1. DEFINE TOOLS FOR THE AGENT
# ==========================================
def get_weather(location: str) -> str:
    """Mock function to retrieve weather data."""
    print(f"\n[Tool Execution] Fetching weather for: {location}...")
    location_lower = location.lower()
    if "hanoi" in location_lower or "ha noi" in location_lower:
        return "Current temperature is 30°C, sunny."
    elif "tokyo" in location_lower:
        return "Current temperature is 15°C, light rain."
    return f"Weather data not found for {location}. Please try Hanoi or Tokyo."

def calculate(expression: str) -> str:
    """Function to evaluate simple mathematical expressions."""
    print(f"\n[Tool Execution] Calculating: {expression}...")
    try:
        # Note: eval() is used for demo purposes. Use a safer parser in production.
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"Calculation error: {str(e)}"

# Define the tools list for the ReActAgent
my_tools = [
    {
        "name": "book_calendar_event",
        "description": "Use this to schedule appointments or events in Google Calendar. You MUST provide the parameters in the exact string format: 'Title | YYYY-MM-DDTHH:MM:SS+07:00 | YYYY-MM-DDTHH:MM:SS+07:00 | Location'. The vertical bar '|' must be used as the separator.",
        "func": book_calendar_event
    },
    {
        "name": "get_weather",
        "description": "Use this to check the weather of a city. Parameter: city name (e.g., Hanoi).",
        "func": get_weather
    },
    {
        "name": "calculate",
        "description": "Use this for math operations (+, -, *, /). Parameter: a math expression (e.g., 30 * 2).",
        "func": calculate
    }
]

# ==========================================
# 2. REUSABLE AGENT HELPERS (FOR API)
# ==========================================
def _format_history(history):
    if not history:
        return ""
    lines = ["Conversation history:"]
    for msg in history:
        role = str(msg.get("role", "")).strip() or "user"
        content = str(msg.get("content", "")).strip()
        if content:
            lines.append(f"{role.capitalize()}: {content}")
    lines.append("")
    return "\n".join(lines)


def build_agent(model_name: str = "llama3.2:latest", temperature: float = 0.1, max_steps: int = 5) -> ReActAgent:
    llm = OllamaProvider(model_name=model_name, temperature=temperature)
    return ReActAgent(llm=llm, tools=my_tools, max_steps=max_steps)


def run_agent_message(user_message: str, history=None, model_name: str = "llama3.2:latest", temperature: float = 0.1, max_steps: int = 5) -> str:
    agent = build_agent(model_name=model_name, temperature=temperature, max_steps=max_steps)
    history_block = _format_history(history)
    prompt = f"{history_block}User: {user_message}".strip()
    return agent.run(prompt)

# ==========================================
# 3. AUTOMATED BENCHMARK EXECUTION
# ==========================================
def run_benchmarks():
    # 1. Load the JSON file containing test cases
    file_path = os.path.join(os.path.dirname(__file__), 'data_test.json')
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            test_data = json.load(f)
        benchmarks = test_data.get("lab_03_benchmarks", [])
    except Exception as e:
        print(f"❌ Error reading data_test.json: {e}")
        print("Ensure data_test.json is in the same directory as this script.")
        return

    # 2. Initialize LLM and Agent
    print("Initializing model...")
    # Tip: Keep temperature low (0.1) for better ReAct format adherence
    llm = OllamaProvider(model_name="llama3.2:latest", temperature=0.1) 
    agent = ReActAgent(llm=llm, tools=my_tools, max_steps=5)
    
    print(f"Successfully loaded {len(benchmarks)} test cases. Starting evaluation...\n")
    
    # 3. Loop through each test case
    for index, test_case in enumerate(benchmarks, 1):
        test_id = test_case.get("id", "UNKNOWN_ID")
        description = test_case.get("description", "")
        user_input = test_case.get("input", "")
        expected = test_case.get("expected_behavior", "")
        
        print("="*80)
        print(f"🚀 [TEST CASE {index}/{len(benchmarks)}]: {test_id}")
        print(f"📌 Objective: {description}")
        print(f"🗣️ Input: {user_input}")
        print(f"🎯 Expected Behavior: {expected}")
        print("-" * 80)
        print("Agent is reasoning...\n")
        
        # Run the Agent with the test case input
        final_result = agent.run(user_input)
        
        print("\n" + "-"*80)
        print("🤖 [ACTUAL AGENT RESPONSE]:")
        print(final_result)
        print("="*80 + "\n")

if __name__ == "__main__":
    run_benchmarks()
