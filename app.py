import io
import re
import pandas as pd
from pypdf import PdfReader
import streamlit as st

# Cấu hình giao diện trang web
st.set_page_config(page_title="Trợ lý Xuất Số Seri Bảo Mật", layout="centered")

st.title("🛡️ Trợ lý Trích xuất Số Seri (SN)")
st.write(
    "Hệ thống tự động xử lý ngầm phiên bản ổn định cao. Tuyệt đối không hiển thị dữ liệu."
)

# Tạo nút cho nhân viên tải file PDF lên
uploaded_file = st.file_uploader(
    "Kéo và thả hoặc bấm để tải file PDF vào đây", type=["pdf"]
)

if uploaded_file is not None:
    serial_numbers = []

    with st.spinner("🚀 Đang giải mã dữ liệu PDF ngầm... Vui lòng đợi."):
        try:
            # Sử dụng bộ đọc PdfReader của pypdf để tránh lỗi font mã hóa
            reader = PdfReader(uploaded_file)

            for page in reader.pages:
                text = page.extract_text()

                if text:
                    # Tìm tất cả chuỗi số liên tiếp có độ dài từ 10 đến 25 ký tự
                    matches = re.findall(r"\b\d{10,25}\b", text)
                    for match in matches:
                        serial_numbers.append(str(match).strip())

        except Exception as e:
            st.error(f"Lỗi hệ thống khi đọc tệp: {str(e)}")

        # Tiến hành xử lý và xuất file Excel
        if serial_numbers:
            # Loại bỏ số trùng lặp và sắp xếp thứ tự
            serial_numbers = list(dict.fromkeys(serial_numbers))
            serial_numbers.sort()

            # Đóng gói dữ liệu vào bảng
            df = pd.DataFrame(serial_numbers, columns=["Serial Number (SN)"])

            # Ghi vào bộ nhớ đệm
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                df.to_excel(writer, index=False)
            buffer.seek(0)

            st.success("🎉 Xử lý ngầm hoàn tất thành công!")

            # Nút bấm tải file thành phẩm
            st.download_button(
                label="📥 BẤM VÀO ĐÂY ĐỂ TẢI FILE EXCEL VỀ",
                data=buffer,
                file_name="danh_sach_seri_chinh_thuc.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        else:
            st.error(
                "Hệ thống không tìm thấy số seri nào. Vui lòng kiểm tra lại cấu trúc file PDF của bạn."
            )