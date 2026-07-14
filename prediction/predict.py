import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import joblib

from chatbot.chatbot import explain_prediction
from report.report import generate_pdf
from tensorflow.keras.models import load_model
from db.db import conn, cursor

from risk_timeline import risk_timeline_section
from reminder import reminder_section
from lifestyle import lifestyle_analysis_section
from share_doctor import share_with_doctor_section
from wearable import wearable_section

model  = load_model("models/diabetes_model.keras")
scaler = joblib.load("models/scaler.pkl")


def prediction_page():
    st.subheader("🩺 Diabetes Prediction System")

    is_guest = st.session_state.get("is_guest", False)
    username = "Khách" if is_guest else st.session_state.get("username", "")

    user_id = None
    if not is_guest and username:
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        row = cursor.fetchone()
        if row:
            user_id = row[0]

    # ── Tabs chính (bỏ Thành tích) ──
    if is_guest:
        tab1, tab3 = st.tabs(["🔍 Dự đoán", "🥗 Lối sống"])
        tab2 = tab4 = None
    else:
        tab1, tab2, tab3, tab4 = st.tabs([
            "🔍 Dự đoán", "📈 Timeline", "🥗 Lối sống", "⌚ Wearable"
        ])

    # ════════════════════════════════
    # TAB 1 — DỰ ĐOÁN
    # ════════════════════════════════
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            pregnancies    = st.number_input("🤰 Pregnancies",                   min_value=0)
            glucose        = st.number_input("🩸 Glucose",                       min_value=0)
            blood_pressure = st.number_input("💓 Blood Pressure",                min_value=0)
            skin_thickness = st.number_input("📏 Skin Thickness",                min_value=0)
        with col2:
            insulin           = st.number_input("💉 Insulin",                    min_value=0)
            bmi               = st.number_input("⚖️ BMI",                        min_value=0.0)
            diabetes_pedigree = st.number_input("🧬 Diabetes Pedigree Function", min_value=0.0)
            age               = st.number_input("🎂 Age",                        min_value=1)

        # ── Validation ──
        errors = []
        if glucose == 0:   errors.append("⚠️ Glucose không thể bằng 0.")
        if bmi == 0.0:     errors.append("⚠️ BMI không thể bằng 0.")
        if age < 1:        errors.append("⚠️ Tuổi phải lớn hơn 0.")
        if glucose > 500:  errors.append("⚠️ Glucose có vẻ quá cao (> 500).")
        if bmi > 70:       errors.append("⚠️ BMI có vẻ quá cao (> 70).")
        if blood_pressure > 200: errors.append("⚠️ Huyết áp có vẻ quá cao (> 200).")

        warnings = []
        if glucose > 126:       warnings.append(f"🩸 Glucose = {glucose} mg/dL — vượt ngưỡng (< 126)")
        if blood_pressure > 90: warnings.append(f"💓 Huyết áp = {blood_pressure} mmHg — vượt ngưỡng (< 90)")
        if bmi > 30:            warnings.append(f"⚖️ BMI = {bmi} — béo phì (> 30)")
        if insulin > 200:       warnings.append(f"💉 Insulin = {insulin} μU/mL — vượt ngưỡng (< 200)")

        if warnings:
            with st.expander("⚠️ Phát hiện chỉ số bất thường"):
                for w in warnings:
                    st.warning(w)

        st.markdown("---")
        col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 2])
        with col_btn2:
            predict_btn = st.button("🔍 Predict", key="predict_button", use_container_width=True)

        if errors:
            for e in errors:
                st.error(e)

        elif predict_btn:
            raw_data = np.array([[pregnancies, glucose, blood_pressure, skin_thickness,
                                   insulin, bmi, diabetes_pedigree, age]])
            data       = scaler.transform(raw_data)
            prediction = model.predict(data)
            result_val = prediction[0][0]
            risk       = round(result_val * 100, 2)

            if result_val > 0.5:
                final_result = "High Risk of Diabetes"
            else:
                final_result = "Low Risk of Diabetes"

            # Lưu vào session để dùng lại ở các section
            st.session_state["pred_risk"]           = risk
            st.session_state["pred_result"]         = final_result
            st.session_state["pred_result_val"]     = result_val
            st.session_state["pred_glucose"]        = glucose
            st.session_state["pred_bmi"]            = bmi
            st.session_state["pred_age"]            = age
            st.session_state["pred_blood_pressure"] = blood_pressure
            st.session_state["pred_insulin"]        = insulin
            st.session_state["pred_skin"]           = skin_thickness
            st.session_state["last_glucose"]        = glucose
            st.session_state["last_bmi"]            = bmi
            st.session_state["last_risk"]           = risk

            # Lưu DB
            if not is_guest and user_id:
                sql = """INSERT INTO predictions
                         (user_id, glucose, bmi, age, risk, result, blood_pressure, insulin)
                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
                cursor.execute(sql, (user_id, float(glucose), float(bmi), int(age),
                                     float(risk), str(final_result),
                                     int(blood_pressure), int(insulin)))
                conn.commit()
                st.success("💾 Đã lưu vào lịch sử của bạn!")
            elif is_guest:
                st.info("👤 Chế độ khách — kết quả không được lưu.")

        # ── Hiển thị kết quả nếu đã predict ──
        if "pred_risk" in st.session_state:
            risk         = st.session_state["pred_risk"]
            final_result = st.session_state["pred_result"]
            result_val   = st.session_state["pred_result_val"]
            glucose      = st.session_state["pred_glucose"]
            bmi          = st.session_state["pred_bmi"]
            age          = st.session_state["pred_age"]
            blood_pressure = st.session_state["pred_blood_pressure"]
            insulin      = st.session_state["pred_insulin"]
            skin_thickness = st.session_state["pred_skin"]

            # Risk badge
            risk_color = "#a32d2d" if risk >= 60 else ("#854f0b" if risk >= 30 else "#0f6e56")
            risk_bg    = "#fcebeb" if risk >= 60 else ("#faeeda" if risk >= 30 else "#e1f5ee")
            st.markdown(f"""
            <div style="background:{risk_bg}; border:2px solid {risk_color};
                        border-radius:14px; padding:16px 20px; text-align:center;
                        margin:12px 0;">
                <div style="font-size:13px; color:{risk_color}; font-weight:600;
                            text-transform:uppercase; letter-spacing:.05em;">🎯 Diabetes Risk</div>
                <div style="font-size:40px; font-weight:700; color:{risk_color};">{risk:.2f}%</div>
                <div style="font-size:15px; color:{risk_color}; font-weight:500;">{final_result}</div>
            </div>
            """, unsafe_allow_html=True)

            # ── Sub-section buttons ──
            st.markdown("#### 📂 Xem chi tiết")
            if "result_section" not in st.session_state:
                st.session_state["result_section"] = "biểu_đồ"

            btn_cols = st.columns(4)
            sections = [
                ("biểu_đồ",    "📊 Biểu đồ"),
                ("ai",         "🤖 Giải thích AI"),
                ("lịch_khám",  "🗓️ Lịch tái khám"),
                ("pdf",        "📄 Tải PDF"),
            ]
            # Ẩn lịch khám với khách
            if is_guest:
                sections = [s for s in sections if s[0] != "lịch_khám"]

            for i, (key, label) in enumerate(sections):
                with btn_cols[i]:
                    is_active = st.session_state["result_section"] == key
                    if st.button(
                        label,
                        key=f"sec_{key}",
                        use_container_width=True,
                        type="primary" if is_active else "secondary"
                    ):
                        st.session_state["result_section"] = key
                        st.rerun()

            st.markdown("---")
            section = st.session_state["result_section"]

            # ── SECTION: Biểu đồ ──
            if section == "biểu_đồ":
                col1, col2 = st.columns(2)
                with col1:
                    fig_gauge = go.Figure(go.Indicator(
                        mode="gauge+number+delta", value=risk,
                        title={"text": "Diabetes Risk (%)"},
                        gauge={
                            "axis": {"range": [0, 100]},
                            "bar":  {"color": "red" if risk > 50 else "green"},
                            "steps": [
                                {"range": [0,  30],  "color": "#d4edda"},
                                {"range": [30, 60],  "color": "#fff3cd"},
                                {"range": [60, 100], "color": "#f8d7da"},
                            ],
                            "threshold": {"line": {"color": "black", "width": 4},
                                          "thickness": 0.75, "value": 50}
                        }
                    ))
                    st.plotly_chart(fig_gauge, use_container_width=True)

                with col2:
                    compare_df = pd.DataFrame({
                        "Chỉ số":      ["Glucose", "Blood Pressure", "BMI", "Insulin"],
                        "Của bạn":     [glucose, blood_pressure, bmi, insulin],
                        "Bình thường": [100, 80, 24.9, 85],
                    })
                    fig_compare = px.bar(
                        compare_df, x="Chỉ số", y=["Của bạn", "Bình thường"],
                        barmode="group", title="So sánh với ngưỡng bình thường",
                        color_discrete_map={"Của bạn": "#e74c3c", "Bình thường": "#2ecc71"}
                    )
                    st.plotly_chart(fig_compare, use_container_width=True)

                categories = ["Glucose", "Blood Pressure", "Skin Thickness", "Insulin", "BMI", "Age"]
                user_norm  = [
                    min(glucose        / 200 * 100, 100),
                    min(blood_pressure / 120 * 100, 100),
                    min(skin_thickness / 60  * 100, 100),
                    min(insulin        / 200 * 100, 100),
                    min(bmi            / 40  * 100, 100),
                    min(age            / 80  * 100, 100),
                ]
                fig_radar = go.Figure(go.Scatterpolar(
                    r=user_norm + [user_norm[0]], theta=categories + [categories[0]],
                    fill="toself", fillcolor="rgba(231,76,60,0.3)",
                    line=dict(color="#e74c3c"), name="Chỉ số của bạn"
                ))
                fig_radar.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                    title="Tổng quan chỉ số sức khỏe"
                )
                st.plotly_chart(fig_radar, use_container_width=True)

            # ── SECTION: AI Giải thích ──
            elif section == "ai":
                st.subheader("🤖 AI Giải thích kết quả")
                # Cache explanation để không gọi API lại mỗi lần
                if "pred_explanation" not in st.session_state:
                    with st.spinner("AI đang phân tích..."):
                        st.session_state["pred_explanation"] = explain_prediction(
                            glucose=glucose, bmi=bmi, age=age,
                            blood_pressure=blood_pressure, insulin=insulin,
                            skin_thickness=skin_thickness, risk=risk
                        )
                st.info(st.session_state["pred_explanation"])

                st.markdown("---")
                if not is_guest:
                    share_with_doctor_section(
                        username=username, risk=risk, result=final_result,
                        glucose=glucose, bmi=bmi, age=int(age),
                        blood_pressure=int(blood_pressure), insulin=int(insulin)
                    )

            # ── SECTION: Lịch tái khám ──
            elif section == "lịch_khám":
                reminder_section(risk=risk, user_id=user_id)

            # ── SECTION: PDF ──
            elif section == "pdf":
                st.subheader("📄 Tải báo cáo PDF")
                if "pred_explanation" not in st.session_state:
                    with st.spinner("AI đang tạo nội dung báo cáo..."):
                        st.session_state["pred_explanation"] = explain_prediction(
                            glucose=glucose, bmi=bmi, age=age,
                            blood_pressure=blood_pressure, insulin=insulin,
                            skin_thickness=skin_thickness, risk=risk
                        )
                pdf_bytes = generate_pdf(
                    username=username, glucose=glucose, bmi=bmi, age=age,
                    blood_pressure=blood_pressure, insulin=insulin,
                    risk=risk, result=final_result,
                    explanation=st.session_state["pred_explanation"]
                )
                st.download_button(
                    label="⬇️ Tải báo cáo PDF",
                    data=pdf_bytes,
                    file_name=f"diabetes_report_{username}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

            # Gợi ý đăng nhập cho khách
            if is_guest:
                st.markdown("""
                <div style="background:#e8f5e9; border:1px solid #a5d6a7; border-radius:10px;
                            padding:14px 18px; font-size:14px; color:#2e7d32; margin-top:16px;">
                    🔐 <b>Đăng nhập</b> để mở khoá: 💾 Lưu lịch sử &nbsp;·&nbsp;
                    📈 Timeline &nbsp;·&nbsp; 🔔 Lịch tái khám
                </div>
                """, unsafe_allow_html=True)

    # ════════════════════════════════
    # TAB 2 — TIMELINE
    # ════════════════════════════════
    if tab2 is not None:
        with tab2:
            risk_timeline_section(username=username)

    # ════════════════════════════════
    # TAB 3 — LỐI SỐNG
    # ════════════════════════════════
    with tab3:
        glucose_val = st.session_state.get("last_glucose", 100)
        bmi_val     = st.session_state.get("last_bmi", 24.0)
        risk_val    = st.session_state.get("last_risk", 0.0)
        lifestyle_analysis_section(glucose=glucose_val, bmi=bmi_val, risk=risk_val)

    # ════════════════════════════════
    # TAB 4 — WEARABLE
    # ════════════════════════════════
    if tab4 is not None:
        with tab4:
            wearable_section()