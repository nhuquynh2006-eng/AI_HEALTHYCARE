import streamlit as st
from db.db import cursor, conn


def gamification_section(username: str):
    """Hiển thị huy hiệu, streak và thành tích sức khỏe — theo từng user."""

    st.subheader("🏆 Thành tích sức khỏe")

    # Lấy user_id từ username
    cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
    uid_row = cursor.fetchone()

    if not uid_row:
        st.warning("Không tìm thấy tài khoản.")
        return

    user_id = uid_row[0]

    # Chỉ lấy predictions của user này
    cursor.execute(
        "SELECT risk, result FROM predictions WHERE user_id = %s ORDER BY id ASC",
        (user_id,)
    )
    rows = cursor.fetchall()
    total = len(rows)

    if total == 0:
        st.info("Chưa có dữ liệu dự đoán. Hãy thực hiện kiểm tra sức khỏe đầu tiên!")
        return

    high_risk_count = sum(1 for r in rows if r[0] >= 60)
    low_risk_count  = sum(1 for r in rows if r[0] < 30)
    risks = [r[0] for r in rows]

    # Tính streak cải thiện liên tiếp
    streak = 0
    for i in range(len(risks) - 1, 0, -1):
        if risks[i] < risks[i - 1]:
            streak += 1
        else:
            break

    # ── Thống kê nhanh ──
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📊 Tổng kiểm tra", total)
    col2.metric("✅ Nguy cơ thấp",   low_risk_count)
    col3.metric("⚠️ Nguy cơ cao",    high_risk_count)
    col4.metric("🔥 Streak cải thiện", f"{streak} lần")

    st.markdown("---")
    st.markdown("#### 🏅 Huy hiệu của bạn")

    badges = [
        {
            "icon": "🩺", "name": "Bước đầu tiên",
            "desc": "Thực hiện kiểm tra sức khỏe đầu tiên",
            "earned": total >= 1,
        },
        {
            "icon": "📅", "name": "Kiên trì",
            "desc": "Kiểm tra sức khỏe 5 lần",
            "earned": total >= 5,
        },
        {
            "icon": "💪", "name": "Chăm chỉ",
            "desc": "Kiểm tra sức khỏe 10 lần",
            "earned": total >= 10,
        },
        {
            "icon": "💚", "name": "Sức khỏe tốt",
            "desc": "Đạt nguy cơ thấp ít nhất 3 lần",
            "earned": low_risk_count >= 3,
        },
        {
            "icon": "📈", "name": "Đang cải thiện",
            "desc": "Cải thiện liên tiếp 3 lần",
            "earned": streak >= 3,
        },
        {
            "icon": "🛡️", "name": "Chiến binh sức khỏe",
            "desc": "Duy trì streak cải thiện 5 lần",
            "earned": streak >= 5,
        },
        {
            "icon": "🌟", "name": "Anh hùng sức khỏe",
            "desc": "Không có lần nào nguy cơ cao",
            "earned": high_risk_count == 0 and total >= 3,
        },
        {
            "icon": "👑", "name": "Bậc thầy sức khỏe",
            "desc": "Hoàn thành 20 lần kiểm tra",
            "earned": total >= 20,
        },
    ]

    earned_badges = [b for b in badges if b["earned"]]
    locked_badges = [b for b in badges if not b["earned"]]

    if earned_badges:
        cols = st.columns(4)
        for i, badge in enumerate(earned_badges):
            with cols[i % 4]:
                st.markdown(f"""
                <div style="background:linear-gradient(135deg,#eaf7f2,#d4ede6);
                            border:2px solid #22966f; border-radius:14px;
                            padding:16px 10px; text-align:center; margin-bottom:10px;">
                    <div style="font-size:32px; margin-bottom:6px;">{badge['icon']}</div>
                    <div style="font-weight:700; color:#0d4f3c; font-size:13px;">{badge['name']}</div>
                    <div style="color:#5a8a7a; font-size:11px; margin-top:4px;">{badge['desc']}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Chưa có huy hiệu nào. Hãy tiếp tục kiểm tra sức khỏe!")

    if locked_badges:
        st.markdown("#### 🔒 Huy hiệu chưa mở khóa")
        cols = st.columns(4)
        for i, badge in enumerate(locked_badges):
            with cols[i % 4]:
                st.markdown(f"""
                <div style="background:#f5f5f5; border:1.5px dashed #cccccc;
                            border-radius:14px; padding:16px 10px; text-align:center;
                            margin-bottom:10px; opacity:0.6;">
                    <div style="font-size:32px; margin-bottom:6px; filter:grayscale(1);">{badge['icon']}</div>
                    <div style="font-weight:600; color:#888; font-size:13px;">{badge['name']}</div>
                    <div style="color:#aaa; font-size:11px; margin-top:4px;">{badge['desc']}</div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("---")
    progress = len(earned_badges) / len(badges)
    st.markdown(f"#### ⭐ Tiến độ: {len(earned_badges)}/{len(badges)} huy hiệu")
    st.progress(progress)