"""
chatbot.py — Phiên bản nâng cấp
AI_HEALTHY_CARE Project
Cải tiến:
  - API key từ .env (bảo mật)
  - Lịch sử hội thoại đầy đủ (context-aware)
  - System prompt chuyên sâu hơn
  - Giới hạn lịch sử để tránh vượt token limit
  - Hiển thị disclaimer y tế
"""

import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

# ─────────────────────────────────────────────
# Load API key từ .env (KHÔNG hardcode trong code)
# Tạo file .env với nội dung: GROQ_API_KEY=gsk_xxx...
# ─────────────────────────────────────────────
load_dotenv()
client = Groq(api_key=os.getenv(""))

# Giới hạn số lượt hội thoại lưu lại (tránh vượt token limit)
MAX_HISTORY_TURNS = 10

SYSTEM_PROMPT = """Bạn là trợ lý y tế AI chuyên về bệnh tiểu đường (diabetes), 
được tích hợp trong hệ thống AI_HEALTHY_CARE.

Vai trò của bạn:
- Giải thích các chỉ số sức khỏe liên quan đến tiểu đường (Glucose, BMI, HbA1c, Insulin, v.v.)
- Tư vấn lối sống, chế độ ăn uống và tập luyện phòng ngừa tiểu đường
- Giải thích kết quả dự đoán từ mô hình AI một cách dễ hiểu
- Trả lời câu hỏi về triệu chứng, nguyên nhân, phân loại tiểu đường

Nguyên tắc:
- Luôn trả lời bằng tiếng Việt trừ khi người dùng hỏi bằng tiếng Anh
- Trả lời rõ ràng, ngắn gọn, dễ hiểu với người không có chuyên môn y tế
- KHÔNG chẩn đoán bệnh cụ thể hay thay thế bác sĩ
- Nếu câu hỏi không liên quan đến sức khỏe/tiểu đường, lịch sự từ chối và hướng dẫn lại
- Luôn khuyến khích người dùng gặp bác sĩ khi có triệu chứng nghiêm trọng"""


def get_messages_with_history(user_input: str) -> list:
    """Tạo danh sách messages gồm system prompt + lịch sử + câu hỏi mới."""
    # Giới hạn lịch sử để tránh vượt context window
    recent_history = st.session_state.chat_history[-MAX_HISTORY_TURNS * 2:]

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(recent_history)
    messages.append({"role": "user", "content": user_input})
    return messages


def chatbot_page():
    st.markdown("---")
    st.subheader("🧠 AI Health Chatbot")
    st.caption("⚠️ Chatbot chỉ mang tính tham khảo, không thay thế tư vấn bác sĩ.")

    # Khởi tạo lịch sử hội thoại
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Nút xóa lịch sử
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🗑️ Xóa", help="Xóa lịch sử trò chuyện"):
            st.session_state.chat_history = []
            st.rerun()

    # Hiển thị lịch sử hội thoại
    for msg in st.session_state.chat_history:
        st.chat_message(msg["role"]).write(msg["content"])

    # Ô nhập câu hỏi
    user_input = st.chat_input("Hỏi về tiểu đường, chỉ số sức khỏe...")

    if user_input:
        # Hiển thị câu hỏi người dùng
        st.chat_message("user").write(user_input)
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input
        })

        with st.spinner("Đang xử lý..."):
            try:
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=get_messages_with_history(user_input),
                    temperature=0.7,
                    max_tokens=1024,
                )
                answer = response.choices[0].message.content
            except Exception as e:
                answer = f"⚠️ Lỗi kết nối: {str(e)}"

        # Hiển thị câu trả lời
        st.chat_message("assistant").write(answer)
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": answer
        })


def explain_prediction(glucose, bmi, age, blood_pressure, insulin, skin_thickness, risk):
    """
    Giải thích kết quả dự đoán từ mô hình ML bằng ngôn ngữ tự nhiên.
    Đã bổ sung thêm chỉ số skin_thickness so với phiên bản cũ.
    """

    # Đánh giá mức độ nguy cơ
    if risk < 30:
        risk_level = "thấp"
    elif risk < 60:
        risk_level = "trung bình"
    else:
        risk_level = "cao"

    prompt = f"""Bạn là trợ lý y tế chuyên về tiểu đường trong hệ thống AI_HEALTHY_CARE.
Hãy giải thích kết quả dự đoán sau bằng tiếng Việt, ngắn gọn và dễ hiểu:

Thông tin bệnh nhân:
- Glucose (đường huyết): {glucose} mg/dL
- BMI (chỉ số khối cơ thể): {bmi}
- Tuổi: {age}
- Huyết áp: {blood_pressure} mmHg
- Insulin: {insulin} μU/mL
- Độ dày nếp gấp da: {skin_thickness} mm
- Nguy cơ tiểu đường: {risk}% (mức {risk_level})

Hãy trình bày theo 3 phần:
1. **Nhận xét chỉ số**: Chỉ số nào đang bất thường, ngưỡng bình thường là bao nhiêu?
2. **Mức độ nguy cơ**: Giải thích {risk}% có nghĩa là gì với người này.
3. **Lời khuyên cụ thể**: 3 hành động thiết thực nhất để cải thiện sức khỏe.

Lưu ý: Nhắc người dùng đây chỉ là kết quả từ mô hình AI, cần gặp bác sĩ để chẩn đoán chính xác."""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": prompt}
            ],
            temperature=0.5,
            max_tokens=800,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Không thể tạo giải thích: {str(e)}"