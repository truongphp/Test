import random
import streamlit as st

st.set_page_config(page_title="Game Đoán Số", page_icon="🎲")
st.title("🎲 Trò Chơi Đoán Số Bí Mật")
st.write("Máy tính đã chọn một số ngẫu nhiên từ **1 đến 100**. Bạn đoán xem đó là số nào nhé!")

# Khởi tạo trạng thái trò chơi trong session_state
if "secret" not in st.session_state:
    st.session_state.secret = random.randint(1, 100)
    st.session_state.attempts = 0

# Ô nhập số và nút đoán
guess = st.number_input("Nhập số bạn đoán:", min_value=1, max_value=100, step=1)

col1, col2 = st.columns(2)

if col1.button("🔍 Kiểm tra", use_container_width=True):
    st.session_state.attempts += 1
    if guess < st.session_state.secret:
        st.warning(f"🔼 Số bí mật **lớn hơn** {guess}! (Lần thử: {st.session_state.attempts})")
    elif guess > st.session_state.secret:
        st.warning(f"🔽 Số bí mật **nhỏ hơn** {guess}! (Lần thử: {st.session_state.attempts})")
    else:
        st.success(f"🎉 Chính xác! Số bí mật là **{st.session_state.secret}**. Bạn mất **{st.session_state.attempts}** lần đoán!")
        st.balloons()

if col2.button("🔄 Chơi lại", use_container_width=True):
    st.session_state.secret = random.randint(1, 100)
    st.session_state.attempts = 0
    st.rerun()
