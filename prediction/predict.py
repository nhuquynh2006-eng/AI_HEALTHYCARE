import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from chatbot.chatbot import explain_prediction
from report.report import generate_pdf
from tensorflow.keras.models import load_model
from db.db import conn, cursor

# Load model
model = load_model("models/diabetes_model.h5")


def prediction_page():
    st.subheader("🩺 Diabetes Prediction System")

    col1, col2 = st.columns(2)

    with col1:
        pregnancies = st.number_input("🤰 Pregnancies", min_value=0)
        glucose = st.number_input("🩸 Glucose", min_value=0)
        blood_pressure = st.number_input("💓 Blood Pressure", min_value=0)
        skin_thickness = st.number_input("📏 Skin Thickness", min_value=0)

    with col2:
        insulin = st.number_input("💉 Insulin", min_value=0)
        bmi = st.number_input("⚖️ BMI", min_value=0.0)
        diabetes_pedigree = st.number_input("🧬 Diabetes Pedigree Function", min_value=0.0)
        age = st.number_input("🎂 Age", min_value=1)

    st.markdown("---")

    col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 2])
    with col_btn2:
        predict_btn = st.button("🔍 Predict", key="predict_button", use_container_width=True)

    if predict_btn:

        data = np.array([[pregnancies, glucose, blood_pressure, skin_thickness,
                          insulin, bmi, diabetes_pedigree, age]])

        prediction = model.predict(data)
        result = prediction[0][0]
        risk = round(result * 100, 2)

        st.metric(label="🎯 Diabetes Risk", value=f"{risk:.2f}%")

        # ===== BIỂU ĐỒ =====
        col1, col2 = st.columns(2)

        with col1:
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=risk,
                title={"text": "Diabetes Risk (%)"},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": "red" if risk > 50 else "green"},
                    "steps": [
                        {"range": [0, 30], "color": "#d4edda"},
                        {"range": [30, 60], "color": "#fff3cd"},
                        {"range": [60, 100], "color": "#f8d7da"},
                    ],
                    "threshold": {
                        "line": {"color": "black", "width": 4},
                        "thickness": 0.75,
                        "value": 50
                    }
                }
            ))
            st.plotly_chart(fig_gauge, use_container_width=True)

        with col2:
            compare_df = pd.DataFrame({
                "Chỉ số": ["Glucose", "Blood Pressure", "BMI", "Insulin"],
                "Của bạn": [glucose, blood_pressure, bmi, insulin],
                "Bình thường": [100, 80, 24.9, 85],
            })
            fig_compare = px.bar(
                compare_df,
                x="Chỉ số",
                y=["Của bạn", "Bình thường"],
                barmode="group",
                title="So sánh với ngưỡng bình thường",
                color_discrete_map={"Của bạn": "#e74c3c", "Bình thường": "#2ecc71"}
            )
            st.plotly_chart(fig_compare, use_container_width=True)

        categories = ["Glucose", "Blood Pressure", "Skin Thickness", "Insulin", "BMI", "Age"]
        user_norm = [
            min(glucose / 200 * 100, 100),
            min(blood_pressure / 120 * 100, 100),
            min(skin_thickness / 60 * 100, 100),
            min(insulin / 200 * 100, 100),
            min(bmi / 40 * 100, 100),
            min(age / 80 * 100, 100),
        ]
        fig_radar = go.Figure(go.Scatterpolar(
            r=user_norm + [user_norm[0]],
            theta=categories + [categories[0]],
            fill="toself",
            fillcolor="rgba(231, 76, 60, 0.3)",
            line=dict(color="#e74c3c"),
            name="Chỉ số của bạn"
        ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            title="Tổng quan chỉ số sức khỏe"
        )
        st.plotly_chart(fig_radar, use_container_width=True)

        st.markdown("---")
        st.subheader("🤖 AI Giải thích kết quả")
        with st.spinner("AI đang phân tích..."):
            explanation = explain_prediction(
                glucose=glucose,
                bmi=bmi,
                age=age,
                blood_pressure=blood_pressure,
                insulin=insulin,
                risk=risk
            )
        st.info(explanation)

        if result > 0.5:
            final_result = "High Risk of Diabetes"
            st.error(f"⚠️ {final_result}")
        else:
            final_result = "Low Risk of Diabetes"
            st.success(f"✅ {final_result}")

        sql = "INSERT INTO predictions (glucose, bmi, age, risk, result, blood_pressure, insulin) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        values = (float(glucose), float(bmi), int(age), float(risk), str(final_result), int(blood_pressure),
                  int(insulin))
        cursor.execute(sql, values)
        conn.commit()
        st.success("💾 Saved to database!")

        # ===== XUẤT PDF =====
        st.markdown("---")
        pdf_bytes = generate_pdf(
            username=st.session_state.username,
            glucose=glucose,
            bmi=bmi,
            age=age,
            blood_pressure=blood_pressure,
            insulin=insulin,
            risk=risk,
            result=final_result,
            explanation=explanation
        )
        st.download_button(
            label="📄 Tải báo cáo PDF",
            data=pdf_bytes,
            file_name=f"diabetes_report_{st.session_state.username}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

