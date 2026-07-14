import streamlit as st
import plotly.graph_objects as go


def lifestyle_analysis_section(glucose: float, bmi: float, risk: float):
    """Phân tích lối sống và đưa ra gợi ý cải thiện."""

    st.subheader("🥗 Phân tích lối sống")
    st.caption("Trả lời các câu hỏi để nhận gợi ý cá nhân hóa")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### 🍽️ Dinh dưỡng")
        diet_sugar = st.slider("Đường/tinh bột/ngày", 0, 10, 5,
                               help="0 = rất ít, 10 = rất nhiều", key="diet_sugar")
        diet_veggie = st.slider("Rau xanh/ngày", 0, 10, 5,
                                help="0 = không ăn, 10 = ăn nhiều", key="diet_veggie")
        diet_water = st.slider("Nước uống (ly/ngày)", 0, 15, 8, key="diet_water")
        diet_fast_food = st.slider("Đồ ăn nhanh/tuần", 0, 7, 2, key="diet_fast_food")

    with col2:
        st.markdown("#### 🏃 Vận động")
        exercise_days = st.slider("Ngày tập/tuần", 0, 7, 3, key="exercise_days")
        exercise_mins = st.slider("Phút tập mỗi lần", 0, 120, 30, key="exercise_mins")
        exercise_type = st.selectbox("Loại hình tập",
                                     ["Đi bộ", "Chạy bộ", "Bơi lội", "Đạp xe",
                                      "Gym", "Yoga", "Không tập"],
                                     key="exercise_type")

    with col3:
        st.markdown("#### 😴 Giấc ngủ & Stress")
        sleep_hours = st.slider("Giờ ngủ/đêm", 0, 12, 7, key="sleep_hours")
        stress_level = st.slider("Mức độ stress", 0, 10, 5,
                                 help="0 = không stress, 10 = rất căng thẳng",
                                 key="stress_level")
        smoking = st.selectbox("Hút thuốc", ["Không", "Thỉnh thoảng", "Thường xuyên"],
                               key="smoking")

    st.markdown("---")

    if st.button("🔍 Phân tích lối sống của tôi", key="analyze_lifestyle"):

        # Tính điểm từng mục (0-100)
        diet_score = max(0, min(100, int(
            (10 - diet_sugar) * 5 +
            diet_veggie * 5 +
            min(diet_water, 8) * 5 +
            (7 - diet_fast_food) * 5
        )))

        exercise_score = max(0, min(100, int(
            exercise_days * 10 +
            min(exercise_mins, 60) * 0.5 +
            (0 if exercise_type == "Không tập" else 20)
        )))

        sleep_score = max(0, min(100, int(
            (100 - abs(sleep_hours - 7.5) * 15) +
            (10 - stress_level) * 2 +
            (0 if smoking == "Thường xuyên" else 20 if smoking == "Không" else 10)
        )))

        overall = int((diet_score + exercise_score + sleep_score) / 3)

        # Radar chart
        fig = go.Figure(go.Scatterpolar(
            r=[diet_score, exercise_score, sleep_score, diet_score],
            theta=["🍽️ Dinh dưỡng", "🏃 Vận động", "😴 Ngủ & Stress", "🍽️ Dinh dưỡng"],
            fill="toself",
            fillcolor="rgba(26, 122, 94, 0.2)",
            line=dict(color="#1a7a5e", width=2),
            name="Lối sống của bạn"
        ))
        fig.add_trace(go.Scatterpolar(
            r=[80, 80, 80, 80],
            theta=["🍽️ Dinh dưỡng", "🏃 Vận động", "😴 Ngủ & Stress", "🍽️ Dinh dưỡng"],
            fill="toself",
            fillcolor="rgba(200, 230, 220, 0.15)",
            line=dict(color="#a8d5c5", width=1.5, dash="dot"),
            name="Mục tiêu lý tưởng"
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            title="Phân tích lối sống tổng thể",
            plot_bgcolor="#ffffff",
            paper_bgcolor="#ffffff",
            height=350,
            legend=dict(orientation="h", y=-0.15)
        )
        st.plotly_chart(fig, use_container_width=True)

        # Điểm số
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🍽️ Dinh dưỡng", f"{diet_score}/100")
        col2.metric("🏃 Vận động", f"{exercise_score}/100")
        col3.metric("😴 Ngủ & Stress", f"{sleep_score}/100")
        col4.metric("⭐ Tổng thể", f"{overall}/100")

        st.markdown("---")
        st.markdown("#### 💡 Gợi ý cải thiện cá nhân hóa")

        suggestions = []

        if diet_sugar > 6:
            suggestions.append(("🍬", "Giảm đường & tinh bột", "Hạn chế nước ngọt, bánh kẹo, cơm trắng. Thay bằng ngũ cốc nguyên hạt, khoai lang."))
        if diet_veggie < 5:
            suggestions.append(("🥦", "Tăng rau xanh", "Ăn ít nhất 3 phần rau/ngày. Rau lá xanh giúp kiểm soát đường huyết hiệu quả."))
        if diet_water < 6:
            suggestions.append(("💧", "Uống đủ nước", "Uống 8 ly nước/ngày. Mất nước làm tăng nồng độ đường trong máu."))
        if exercise_days < 3:
            suggestions.append(("🏃", "Tăng vận động", "Đi bộ nhanh 30 phút/ngày, ít nhất 5 ngày/tuần giúp giảm nguy cơ tiểu đường 30%."))
        if sleep_hours < 6 or sleep_hours > 9:
            suggestions.append(("😴", "Cải thiện giấc ngủ", "Ngủ 7–8 tiếng/đêm. Thiếu ngủ làm tăng insulin resistance."))
        if stress_level > 7:
            suggestions.append(("🧘", "Giảm stress", "Thực hành thiền định, yoga 15–20 phút/ngày. Stress mãn tính làm tăng đường huyết."))
        if smoking == "Thường xuyên":
            suggestions.append(("🚬", "Bỏ thuốc lá", "Hút thuốc làm tăng nguy cơ tiểu đường type 2 lên 30–40%."))

        if not suggestions:
            st.success("🎉 Lối sống của bạn rất tốt! Hãy duy trì thói quen này.")
        else:
            for icon, title, desc in suggestions:
                st.markdown(f"""
                <div style="background:#ffffff; border:1px solid #d4ede6; border-radius:10px;
                            padding:14px 18px; margin-bottom:8px; display:flex; gap:14px;">
                    <div style="font-size:24px;">{icon}</div>
                    <div>
                        <div style="font-weight:600; color:#0d4f3c;">{title}</div>
                        <div style="color:#2d6b57; font-size:13px; margin-top:3px;">{desc}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)