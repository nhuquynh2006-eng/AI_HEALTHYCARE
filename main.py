import streamlit as st
import pandas as pd

from dashboard.dashboard import dashboard_page
from auth.auth import register_user, login_user
from prediction.predict import prediction_page
from chatbot.chatbot import chatbot_page
from db.db import conn, cursor
from about.about import about_page

st.set_page_config(page_title="AI Healthcare System", page_icon="🩺", layout="wide")

with open("styles/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("🩺 AI Healthcare System")

if "logged_in"  not in st.session_state: st.session_state.logged_in  = False
if "username"   not in st.session_state: st.session_state.username   = ""
if "role"       not in st.session_state: st.session_state.role       = "user"
if "is_guest"   not in st.session_state: st.session_state.is_guest   = False

# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.image("https://img.icons8.com/color/96/caduceus.png", width=70)
    st.markdown("## 🏥 AI Healthcare")
    st.markdown("---")

    if st.session_state.logged_in:
        st.markdown(f"👋 Xin chào, **{st.session_state.username}**")
        if st.session_state.role == "admin":
            st.markdown("🔴 **Admin**")
        st.markdown("---")
        st.markdown("### 📌 Menu")
        if st.session_state.role == "admin":
            menu_options = ["📊 Dashboard", "ℹ️ Giới thiệu", "👥 Quản lý Users",
                            "🩺 Dự đoán", "🤖 Chatbot", "📋 Lịch sử"]
        else:
            menu_options = ["ℹ️ Giới thiệu", "🩺 Dự đoán", "🤖 Chatbot", "📋 Lịch sử"]
        page = st.radio("", menu_options, label_visibility="collapsed")
        st.markdown("---")

        if st.session_state.role == "admin":
            cursor.execute("SELECT COUNT(*) FROM predictions")
        else:
            cursor.execute("SELECT id FROM users WHERE username = %s", (st.session_state.username,))
            uid_row = cursor.fetchone()
            if uid_row:
                cursor.execute("SELECT COUNT(*) FROM predictions WHERE user_id = %s", (uid_row[0],))
            else:
                cursor.execute("SELECT 0")
        total = cursor.fetchone()[0]
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.1); border-radius:10px; padding:12px 14px; margin-bottom:8px;">
            <div style="font-size:11px; color:rgba(255,255,255,0.6); text-transform:uppercase;
                        letter-spacing:.05em; margin-bottom:4px;">🔢 Tổng dự đoán</div>
            <div style="font-size:24px; font-weight:700; color:#ffffff;">{total}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.is_guest  = False
            st.session_state.role      = "user"
            st.rerun()

    elif st.session_state.is_guest:
        st.markdown("👤 Xin chào, **Khách**")
        st.caption("Chế độ dùng thử — không lưu lịch sử")
        st.markdown("---")
        st.markdown("### 📌 Menu")
        menu_options = ["ℹ️ Giới thiệu", "🩺 Dự đoán", "🤖 Chatbot"]
        page = st.radio("", menu_options, label_visibility="collapsed")
        st.markdown("---")
        st.info("💡 **Đăng nhập** để lưu lịch sử và xem Dashboard cá nhân.")
        if st.button("🔐 Đăng nhập / Đăng ký", use_container_width=True):
            st.session_state.is_guest = False
            st.rerun()

    else:
        st.markdown("### 📌 Menu")
        page = st.radio("", ["🔐 Đăng nhập", "📝 Đăng ký"], label_visibility="collapsed")
        st.markdown("---")
        st.markdown("**Hoặc dùng thử ngay:**")
        if st.button("👤 Vào với tư cách Khách", use_container_width=True):
            st.session_state.is_guest = True
            st.rerun()
        st.markdown("---")
        st.info("💡 Đăng nhập để lưu lịch sử và sử dụng đầy đủ tính năng")

# =========================
# NỘI DUNG CHÍNH
# =========================

