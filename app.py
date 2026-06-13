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

    # Hiển thị thông báo đang xử lý
    with st.spinner("Đang xử lý ngầm dữ liệu... Xin vui lòng đợi."):
        # Đọc file PDF trực tiếp từ bộ nhớ
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                # Cách 1: Quét văn bản thô để tìm các dãy số seri dài (Bất chấp file lỗi bảng)
                text = page.extract_text()
                if text:
                    # Tìm tất cả các chuỗi số liên tiếp có độ dài từ 10 đến 25 ký tự số
                    # (Định dạng số seri của bạn là chuỗi số dài như 202601185231410001)
                    matches = re.findall(r"\b\d{10,25}\b", text)
                    for match in matches:
                        # Loại bỏ các số đặc biệt không phải số seri nếu cần (Ví dụ số năm quá ngắn)
                        if not match.startswith("0000"):
                            serial_numbers.append(str(match).strip())

                # Cách 2: Quét bảng dự phòng nếu văn bản thô không có dữ liệu
                tables = page.extract_tables()
                for table in tables:
                    if not table or len(table) < 2:
                        continue
                    header = [
                        str(cell).strip().upper() if cell else ""
                        for cell in table[0]
                    ]
                    sn_index = None
                    for index, col_name in enumerate(header):
                        if any(
                            k in col_name
                            for k in [
                                "SN",
                                "S/N",
                                "SERIAL",
                                "SÊ-RI",
                                "SERI",
                                "SỐ MÁY",
                            ]
                        ):
                            sn_index = index
                            break
                    if sn_index is not None:
                        for row in table[1:]:
                            if len(row) > sn_index and row[sn_index]:
                                val = str(row[sn_index]).strip()
                                if val.isdigit() and len(val) >= 10:
                                    serial_numbers.append(val)

        # Tiến hành xử lý và loại bỏ các số trùng lặp
        if serial_numbers:
            serial_numbers = list(dict.fromkeys(serial_numbers))

            # Sắp xếp lại danh sách số seri cho đẹp mắt
            serial_numbers.sort()

            df = pd.DataFrame(serial_numbers, columns=["Serial Number (SN)"])

            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                df.to_excel(writer, index=False)
            buffer.seek(0)

            st.success("🎉 Xử lý ngầm hoàn tất thành công!")

            # Tạo nút bấm Tải file Excel về
            st.download_button(
                label="📥 BẤM VÀO ĐÊ ĐỂ TẢI FILE EXCEL VỀ",
                data=buffer,
                file_name="danh_sach_seri_thành_phẩm.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        else:
            st.error(
                "Hệ thống không tìm thấy bất kỳ dãy số seri hợp lệ nào trong tệp này. Vui lòng kiểm tra lại file PDF."
            )