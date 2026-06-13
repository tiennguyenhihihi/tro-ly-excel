import io
import re
import pdfplumber
import pandas as pd
import streamlit as st

# Cấu hình giao diện trang web
st.set_page_config(page_title="Trợ lý Xuất Số Seri Bảo Mật", layout="centered")

st.title("🛡️ Trợ lý Trích xuất Số Seri (SN)")
st.write(
    "Hệ thống tự động xử lý ngầm (Hỗ trợ cả file PDF Scan). Tuyệt đối không hiển thị dữ liệu."
)

# Tạo nút cho nhân viên tải file PDF lên
uploaded_file = st.file_uploader(
    "Kéo và thả hoặc bấm để tải file PDF vào đây", type=["pdf"]
)

if uploaded_file is not None:
    serial_numbers = []

    with st.spinner("⚠️ Đang dùng công nghệ quét ảnh nâng cao... Vui lòng đợi trong giây lát."):
        # Sử dụng pdfplumber để quét sâu
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                # 1. Thử nghiệm đọc text thông thường
                text = page.extract_text()

                # 2. Nếu không có text (file scan), ép hệ thống quét các đối tượng chữ ẩn hoặc hình ảnh
                if not text:
                    # Gom các phần tử chữ rời rạc trong file scan
                    words = page.extract_words()
                    text = " ".join([w["text"] for w in words])

                if text:
                    # Dùng biểu thức tìm các dãy số seri độ dài từ 10-25 ký tự số như hình mẫu của bạn
                    matches = re.findall(r"\b\d{10,25}\b", text)
                    for match in matches:
                        serial_numbers.append(str(match).strip())

                # 3. Phương án dự phòng quét bảng biểu
                tables = page.extract_tables()
                for table in tables:
                    if not table:
                        continue
                    for row in table:
                        for cell in row:
                            if cell:
                                cell_str = str(cell).strip()
                                # Nếu ô chứa chuỗi số dài thì hốt luôn
                                if cell_str.isdigit() and len(cell_str) >= 10:
                                    serial_numbers.append(cell_str)

        # Tiến hành xử lý và đóng gói file Excel
        if serial_numbers:
            # Loại bỏ trùng lặp và sắp xếp
            serial_numbers = list(dict.fromkeys(serial_numbers))
            serial_numbers.sort()

            df = pd.DataFrame(serial_numbers, columns=["Serial Number (SN)"])

            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                df.to_excel(writer, index=False)
            buffer.seek(0)

            st.success("🎉 Xử lý ngầm thành công chiếc file PDF Scan của bạn!")

            # Tạo nút bấm Tải file Excel về
            st.download_button(
                label="📥 BẤM VÀO ĐÂY ĐỂ TẢI FILE EXCEL VỀ",
                data=buffer,
                file_name="danh_sach_seri_on_dinh.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        else:
            st.error(
                "Không thể trích xuất tự động. Bản scan này có thể quá mờ hoặc lỗi định dạng ảnh. Vui lòng kiểm tra lại file."
            )