def render_history_card(id, glucose, bmi, age, risk, result, blood_pressure, insulin,
                        owner, is_admin_view):
    """Hiển thị 1 bản ghi lịch sử dạng HTML card — không dùng st.metric()"""
    # Màu risk
    if risk >= 60:
        risk_color = "#a32d2d"; risk_bg = "#fcebeb"
    elif risk >= 30:
        risk_color = "#854f0b"; risk_bg = "#faeeda"
    else:
        risk_color = "#0f6e56"; risk_bg = "#e1f5ee"

    result_color = "#a32d2d" if "High" in result else "#0f6e56"

    admin_row = (
        f'<div style="background:#eeedfe; border-radius:8px; padding:8px 12px; margin-top:6px;'
        f'font-size:13px; color:#3c3489;">👤 <b>User:</b> {owner}</div>'
    ) if is_admin_view else ""

    st.markdown(f"""
    <div style="display:grid; grid-template-columns:repeat(3,1fr); gap:10px; margin-bottom:8px;">
        <div style="background:#f0faf5; border:1px solid #d4ede6; border-radius:10px; padding:12px;">
            <div style="font-size:11px; color:#5a8a7a; font-weight:600;
                        text-transform:uppercase; letter-spacing:.04em; margin-bottom:4px;">🩸 Glucose</div>
            <div style="font-size:20px; font-weight:700; color:#0d4f3c;">{glucose:.0f} <span style="font-size:12px;font-weight:400">mg/dL</span></div>
        </div>
        <div style="background:#f0faf5; border:1px solid #d4ede6; border-radius:10px; padding:12px;">
            <div style="font-size:11px; color:#5a8a7a; font-weight:600;
                        text-transform:uppercase; letter-spacing:.04em; margin-bottom:4px;">⚖️ BMI</div>
            <div style="font-size:20px; font-weight:700; color:#0d4f3c;">{bmi:.1f}</div>
        </div>
        <div style="background:#f0faf5; border:1px solid #d4ede6; border-radius:10px; padding:12px;">
            <div style="font-size:11px; color:#5a8a7a; font-weight:600;
                        text-transform:uppercase; letter-spacing:.04em; margin-bottom:4px;">🎂 Tuổi</div>
            <div style="font-size:20px; font-weight:700; color:#0d4f3c;">{age} <span style="font-size:12px;font-weight:400">tuổi</span></div>
        </div>
        <div style="background:{risk_bg}; border:1px solid {risk_color}40; border-radius:10px; padding:12px;">
            <div style="font-size:11px; color:{risk_color}; font-weight:600;
                        text-transform:uppercase; letter-spacing:.04em; margin-bottom:4px;">🎯 Risk</div>
            <div style="font-size:20px; font-weight:700; color:{risk_color};">{risk:.2f}%</div>
        </div>
        <div style="background:#f0faf5; border:1px solid #d4ede6; border-radius:10px; padding:12px;">
            <div style="font-size:11px; color:#5a8a7a; font-weight:600;
                        text-transform:uppercase; letter-spacing:.04em; margin-bottom:4px;">💓 Huyết áp</div>
            <div style="font-size:20px; font-weight:700; color:#0d4f3c;">{blood_pressure} <span style="font-size:12px;font-weight:400">mmHg</span></div>
        </div>
        <div style="background:#f0faf5; border:1px solid #d4ede6; border-radius:10px; padding:12px;">
            <div style="font-size:11px; color:#5a8a7a; font-weight:600;
                        text-transform:uppercase; letter-spacing:.04em; margin-bottom:4px;">💉 Insulin</div>
            <div style="font-size:20px; font-weight:700; color:#0d4f3c;">{insulin} <span style="font-size:12px;font-weight:400">μU/mL</span></div>
        </div>
    </div>
    <div style="background:{risk_bg}; border-left:4px solid {result_color};
                border-radius:0 8px 8px 0; padding:10px 14px; font-size:14px;
                font-weight:600; color:{result_color}; margin-bottom:6px;">
        📋 Kết quả: {result}
    </div>
    {admin_row}
    """, unsafe_allow_html=True)


