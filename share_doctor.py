import streamlit as st
import qrcode
import io
import base64
from db.db import cursor
from datetime import date


def share_with_doctor_section(username: str, risk: float, result: str,
                               glucose: float, bmi: float, age: int,
                               blood_pressure: int, insulin: int):
    """Tạo QR code và link chia sẻ report với bác sĩ."""

    st.subheader("🔗 Chia sẻ với bác sĩ")
    st.caption("Tạo link hoặc QR code để chia sẻ kết quả với bác sĩ của bạn.")

    # Tóm tắt thông tin
    today = date.today().strftime("%d/%m/%Y")
    risk_level = "Cao" if risk >= 60 else "Trung bình" if risk >= 30 else "Thấp"

    summary = f"""=== BÁO CÁO SỨC KHỎE ===
Bệnh nhân : {username}
Ngày       : {today}
─────────────────────────
Glucose    : {glucose} mg/dL
BMI        : {bmi}
Tuổi       : {age}
Huyết áp   : {blood_pressure} mmHg
Insulin    : {insulin} μU/mL
─────────────────────────
Nguy cơ ĐTĐ: {risk:.1f}% ({risk_level})
Kết quả    : {result}
─────────────────────────
Hệ thống   : AI Healthcare System
"""

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("#### 📋 Tóm tắt kết quả")
        st.code(summary, language=None)

        # Copy button
        st.markdown(f"""
        <div style="background:#eaf7f2; border:1px solid #22966f; border-radius:10px;
                    padding:12px 16px; margin-top:8px;">
            <div style="font-weight:600; color:#0d4f3c; margin-bottom:6px;">
                📨 Nội dung gửi cho bác sĩ
            </div>
            <div style="color:#2d6b57; font-size:13px; line-height:1.7;">
                Bệnh nhân <b>{username}</b> — Ngày {today}<br>
                Glucose: <b>{glucose}</b> | BMI: <b>{bmi}</b> | Tuổi: <b>{age}</b><br>
                Nguy cơ tiểu đường: <b style="color:{'#e05252' if risk>=60 else '#f5a623' if risk>=30 else '#22966f'}">
                    {risk:.1f}% ({risk_level})</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("#### 📱 QR Code")

        # Tạo nội dung QR
        qr_content = (
            f"AI Healthcare Report\n"
            f"Patient: {username}\n"
            f"Date: {today}\n"
            f"Glucose: {glucose} | BMI: {bmi} | Age: {age}\n"
            f"BP: {blood_pressure} | Insulin: {insulin}\n"
            f"Diabetes Risk: {risk:.1f}% ({risk_level})\n"
            f"Result: {result}"
        )

        # Generate QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=6,
            border=3,
        )
        qr.add_data(qr_content)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#0d4f3c", back_color="white")

        # Convert to bytes
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        img_bytes = buf.getvalue()

        # Hiển thị QR
        st.image(img_bytes, caption="Scan để xem thông tin sức khỏe", width=200)

        # Download QR
        st.download_button(
            label="⬇️ Tải QR Code",
            data=img_bytes,
            file_name=f"qr_report_{username}_{date.today()}.png",
            mime="image/png",
            use_container_width=True
        )

    st.markdown("---")

    # Lời khuyên khi gặp bác sĩ
    st.markdown("#### 💬 Những điều nên nói với bác sĩ")
    tips = [
        "Cho bác sĩ xem kết quả dự đoán này để tham khảo",
        "Kể về các triệu chứng bất thường gần đây (khát nước, mệt mỏi, tiểu nhiều...)",
        "Hỏi về xét nghiệm HbA1c để có kết quả chính xác hơn",
        "Thảo luận về chế độ ăn và tập luyện phù hợp với tình trạng của bạn",
        "Hỏi về lịch tái khám và các xét nghiệm cần theo dõi định kỳ",
    ]
    for tip in tips:
        st.markdown(f"- {tip}")