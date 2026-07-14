import streamlit as st
from datetime import date, timedelta
from db.db import conn, cursor


def reminder_section(risk: float, user_id: int = None):
    """Nhắc nhở tái khám — lưu lịch vào DB thật."""

    st.subheader("🗓️ Nhắc nhở tái khám")

    today = date.today()

    if risk >= 60:
        interval_days, level, color, border, icon = 30,  "cao",        "#f8d7da", "#e05252", "🚨"
        advice = "Nguy cơ cao — nên gặp bác sĩ trong vòng 1 tháng."
    elif risk >= 30:
        interval_days, level, color, border, icon = 90,  "trung bình", "#fff3cd", "#f5a623", "⚠️"
        advice = "Nguy cơ trung bình — kiểm tra lại sau 3 tháng."
    else:
        interval_days, level, color, border, icon = 180, "thấp",       "#d4edda", "#22966f", "✅"
        advice = "Nguy cơ thấp — kiểm tra định kỳ 6 tháng/lần."

    next_checkup = today + timedelta(days=interval_days)

    st.markdown(f"""
    <div style="background:{color}; border-left:4px solid {border};
                border-radius:0 12px 12px 0; padding:16px 20px; margin-bottom:16px;">
        <div style="font-weight:700; font-size:15px; color:#1a2e2a; margin-bottom:6px;">
            {icon} Mức nguy cơ: <span style="color:{border};">{level.upper()}</span>
        </div>
        <div style="color:#2d2d2d; font-size:14px;">{advice}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-bottom:16px;">
        <div style="background:#ffffff; border:1px solid #d4ede6; border-radius:12px; padding:14px 16px;">
            <div style="font-size:11px; color:#5a8a7a; font-weight:600;
                        text-transform:uppercase; letter-spacing:.04em; margin-bottom:6px;">
                🗓️ Ngày kiểm tra hôm nay
            </div>
            <div style="font-size:20px; font-weight:700; color:#0d4f3c;">
                {today.strftime("%d/%m/%Y")}
            </div>
        </div>
        <div style="background:#ffffff; border:1px solid #d4ede6; border-radius:12px; padding:14px 16px;">
            <div style="font-size:11px; color:#5a8a7a; font-weight:600;
                        text-transform:uppercase; letter-spacing:.04em; margin-bottom:6px;">
                🗓️ Lịch tái khám tiếp theo
            </div>
            <div style="font-size:20px; font-weight:700; color:#0d4f3c;">
                {next_checkup.strftime("%d/%m/%Y")}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("#### ✏️ Tự đặt lịch nhắc nhở")

    reminder_date = st.date_input(
        "Chọn ngày tái khám",
        value=next_checkup,
        min_value=today,
        key="reminder_date_input"
    )
    reminder_note = st.text_input(
        "Ghi chú (tên bác sĩ, bệnh viện...)",
        placeholder="VD: BS. Nguyễn Văn A - BV Chợ Rẫy",
        key="reminder_note_input"
    )

    if st.button("💾 Lưu lịch nhắc", key="save_reminder"):
        if user_id:
            try:
                cursor.execute(
                    "INSERT INTO appointments (user_id, appt_date, note, risk) VALUES (%s, %s, %s, %s)",
                    (user_id, reminder_date, reminder_note, float(risk))  # ← fix numpy.float32
                )
                conn.commit()
                st.success(f"✅ Đã lưu lịch tái khám **{reminder_date.strftime('%d/%m/%Y')}** vào hệ thống!")
            except Exception as e:
                st.error(f"Lỗi lưu DB: {e}")
        else:
            st.warning("Không thể lưu — vui lòng đăng nhập.")

    # ── Hiển thị lịch đã lưu từ DB ──
    if user_id:
        cursor.execute(
            "SELECT appt_date, note, risk FROM appointments WHERE user_id = %s ORDER BY appt_date ASC",
            (user_id,)
        )
        saved = cursor.fetchall()
        if saved:
            st.markdown("#### 📌 Lịch hẹn đã lưu")
            for appt_date, note, appt_risk in saved:
                days_left = (appt_date - today).days
                if days_left < 0:
                    tag = f"<span style='color:#a32d2d;font-weight:600;'>Quá hạn {abs(days_left)} ngày</span>"
                elif days_left == 0:
                    tag = "<span style='color:#854f0b;font-weight:600;'>Hôm nay!</span>"
                else:
                    tag = f"<span style='color:#0f6e56;font-weight:600;'>Còn {days_left} ngày</span>"

                st.markdown(f"""
                <div style="background:#eaf7f2; border:1px solid #22966f; border-radius:10px;
                            padding:12px 16px; margin-bottom:8px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div style="font-weight:600; color:#0d4f3c;">
                            📅 {appt_date.strftime('%d/%m/%Y')}
                        </div>
                        {tag}
                    </div>
                    <div style="color:#2d6b57; font-size:13px; margin-top:4px;">
                        📝 {note if note else 'Không có ghi chú'} &nbsp;|&nbsp; Risk: {appt_risk:.1f}%
                    </div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("#### 📋 Chuẩn bị trước khi khám")
    checklist = [
        "Nhịn ăn ít nhất 8 tiếng trước khi xét nghiệm máu",
        "Mang theo kết quả xét nghiệm lần trước",
        "Ghi lại các triệu chứng bất thường gần đây",
        "Chuẩn bị danh sách thuốc đang sử dụng",
        "Uống đủ nước (không ảnh hưởng đến xét nghiệm)",
    ]
    for item in checklist:
        st.checkbox(item, key=f"check_{item[:20]}")