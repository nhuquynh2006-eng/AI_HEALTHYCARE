import streamlit as st
import pandas as pd

from dashboard.dashboard import dashboard_page
from auth.auth import register_user, login_user
from prediction.predict import prediction_page
from chatbot.chatbot import chatbot_page
from db.db import conn, cursor

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="AI Healthcare System",
    page_icon="🩺",
    layout="wide"
)

# =========================
# CSS
# =========================

with open("styles/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# =========================
# TITLE
# =========================

st.title("🩺 AI Healthcare System")

# Session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "role" not in st.session_state:
    st.session_state.role = "user"

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
            menu_options = ["📊 Dashboard", "👥 Quản lý Users", "🩺 Dự đoán", "🤖 Chatbot", "📋 Lịch sử"]
        else:
            menu_options = ["📊 Dashboard", "🩺 Dự đoán", "🤖 Chatbot", "📋 Lịch sử"]

        page = st.radio(
            "",
            menu_options,
            label_visibility="collapsed"
        )
        st.markdown("---")

        cursor.execute("SELECT COUNT(*) FROM predictions")
        total = cursor.fetchone()[0]
        st.metric(label="🔢 Tổng dự đoán", value=total)

        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.role = "user"
            st.rerun()

    else:
        st.markdown("### 📌 Menu")
        page = st.radio(
            "",
            ["🔐 Đăng nhập", "📝 Đăng ký"],
            label_visibility="collapsed"
        )
        st.markdown("---")
        st.info("💡 Đăng nhập để sử dụng hệ thống dự đoán tiểu đường AI")

# =========================
# NỘI DUNG CHÍNH
# =========================

if not st.session_state.logged_in:
    if page == "🔐 Đăng nhập":
        login_user()
    elif page == "📝 Đăng ký":
        register_user()

else:
    st.success(f"✅ Welcome, {st.session_state.username}!")

    if page == "📊 Dashboard":
        dashboard_page()

    elif page == "👥 Quản lý Users":
        if st.session_state.role == "admin":
            st.subheader("👥 Quản lý Users")

            # Thống kê nhanh
            cursor.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
            total_admins = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'user'")
            total_normal = cursor.fetchone()[0]

            col1, col2, col3 = st.columns(3)
            col1.metric("👥 Tổng users", total_users)
            col2.metric("🔴 Admin", total_admins)
            col3.metric("🟢 User", total_normal)

            st.markdown("---")

            # Danh sách users
            st.subheader("📋 Danh sách Users")
            cursor.execute("SELECT id, username, role FROM users")
            users = cursor.fetchall()
            users_df = pd.DataFrame(users, columns=["ID", "Username", "Role"])
            st.dataframe(users_df, use_container_width=True)

            st.markdown("---")

            # Xóa user
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

            # Tất cả dự đoán
            st.subheader("📊 Tất cả dự đoán")
            cursor.execute("SELECT * FROM predictions ORDER BY id DESC")
            all_predictions = cursor.fetchall()
            if all_predictions:
                all_df = pd.DataFrame(
                    all_predictions,
                    columns=["ID", "Glucose", "BMI", "Age", "Risk", "Result", "Blood Pressure", "Insulin"]
                )
                st.dataframe(all_df, use_container_width=True)
            else:
                st.info("Chưa có dữ liệu!")
        else:
            st.error("⛔ Bạn không có quyền truy cập trang này!")

    elif page == "🩺 Dự đoán":
        prediction_page()

    elif page == "🤖 Chatbot":
        chatbot_page()

    elif page == "📋 Lịch sử":
        st.subheader("📋 Prediction History")
        cursor.execute("SELECT * FROM predictions")
        history = cursor.fetchall()

        if not history:
            st.info("Chưa có dữ liệu dự đoán nào!")
        else:
            from report.report import generate_pdf
            from chatbot.chatbot import explain_prediction

            for row in history:
                id, glucose, bmi, age, risk, result, blood_pressure, insulin = row

                with st.expander(f"#{id} | {result} | Risk: {risk:.2f}% | Glucose: {glucose}"):
                    col1, col2, col3 = st.columns(3)
                    col1.metric("🩸 Glucose", glucose)
                    col2.metric("⚖️ BMI", bmi)
                    col3.metric("🎂 Age", age)
                    col1.metric("🎯 Risk", f"{risk:.2f}%")
                    col2.metric("📋 Result", result)

                    if st.button(f"📄 Xuất PDF", key=f"pdf_{id}"):
                        with st.spinner("Đang tạo PDF..."):
                            explanation = explain_prediction(
                                glucose=glucose,
                                bmi=bmi,
                                age=age,
                                blood_pressure=blood_pressure,
                                insulin=insulin,
                                risk=risk
                            )
                            pdf_bytes = generate_pdf(
                                username=st.session_state.username,
                                glucose=glucose,
                                bmi=bmi,
                                age=age,
                                blood_pressure=blood_pressure,
                                insulin=insulin,
                                risk=risk,
                                result=result,
                                explanation=explanation
                            )
                        st.download_button(
                            label="⬇️ Tải PDF",
                            data=pdf_bytes,
                            file_name=f"report_{id}.pdf",
                            mime="application/pdf",
                            key=f"download_{id}"
                        )