import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from db.db import conn, cursor


def dashboard_page():
    st.subheader("📊 Dashboard Thống Kê")

    # ===== LẤY DỮ LIỆU =====
    cursor.execute("SELECT COUNT(*) FROM predictions")
    total_predictions = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM predictions WHERE result = 'High Risk of Diabetes'")
    high_risk = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM predictions WHERE result = 'Low Risk of Diabetes'")
    low_risk = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(risk) FROM predictions")
    avg_risk = cursor.fetchone()[0] or 0

    # ===== METRIC CARDS =====
    st.markdown("### 📈 Tổng quan")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("👥 Người dùng", total_users)
    col2.metric("🔢 Tổng dự đoán", total_predictions)
    col3.metric("⚠️ Nguy cơ cao", high_risk)
    col4.metric("✅ Nguy cơ thấp", low_risk)
    col5.metric("📊 Risk TB", f"{avg_risk:.1f}%")

    st.markdown("---")

    # ===== BIỂU ĐỒ HÀNG 1 =====
    col1, col2 = st.columns(2)

    with col1:
        # Pie chart tỉ lệ
        fig_pie = px.pie(
            names=["High Risk", "Low Risk"],
            values=[high_risk, low_risk],
            title="🎯 Tỉ lệ nguy cơ",
            color_discrete_map={
                "High Risk": "#e74c3c",
                "Low Risk": "#2ecc71"
            },
            hole=0.4
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        # Bar chart glucose trung bình theo kết quả
        cursor.execute("SELECT result, AVG(glucose), AVG(bmi), AVG(risk) FROM predictions GROUP BY result")
        avg_data = cursor.fetchall()

        if avg_data:
            avg_df = pd.DataFrame(avg_data, columns=["Result", "Avg Glucose", "Avg BMI", "Avg Risk"])
            fig_avg = px.bar(
                avg_df,
                x="Result",
                y=["Avg Glucose", "Avg BMI", "Avg Risk"],
                barmode="group",
                title="📊 Chỉ số trung bình theo kết quả",
                color_discrete_map={
                    "Avg Glucose": "#3498db",
                    "Avg BMI": "#e67e22",
                    "Avg Risk": "#e74c3c"
                }
            )
            st.plotly_chart(fig_avg, use_container_width=True)

    st.markdown("---")

    # ===== BIỂU ĐỒ HÀNG 2 =====
    col1, col2 = st.columns(2)

    with col1:
        # Risk theo từng lần dự đoán
        cursor.execute("SELECT id, risk, result FROM predictions ORDER BY id")
        trend_data = cursor.fetchall()
        trend_df = pd.DataFrame(trend_data, columns=["ID", "Risk", "Result"])

        fig_trend = px.line(
            trend_df,
            x="ID",
            y="Risk",
            title="📈 Xu hướng Risk theo thời gian",
            markers=True,
            color_discrete_sequence=["#3498db"]
        )
        fig_trend.add_hline(y=50, line_dash="dash", line_color="red", annotation_text="Ngưỡng 50%")
        st.plotly_chart(fig_trend, use_container_width=True)

    with col2:
        # Phân bố glucose
        cursor.execute("SELECT glucose, result FROM predictions")
        glucose_data = cursor.fetchall()
        glucose_df = pd.DataFrame(glucose_data, columns=["Glucose", "Result"])

        fig_hist = px.histogram(
            glucose_df,
            x="Glucose",
            color="Result",
            title="🩸 Phân bố Glucose",
            color_discrete_map={
                "High Risk of Diabetes": "#e74c3c",
                "Low Risk of Diabetes": "#2ecc71"
            },
            nbins=10
        )
        st.plotly_chart(fig_hist, use_container_width=True)