import streamlit as st


def about_page():
    # ── Hero section ──
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #0d4f3c 0%, #1a7a5e 100%);
        border-radius: 16px;
        padding: 40px 32px;
        text-align: center;
        margin-bottom: 2rem;
    ">
        <div style="font-size: 56px; margin-bottom: 12px;">🩺</div>
        <h1 style="color: #ffffff; font-size: 2rem; margin: 0 0 8px 0; font-weight: 700;">
            AI Healthcare System
        </h1>
        <p style="color: #a8d5c5; font-size: 1rem; margin: 0;">
            Hệ thống dự đoán và tư vấn sức khỏe thông minh ứng dụng trí tuệ nhân tạo
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Thống kê nhanh — HTML card thay st.metric() ──
    st.markdown("""
    <div style="display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin-bottom:1.5rem;">
        <div style="background:#ffffff; border:1px solid #d4ede6; border-radius:12px;
                    padding:16px 14px; box-shadow:0 1px 4px rgba(13,79,60,0.06);">
            <div style="font-size:11px; color:#5a8a7a; font-weight:600;
                        text-transform:uppercase; letter-spacing:.04em; margin-bottom:6px;">
                🤖 Mô hình AI
            </div>
            <div style="font-size:18px; font-weight:700; color:#0d4f3c;">Neural Network</div>
        </div>
        <div style="background:#ffffff; border:1px solid #d4ede6; border-radius:12px;
                    padding:16px 14px; box-shadow:0 1px 4px rgba(13,79,60,0.06);">
            <div style="font-size:11px; color:#5a8a7a; font-weight:600;
                        text-transform:uppercase; letter-spacing:.04em; margin-bottom:6px;">
                📊 Dataset
            </div>
            <div style="font-size:18px; font-weight:700; color:#0d4f3c;">768 mẫu</div>
        </div>
        <div style="background:#ffffff; border:1px solid #d4ede6; border-radius:12px;
                    padding:16px 14px; box-shadow:0 1px 4px rgba(13,79,60,0.06);">
            <div style="font-size:11px; color:#5a8a7a; font-weight:600;
                        text-transform:uppercase; letter-spacing:.04em; margin-bottom:6px;">
                🎯 Độ chính xác
            </div>
            <div style="font-size:18px; font-weight:700; color:#0d4f3c;">~82%</div>
        </div>
        <div style="background:#ffffff; border:1px solid #d4ede6; border-radius:12px;
                    padding:16px 14px; box-shadow:0 1px 4px rgba(13,79,60,0.06);">
            <div style="font-size:11px; color:#5a8a7a; font-weight:600;
                        text-transform:uppercase; letter-spacing:.04em; margin-bottom:6px;">
                💬 Chatbot
            </div>
            <div style="font-size:18px; font-weight:700; color:#0d4f3c;">LLaMA 3.3 70B</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Giới thiệu hệ thống ──
    st.subheader("📌 Giới thiệu")
    st.markdown("""
    **AI Healthcare System** là hệ thống hỗ trợ dự đoán nguy cơ mắc bệnh tiểu đường
    và tư vấn sức khỏe sử dụng các mô hình học máy (Machine Learning) và trí tuệ nhân tạo.

    Hệ thống được xây dựng nhằm mục đích **hỗ trợ sàng lọc sớm** nguy cơ tiểu đường
    dựa trên các chỉ số sinh học của người dùng, kết hợp với chatbot AI để giải thích
    kết quả và đưa ra lời khuyên sức khỏe phù hợp.

    > ⚠️ **Lưu ý:** Hệ thống chỉ mang tính tham khảo, không thay thế chẩn đoán y tế
    > từ bác sĩ chuyên khoa.
    """)

    st.markdown("---")

    # ── Tính năng ──
    st.subheader("✨ Tính năng chính")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div style="background:#eaf7f2; border-left:4px solid #22966f; border-radius:0 10px 10px 0; padding:16px 20px; margin-bottom:12px;">
            <b style="color:#0d4f3c;">🔬 Dự đoán tiểu đường</b><br>
            <span style="color:#2d6b57; font-size:14px;">
            Nhập các chỉ số sinh học, hệ thống sẽ dự đoán nguy cơ mắc bệnh
            tiểu đường và trực quan hóa kết quả bằng biểu đồ.
            </span>
        </div>
        <div style="background:#eaf7f2; border-left:4px solid #22966f; border-radius:0 10px 10px 0; padding:16px 20px; margin-bottom:12px;">
            <b style="color:#0d4f3c;">🤖 Chatbot AI tư vấn</b><br>
            <span style="color:#2d6b57; font-size:14px;">
            Chatbot thông minh sử dụng LLaMA 3.3 70B, trả lời câu hỏi
            về tiểu đường và sức khỏe bằng tiếng Việt.
            </span>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="background:#eaf7f2; border-left:4px solid #22966f; border-radius:0 10px 10px 0; padding:16px 20px; margin-bottom:12px;">
            <b style="color:#0d4f3c;">📊 Dashboard thống kê</b><br>
            <span style="color:#2d6b57; font-size:14px;">
            Tổng hợp và trực quan hóa dữ liệu dự đoán theo thời gian,
            phân tích xu hướng nguy cơ của người dùng.
            </span>
        </div>
        <div style="background:#eaf7f2; border-left:4px solid #22966f; border-radius:0 10px 10px 0; padding:16px 20px; margin-bottom:12px;">
            <b style="color:#0d4f3c;">📄 Xuất báo cáo PDF</b><br>
            <span style="color:#2d6b57; font-size:14px;">
            Tạo báo cáo sức khỏe chi tiết dạng PDF, bao gồm kết quả
            dự đoán và lời khuyên từ AI.
            </span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Hướng dẫn sử dụng ──
    st.subheader("📖 Hướng dẫn sử dụng")

    steps = [
        ("1", "Đăng ký / Đăng nhập", "🔐",
         "Tạo tài khoản mới hoặc đăng nhập vào hệ thống. Tài khoản giúp lưu lịch sử dự đoán của bạn."),
        ("2", "Nhập chỉ số sức khỏe", "📋",
         "Vào trang Dự đoán, nhập các chỉ số: Glucose, Huyết áp, BMI, Insulin, Tuổi... Đảm bảo nhập đúng giá trị từ kết quả xét nghiệm."),
        ("3", "Xem kết quả dự đoán", "🎯",
         "Nhấn Predict để xem nguy cơ tiểu đường (%). Kết quả được hiển thị qua biểu đồ đồng hồ, radar và so sánh với ngưỡng bình thường."),
        ("4", "Đọc giải thích AI", "🤖",
         "Hệ thống tự động phân tích các chỉ số bất thường và đưa ra lời khuyên cụ thể giúp cải thiện sức khỏe."),
        ("5", "Tư vấn qua Chatbot", "💬",
         "Dùng trang Chatbot để hỏi thêm về tiểu đường, chế độ ăn uống, tập luyện hay bất kỳ câu hỏi sức khỏe nào."),
        ("6", "Tải báo cáo PDF", "📄",
         "Sau khi dự đoán, nhấn Tải báo cáo PDF để lưu kết quả và lời khuyên về máy để tham khảo hoặc chia sẻ với bác sĩ."),
    ]

    for step in steps:
        num, title, icon, desc = step
        st.markdown(f"""
        <div style="display:flex; gap:16px; align-items:flex-start;
                    background:#ffffff; border:1px solid #d4ede6;
                    border-radius:12px; padding:16px 20px; margin-bottom:10px;
                    box-shadow: 0 1px 6px rgba(13,79,60,0.05);">
            <div style="background:#0d4f3c; color:#ffffff; border-radius:50%;
                        width:36px; height:36px; display:flex; align-items:center;
                        justify-content:center; font-weight:700; font-size:15px;
                        flex-shrink:0;">{num}</div>
            <div>
                <div style="font-weight:600; color:#0d4f3c; margin-bottom:4px;">
                    {icon} {title}
                </div>
                <div style="color:#2d6b57; font-size:14px; line-height:1.6;">{desc}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Giải thích chỉ số ──
    st.subheader("🔬 Giải thích các chỉ số đầu vào")

    indicators = {
        "🩸 Glucose": ("Đường huyết lúc đói", "< 100 mg/dL", "100–125 mg/dL", "> 126 mg/dL"),
        "💓 Huyết áp": ("Huyết áp tâm trương", "< 80 mmHg", "80–89 mmHg", "≥ 90 mmHg"),
        "⚖️ BMI": ("Chỉ số khối cơ thể", "18.5 – 24.9", "25 – 29.9", "≥ 30"),
        "💉 Insulin": ("Insulin huyết thanh 2h", "< 140 μU/mL", "140–199 μU/mL", "≥ 200 μU/mL"),
    }

    col1, col2 = st.columns(2)
    cols = [col1, col2]

    for i, (name, (desc, normal, pre, danger)) in enumerate(indicators.items()):
        with cols[i % 2]:
            st.markdown(f"""
            <div style="background:#ffffff; border:1px solid #d4ede6; border-radius:12px;
                        padding:16px; margin-bottom:12px;">
                <div style="font-weight:700; color:#0d4f3c; font-size:15px; margin-bottom:8px;">
                    {name}
                </div>
                <div style="color:#5a8a7a; font-size:13px; margin-bottom:10px;">{desc}</div>
                <div style="display:flex; flex-direction:column; gap:4px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="background:#d4edda; color:#155724; border-radius:20px;
                                     padding:2px 10px; font-size:12px; font-weight:500; white-space:nowrap;">
                            ✅ Bình thường
                        </span>
                        <span style="font-size:13px; color:#2d6b57; text-align:right; padding-left:8px;">{normal}</span>
                    </div>
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="background:#fff3cd; color:#856404; border-radius:20px;
                                     padding:2px 10px; font-size:12px; font-weight:500; white-space:nowrap;">
                            ⚠️ Tiền tiểu đường
                        </span>
                        <span style="font-size:13px; color:#856404; text-align:right; padding-left:8px;">{pre}</span>
                    </div>
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="background:#f8d7da; color:#721c24; border-radius:20px;
                                     padding:2px 10px; font-size:12px; font-weight:500; white-space:nowrap;">
                            🚨 Nguy hiểm
                        </span>
                        <span style="font-size:13px; color:#721c24; text-align:right; padding-left:8px;">{danger}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Footer ──
    st.markdown("""
    <div style="text-align:center; color:#5a8a7a; font-size:13px; padding:16px 0;">
        © 2026 AI Healthcare System &nbsp;·&nbsp;
        Được xây dựng với ❤️ bằng Python & Streamlit &nbsp;·&nbsp;
        Chỉ dùng cho mục đích học tập và nghiên cứu
    </div>
    """, unsafe_allow_html=True)