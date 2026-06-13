import io
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
    sn_column_index = None

    # Hiển thị thông báo đang xử lý
    with st.spinner("Đang xử lý ngầm dữ liệu... Xin vui lòng đợi."):
        # Đọc file PDF trực tiếp từ bộ nhớ
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    if not table or len(table) < 2:
                        continue

                    # Tìm cột SN
                    header = [
                        str(cell).strip().upper() if cell else ""
                        for cell in table[0]
                    ]
                    for index, col_name in enumerate(header):
                        if col_name in [
                            "SN",
                            "S/N",
                            "SERIAL NUMBER",
                            "SERIAL NO",
                            "SỐ SÊ-RI (SN)",
                        ]:
                            sn_column_index = index
                            break

                    # Trích xuất dữ liệu ngầm
                    if sn_column_index is not None:
                        for row in table[1:]:
                            if len(row) > sn_column_index:
                                sn_value = row[sn_column_index]
                                if sn_value:
                                    serial_numbers.append(str(sn_value).strip())

        # Nếu tìm thấy số seri, chuyển thẳng thành file Excel
        if serial_numbers:
            df = pd.DataFrame(serial_numbers, columns=["Serial Number (SN)"])

            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                df.to_excel(writer, index=False)
            buffer.seek(0)

            st.success("🎉 Xử lý ngầm hoàn tất thành công!")

            # Tạo nút bấm Tải file Excel về
            st.download_button(
                label="📥 BẤM VÀO ĐÂY ĐỂ TẢI FILE EXCEL VỀ",
                data=buffer,
                file_name="danh_sach_seri_thành_phẩm.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        else:
            st.error(
                "Không tìm thấy cột 'SN' hoặc dữ liệu số seri trong file PDF này."
            )