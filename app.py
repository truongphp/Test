import streamlit as st
import json
import os

st.title("Quản lý chi tiêu")

if os.path.exists("so_hoan_chinh.json"):
    with open("so_hoan_chinh.json", "r", encoding="utf-8") as f:
        ds_ct = json.load(f)
else:
    ds_ct = []

menu = st.sidebar.radio("Chọn thao tác: ", [
    " 1. Thêm khoản chi mới", 
    " 2. Xem toàn bộ danh sách & tổng tiền", 
    " 3. Xoá khoản chi tiêu", 
    " 4. Sửa khoản chi tiêu"
])

if menu == " 1. Thêm khoản chi mới":
    cot1, cot2 = st.columns(2)
    with cot1:
        ten_moi = st.text_input("Nhập khoản chi mới: ")
    with cot2:
        tien_moi = st.number_input("Nhập số tiền: ", step=1000)
        if st.button("Lưu khoản chi"):
            ds_ct.append({"ten": ten_moi, "tien": tien_moi})
            with open("so_hoan_chinh.json", "w", encoding="utf-8") as f:
                json.dump(ds_ct, f, ensure_ascii=False, indent=2)
            st.success("Đã thêm")

elif menu == " 2. Xem toàn bộ danh sách & tổng tiền":
    if len(ds_ct) == 0:
        st.warning("Danh sách trống!")
    else:
        tong = 0
        for stt, i in enumerate(ds_ct, start=1):
            tong += i['tien']
            st.write(f"{stt}. Mục: {i['ten']} | Số tiền: {i['tien']}đ")
        st.info(f"Tổng số tiền: {tong}đ")

elif menu == " 3. Xoá khoản chi tiêu":
    if len(ds_ct) == 0:
        st.warning("Danh sách trống không có gì để xóa!")
    else:
        xoa = int(st.number_input("Hãy nhập số vị trí muốn xoá: ", step=1)) - 1
        if st.button("Xác nhận xoá"):
            if 0 <= xoa < len(ds_ct):
                ds_ct.pop(xoa)
                with open("so_hoan_chinh.json", "w", encoding="utf-8") as f:
                    json.dump(ds_ct, f, ensure_ascii=False, indent=2)
                st.success("Đã xoá xong!")
            else:
                st.warning("Vị trí không tồn tại!")

elif menu == " 4. Sửa khoản chi tiêu":
    if len(ds_ct) == 0:
        st.warning("Danh sách trống không có gì để sửa!")
    else:
        sua = int(st.number_input("Nhập vị trí sửa: ", step=1)) - 1
        ten_moi = st.text_input("Hãy nhập tên mới: ")
        tien_moi = st.number_input("Hãy nhập số tiền: ", step=1)
        if st.button("Xác nhận sửa"):
            if 0 <= sua < len(ds_ct):
                ds_ct[sua]['ten'] = ten_moi
                ds_ct[sua]['tien'] = tien_moi
                with open("so_hoan_chinh.json", "w", encoding="utf-8") as f:
                    json.dump(ds_ct, f, ensure_ascii=False, indent=2)
                st.success("Đã sửa thành công")
            else:
                st.warning("Vị trí không tồn tại!")