if st.session_state.is_guest:
    st.markdown("""
    <div style="background:#fff8e1; border:1px solid #ffe082; border-radius:10px;
                padding:10px 16px; margin-bottom:16px; font-size:14px; color:#795548;">
        👤 Bạn đang dùng với tư cách <b>Khách vãng lai</b> — kết quả dự đoán sẽ
        <b>không được lưu</b>. Đăng nhập để lưu lịch sử.
    </div>
    """, unsafe_allow_html=True)
    if page == "ℹ️ Giới thiệu": about_page()
    elif page == "🩺 Dự đoán":   prediction_page()
    elif page == "🤖 Chatbot":   chatbot_page()

elif not st.session_state.logged_in:
    if page == "🔐 Đăng nhập": login_user()
    elif page == "📝 Đăng ký":  register_user()

else:
    st.success(f"✅ Welcome, {st.session_state.username}!")

    if page == "📊 Dashboard":
        dashboard_page()

    elif page == "👥 Quản lý Users":
        if st.session_state.role == "admin":
            st.subheader("👥 Quản lý Users")

            cursor.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
            total_admins = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'user'")
            total_normal = cursor.fetchone()[0]

            st.markdown(f"""
            <div style="display:grid; grid-template-columns:repeat(3,1fr); gap:10px; margin-bottom:1rem;">
                <div style="background:#ffffff; border:1px solid #d4ede6; border-radius:12px; padding:14px 12px;">
                    <div style="font-size:11px; color:#5a8a7a; font-weight:600;
                                text-transform:uppercase; letter-spacing:.04em; margin-bottom:6px;">👥 Tổng users</div>
                    <div style="font-size:22px; font-weight:700; color:#0d4f3c;">{total_users}</div>
                </div>
                <div style="background:#ffffff; border:1px solid #fcebeb; border-radius:12px; padding:14px 12px;">
                    <div style="font-size:11px; color:#a32d2d; font-weight:600;
                                text-transform:uppercase; letter-spacing:.04em; margin-bottom:6px;">🔴 Admin</div>
                    <div style="font-size:22px; font-weight:700; color:#a32d2d;">{total_admins}</div>
                </div>
                <div style="background:#ffffff; border:1px solid #d4ede6; border-radius:12px; padding:14px 12px;">
                    <div style="font-size:11px; color:#0f6e56; font-weight:600;
                                text-transform:uppercase; letter-spacing:.04em; margin-bottom:6px;">🟢 User</div>
                    <div style="font-size:22px; font-weight:700; color:#0f6e56;">{total_normal}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("---")
            st.subheader("📋 Danh sách Users")
            cursor.execute("SELECT id, username, role FROM users")
            users_df = pd.DataFrame(cursor.fetchall(), columns=["ID", "Username", "Role"])
            st.dataframe(users_df, use_container_width=True)

            st.markdown("---")
            st.subheader("🗑️ Xóa User")
            cursor.execute("SELECT username FROM users WHERE role != 'admin'")
            user_list = [u[0] for u in cursor.fetchall()]
            if user_list:
                selected_user = st.selectbox("Chọn user cần xóa", user_list)
                if st.button("🗑️ Xóa", type="primary"):
                    cursor.execute("DELETE FROM users WHERE username = %s", (selected_user,))
                    conn.commit()
                    st.success(f"✅ Đã xóa user {selected_user}!")
                    st.rerun()
            else:
                st.info("Không có user nào để xóa!")

            st.markdown("---")
            st.subheader("📊 Tất cả dự đoán")
            cursor.execute("""
                SELECT p.id, u.username, p.glucose, p.bmi, p.age,
                       p.risk, p.result, p.blood_pressure, p.insulin
                FROM predictions p
                LEFT JOIN users u ON p.user_id = u.id
                ORDER BY p.id DESC
            """)
            all_predictions = cursor.fetchall()
            if all_predictions:
                all_df = pd.DataFrame(all_predictions,
                    columns=["ID","Username","Glucose","BMI","Age","Risk","Result","Blood Pressure","Insulin"])
                st.dataframe(all_df, use_container_width=True)
            else:
                st.info("Chưa có dữ liệu!")
        else:
            st.error("⛔ Bạn không có quyền truy cập trang này!")

    elif page == "🩺 Dự đoán":  prediction_page()
    elif page == "🤖 Chatbot":  chatbot_page()
    elif page == "ℹ️ Giới thiệu": about_page()

    elif page == "📋 Lịch sử":
        if st.session_state.role == "admin":
            st.subheader("📋 Lịch sử tất cả dự đoán")
            cursor.execute("""
                SELECT p.id, p.user_id, p.glucose, p.bmi, p.age,
                       p.risk, p.result, p.blood_pressure, p.insulin,
                       COALESCE(u.username, 'Unknown') as owner
                FROM predictions p
                LEFT JOIN users u ON p.user_id = u.id
                ORDER BY p.id DESC
            """)
            history = cursor.fetchall()
            is_admin_view = True
        else:
            st.subheader("📋 Lịch sử dự đoán của bạn")
            cursor.execute("SELECT id FROM users WHERE username = %s", (st.session_state.username,))
            row = cursor.fetchone()
            current_user_id = row[0] if row else None
            if current_user_id:
                cursor.execute("""
                    SELECT id, user_id, glucose, bmi, age,
                           risk, result, blood_pressure, insulin,
                           %s as owner
                    FROM predictions
                    WHERE user_id = %s
                    ORDER BY id DESC
                """, (st.session_state.username, current_user_id))
            else:
                cursor.execute("SELECT * FROM predictions WHERE 1=0")
            history = cursor.fetchall()
            is_admin_view = False

        if not history:
            st.info("Chưa có dữ liệu dự đoán nào!")
        else:
            from report.report import generate_pdf
            from chatbot.chatbot import explain_prediction

            for row in history:
                id, user_id, glucose, bmi, age, risk, result, blood_pressure, insulin, owner = row

                try: risk           = float(risk)          if risk           not in (None,"") else 0.0
                except: risk           = 0.0
                try: glucose        = float(glucose)       if glucose        is not None else 0.0
                except: glucose        = 0.0
                try: bmi            = float(bmi)           if bmi            is not None else 0.0
                except: bmi            = 0.0
                try: age            = int(age)             if age            is not None else 0
                except: age            = 0
                try: blood_pressure = int(blood_pressure)  if blood_pressure is not None else 0
                except: blood_pressure = 0
                try: insulin        = int(insulin)         if insulin        is not None else 0
                except: insulin        = 0

                owner  = owner  or "Unknown"
                result = result or "N/A"

                label = (
                    f"#{id} | 👤 {owner} | {result} | Risk: {risk:.2f}% | Glucose: {glucose:.0f}"
                    if is_admin_view else
                    f"#{id} | {result} | Risk: {risk:.2f}% | Glucose: {glucose:.0f}"
                )

                with st.expander(label):
                    # HTML cards thay st.metric()
                    render_history_card(id, glucose, bmi, age, risk, result,
                                        blood_pressure, insulin, owner, is_admin_view)

                    if st.button("📄 Xuất PDF", key=f"pdf_{id}"):
                        with st.spinner("Đang tạo PDF..."):
                            explanation = explain_prediction(
                                glucose=glucose, bmi=bmi, age=age,
                                blood_pressure=blood_pressure, insulin=insulin,
                                skin_thickness=0, risk=risk
                            )
                            pdf_bytes = generate_pdf(
                                username=owner, glucose=glucose, bmi=bmi, age=age,
                                blood_pressure=blood_pressure, insulin=insulin,
                                risk=risk, result=result, explanation=explanation
                            )
                        st.download_button(
                            label="⬇️ Tải PDF", data=pdf_bytes,
                            file_name=f"report_{id}.pdf", mime="application/pdf",
                            key=f"download_{id}"
                        )