import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import random


def wearable_section():
    """Nhập và phân tích chỉ số từ thiết bị đeo tay (wearable)."""

    st.subheader("⌚ Chỉ số Wearable")
    st.caption("Nhập chỉ số từ smartwatch hoặc vòng tay theo dõi sức khỏe của bạn.")

    tab1, tab2 = st.tabs(["📥 Nhập chỉ số", "📊 Phân tích"])

    with tab1:
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("#### ❤️ Tim mạch")
            heart_rate = st.number_input("Nhịp tim (bpm)", min_value=40, max_value=200,
                                         value=75, key="heart_rate")
            systolic  = st.number_input("Huyết áp tâm thu (mmHg)", min_value=80,
                                         max_value=200, value=120, key="systolic")
            diastolic = st.number_input("Huyết áp tâm trương (mmHg)", min_value=40,
                                         max_value=130, value=80, key="diastolic")

        with col2:
            st.markdown("#### 🫁 Hô hấp")
            spo2 = st.number_input("SpO2 - Oxy máu (%)", min_value=80,
                                    max_value=100, value=98, key="spo2")
            breath_rate = st.number_input("Nhịp thở (lần/phút)", min_value=8,
                                           max_value=40, value=16, key="breath_rate")
            stress_hrv  = st.number_input("HRV - Độ biến thiên nhịp tim (ms)",
                                           min_value=10, max_value=150,
                                           value=50, key="stress_hrv")

        with col3:
            st.markdown("#### 🏃 Hoạt động")
            steps       = st.number_input("Số bước chân hôm nay", min_value=0,
                                           max_value=50000, value=5000, key="steps")
            calories    = st.number_input("Calo tiêu thụ (kcal)", min_value=0,
                                           max_value=5000, value=300, key="calories")
            sleep_score = st.slider("Chất lượng giấc ngủ", 0, 100, 70,
                                    help="0 = rất tệ, 100 = rất tốt", key="sleep_score")

        if st.button("💾 Lưu chỉ số hôm nay", key="save_wearable", use_container_width=True):
            st.session_state["wearable_data"] = {
                "heart_rate": heart_rate, "systolic": systolic,
                "diastolic": diastolic, "spo2": spo2,
                "breath_rate": breath_rate, "hrv": stress_hrv,
                "steps": steps, "calories": calories, "sleep_score": sleep_score,
                "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M")
            }
            st.success("✅ Đã lưu chỉ số wearable!")

    with tab2:
        # Dữ liệu mẫu nếu chưa có
        data = st.session_state.get("wearable_data", {
            "heart_rate": 75, "systolic": 120, "diastolic": 80,
            "spo2": 98, "breath_rate": 16, "hrv": 50,
            "steps": 5000, "calories": 300, "sleep_score": 70,
            "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M")
        })

        # Đánh giá từng chỉ số
        def evaluate(value, low, high, unit, name):
            if low <= value <= high:
                status, color, icon = "Bình thường", "#22966f", "✅"
            elif value < low:
                status, color, icon = "Thấp", "#f5a623", "⬇️"
            else:
                status, color, icon = "Cao", "#e05252", "⬆️"
            return {"name": name, "value": f"{value} {unit}",
                    "status": status, "color": color, "icon": icon}

        evals = [
            evaluate(data["heart_rate"],  60,  100, "bpm",    "Nhịp tim"),
            evaluate(data["systolic"],    90,  120, "mmHg",   "Huyết áp tâm thu"),
            evaluate(data["diastolic"],   60,   80, "mmHg",   "Huyết áp tâm trương"),
            evaluate(data["spo2"],        95,  100, "%",      "SpO2"),
            evaluate(data["breath_rate"], 12,   20, "lần/ph", "Nhịp thở"),
            evaluate(data["hrv"],         30,  100, "ms",     "HRV"),
        ]

        # Hiển thị bảng đánh giá
        cols = st.columns(3)
        for i, e in enumerate(evals):
            with cols[i % 3]:
                st.markdown(f"""
                <div style="background:#ffffff; border-left:4px solid {e['color']};
                            border-radius:0 10px 10px 0; padding:12px 16px; margin-bottom:10px;
                            box-shadow:0 1px 6px rgba(0,0,0,0.06);">
                    <div style="font-weight:600; color:#0d4f3c; font-size:13px;">{e['icon']} {e['name']}</div>
                    <div style="font-size:20px; font-weight:700; color:{e['color']}; margin:4px 0;">{e['value']}</div>
                    <div style="font-size:12px; color:{e['color']};">{e['status']}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")

        # Gauge charts
        col1, col2, col3 = st.columns(3)

        def make_gauge(value, max_val, title, color):
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=value,
                title={"text": title, "font": {"size": 13}},
                gauge={
                    "axis": {"range": [0, max_val]},
                    "bar": {"color": color},
                    "bgcolor": "#f0f7f4",
                    "steps": [{"range": [0, max_val], "color": "#eaf7f2"}]
                }
            ))
            fig.update_layout(height=180, margin=dict(t=40, b=10, l=10, r=10),
                              paper_bgcolor="#ffffff")
            return fig

        with col1:
            st.plotly_chart(make_gauge(data["steps"], 10000, "👟 Bước chân", "#1a7a5e"),
                           use_container_width=True)
        with col2:
            st.plotly_chart(make_gauge(data["calories"], 500, "🔥 Calo (kcal)", "#f5a623"),
                           use_container_width=True)
        with col3:
            st.plotly_chart(make_gauge(data["sleep_score"], 100, "😴 Giấc ngủ", "#6B48FF"),
                           use_container_width=True)

        # Lời khuyên
        st.markdown("---")
        st.markdown("#### 💡 Nhận xét hôm nay")
        if data["steps"] < 5000:
            st.warning("🚶 Bạn đi ít hơn 5,000 bước — hãy cố gắng đạt 8,000–10,000 bước/ngày.")
        if data["spo2"] < 95:
            st.error("🫁 SpO2 thấp! Hãy hít thở sâu và tham khảo ý kiến bác sĩ nếu kéo dài.")
        if data["heart_rate"] > 100:
            st.warning("❤️ Nhịp tim cao bất thường — tránh caffeine và nghỉ ngơi đủ giấc.")
        if data["sleep_score"] < 60:
            st.warning("😴 Chất lượng giấc ngủ kém — tắt điện thoại trước khi ngủ 30 phút.")
        if data["steps"] >= 8000 and data["sleep_score"] >= 75 and data["spo2"] >= 97:
            st.success("🎉 Hôm nay bạn có sức khỏe rất tốt! Hãy duy trì nhé!")