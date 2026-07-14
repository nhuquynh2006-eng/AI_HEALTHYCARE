import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from db.db import conn, cursor


def risk_timeline_section(username: str):
    """Hiển thị biểu đồ nguy cơ tiểu đường theo thời gian cho user hiện tại."""

    st.subheader("📈 Risk Score Timeline")

    cursor.execute(
        "SELECT id, risk, result, glucose, bmi FROM predictions ORDER BY id ASC"
    )
    rows = cursor.fetchall()

    if not rows or len(rows) < 2:
        st.info("Cần ít nhất 2 lần dự đoán để hiển thị biểu đồ xu hướng.")
        return

    df = pd.DataFrame(rows, columns=["Lần", "Risk (%)", "Kết quả", "Glucose", "BMI"])

    # Màu từng điểm theo mức nguy cơ
    def risk_color(r):
        if r < 30:   return "#22966f"
        elif r < 60: return "#f5a623"
        else:        return "#e05252"

    colors = [risk_color(r) for r in df["Risk (%)"]]

    fig = go.Figure()

    # Vùng nền phân mức
    fig.add_hrect(y0=0,  y1=30,  fillcolor="#d4edda", opacity=0.25, line_width=0)
    fig.add_hrect(y0=30, y1=60,  fillcolor="#fff3cd", opacity=0.25, line_width=0)
    fig.add_hrect(y0=60, y1=100, fillcolor="#f8d7da", opacity=0.25, line_width=0)

    # Đường xu hướng
    fig.add_trace(go.Scatter(
        x=df["Lần"], y=df["Risk (%)"],
        mode="lines+markers+text",
        line=dict(color="#1a7a5e", width=2.5, dash="solid"),
        marker=dict(size=12, color=colors, line=dict(color="#ffffff", width=2)),
        text=[f"{r:.1f}%" for r in df["Risk (%)"]],
        textposition="top center",
        textfont=dict(size=11, color="#0d4f3c"),
        hovertemplate="Lần %{x}<br>Risk: %{y:.2f}%<extra></extra>",
        name="Nguy cơ"
    ))

    # Trend line
    if len(df) >= 3:
        import numpy as np
        z = np.polyfit(df["Lần"], df["Risk (%)"], 1)
        p = np.poly1d(z)
        fig.add_trace(go.Scatter(
            x=df["Lần"], y=p(df["Lần"]),
            mode="lines",
            line=dict(color="#aaaaaa", width=1.5, dash="dot"),
            name="Xu hướng",
            hoverinfo="skip"
        ))

    fig.update_layout(
        title="Xu hướng nguy cơ tiểu đường qua các lần kiểm tra",
        xaxis_title="Lần kiểm tra",
        yaxis_title="Nguy cơ (%)",
        yaxis=dict(range=[0, 105]),
        xaxis=dict(tickmode="linear", dtick=1),
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=60, b=40, l=40, r=20),
        height=380,
    )

    # Annotations mức nguy cơ
    fig.add_annotation(x=df["Lần"].max(), y=15,  text="Thấp",   showarrow=False, font=dict(color="#22966f", size=11), xanchor="right")
    fig.add_annotation(x=df["Lần"].max(), y=45,  text="Trung bình", showarrow=False, font=dict(color="#f5a623", size=11), xanchor="right")
    fig.add_annotation(x=df["Lần"].max(), y=80,  text="Cao",    showarrow=False, font=dict(color="#e05252", size=11), xanchor="right")

    st.plotly_chart(fig, use_container_width=True)

    # Nhận xét xu hướng
    first_risk = df["Risk (%)"].iloc[0]
    last_risk  = df["Risk (%)"].iloc[-1]
    delta      = last_risk - first_risk

    col1, col2, col3 = st.columns(3)
    col1.metric("🎯 Lần đầu", f"{first_risk:.1f}%")
    col2.metric("🎯 Lần gần nhất", f"{last_risk:.1f}%",
                delta=f"{delta:+.1f}%",
                delta_color="inverse")
    col3.metric("📊 Trung bình", f"{df['Risk (%)'].mean():.1f}%")

    if delta < -5:
        st.success("✅ Xu hướng tốt! Nguy cơ đang giảm dần. Hãy duy trì lối sống lành mạnh!")
    elif delta > 5:
        st.error("⚠️ Nguy cơ đang tăng! Hãy tham khảo ý kiến bác sĩ và điều chỉnh lối sống.")
    else:
        st.info("📊 Nguy cơ tương đối ổn định. Tiếp tục theo dõi sức khỏe định kỳ.")