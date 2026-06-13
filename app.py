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

    # Hiển thị thông báo đang xử lý
    with st.spinner("Đang xử lý ngầm dữ liệu... Xin vui lòng đợi."):
        # Đọc file PDF trực tiếp từ bộ nhớ
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    if not table or len(table) < 2:
                        continue

                    # BỘ DÒ TÌM THÔNG MINH: Đọc dòng đầu tiên để quét tất cả các kiểu đặt tên tiêu đề cột trên đời
                    header = [
                        str(cell).strip().upper() if cell else ""
                        for cell in table[0]
                    ]
                    sn_column_index = None

                    for index, col_name in enumerate(header):
                        # Quét mọi từ khóa có thể xảy ra (thêm SERIAL, SỐ MÁY, SỐ SÊ RI, NO, CODE...)
                        if any(
                            keyword in col_name
                            for keyword in [
                                "SN",
                                "S/N",
                                "SERIAL",
                                "SÊ RI",
                                "SÊ-RI",
                                "SERI",
                                "SỐ MÁY",
                                "SỐ BAO",
                                "SER.NO",
                                "SỐ CHẾ TẠO",
                            ]
                        ):
                            sn_column_index = index
                            break

                    # Trích xuất dữ liệu ngầm nếu tìm thấy bất kỳ cột nào khớp
                    if sn_column_index is not None:
                        for row in table[1:]:
                            if len(row) > sn_column_index:
                                sn_value = row[sn_column_index]
                                if sn_value:
                                    # Loại bỏ tiêu đề bị lặp lại nếu có
                                    sn_str = str(sn_value).strip()
                                    if sn_str.upper() not in [
                                        "SN",
                                        "S/N",
                                        "SERIAL",
                                    ]:
                                        serial_numbers.append(sn_str)

        # Nếu tìm thấy số seri, chuyển thẳng thành file Excel
        if serial_numbers:
            # Loại bỏ các số seri bị trùng nhau để file Excel sạch đẹp nhất
            serial_numbers = list(dict.fromkeys(serial_numbers))

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
                "Hệ thống chưa nhận diện được cột Số Seri. Bạn hãy kiểm tra lại xem file PDF có đúng là dạng bảng văn bản không nhé."
            )