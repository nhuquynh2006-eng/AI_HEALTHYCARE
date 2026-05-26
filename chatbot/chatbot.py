import streamlit as st
from groq import Groq

client = Groq(api_key="GROQ_API_KEY")

def chatbot_page():
    st.markdown("---")
    st.subheader("🧠 AI Health Chatbot")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        st.chat_message(msg["role"]).write(msg["content"])

    user_input = st.chat_input("Ask something about diabetes...")

    if user_input:
        st.chat_message("user").write(user_input)
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        with st.spinner("Thinking..."):
            try:
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "You are a helpful medical assistant specializing in diabetes. Answer clearly and concisely. If not related to health, politely redirect."},
                        {"role": "user", "content": user_input}
                    ]
                )
                answer = response.choices[0].message.content
            except Exception as e:
                answer = f"⚠️ Error: {str(e)}"

        st.chat_message("assistant").write(answer)
        st.session_state.chat_history.append({"role": "assistant", "content": answer})


def explain_prediction(glucose, bmi, age, blood_pressure, insulin, risk):
    prompt = f"""
    Bạn là trợ lý y tế chuyên về tiểu đường. 
    Hãy giải thích kết quả dự đoán sau bằng tiếng Việt, ngắn gọn dễ hiểu:

    - Glucose: {glucose}
    - BMI: {bmi}
    - Tuổi: {age}
    - Huyết áp: {blood_pressure}
    - Insulin: {insulin}
    - Nguy cơ tiểu đường: {risk}%

    Giải thích:
    1. Chỉ số nào đang bất thường và tại sao nguy hiểm
    2. Mức độ nguy cơ như thế nào
    3. Lời khuyên cụ thể để cải thiện
    """
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Bạn là trợ lý y tế chuyên về tiểu đường."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Không thể giải thích: {str(e)}"