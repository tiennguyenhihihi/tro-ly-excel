import io
import re
import pdfplumber
import pandas as pd
import streamlit as st

# Cấu hình giao diện trang web
st.set_page_config(page_title="Trợ lý Xuất Số Seri Bảo Mật", layout="centered")

st.title("🛡️ Trợ lý Trích xuất Số Seri (SN)")
st.write("Hệ thống tự động xử lý ngầm. Tuyệt đối không hiển thị dữ liệu ra màn hình.")

# Tạo nút cho nhân viên tải file PDF lên
uploaded_file = st.file_uploader(
    "Kéo và thả hoặc bấm để tải file PDF vào đây", type=["pdf"]
)

if uploaded_file is not None:
    serial_numbers = []

    with st.spinner("🚀 Đang trích xuất danh sách số seri... Vui lòng đợi."):
        try:
            # Dùng pdfplumber mở trực tiếp file 
            with pdfplumber.open(uploaded_file) as pdf:
                for page in pdf.pages:
                    # Lấy văn bản của từng trang dưới dạng thô
                    text = page.extract_text()
                    
                    if text:
                        # BỘ LỌC CHÍNH XÁC: Tìm tất cả các chuỗi số liên tiếp có độ dài đúng từ 15 đến 20 ký tự số
                        # Vì số seri của bạn là 202601185231410005... (độ dài 18 ký tự số)
                        matches = re.findall(r'\b\d{15,20}\b', text)
                        for match in matches:
                            serial_numbers.append(str(match).strip())
                            
        except Exception as e:
            st.error(f"Lỗi hệ thống khi giải mã file: {str(e)}")

        # Tiến hành xử lý và đóng gói file Excel
        if serial_numbers:
            # Loại bỏ các số trùng lặp nếu có
            serial_numbers = list(dict.fromkeys(serial_numbers))
            
            # Sắp xếp danh sách số seri theo thứ tự từ nhỏ đến lớn
            serial_numbers.sort()

            # Đút dữ liệu vào cột
            df = pd.DataFrame(serial_numbers, columns=["Serial Number (SN)"])

            # Ghi ngầm vào bộ nhớ đệm
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            buffer.seek(0)

            st.success(f"🎉 Xử lý thành công! Đã tìm thấy {len(serial_numbers)} số seri.")

            # Nút bấm tải file thành phẩm về máy
            st.download_button(
                label="📥 BẤM VÀO ĐÂY ĐỂ TẢI FILE EXCEL VỀ",
                data=buffer,
                file_name="danh_sach_seri_thanh_pham.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.error("Hệ thống không tìm thấy số seri nào đạt định dạng. Vui lòng kiểm tra lại file PDF.")