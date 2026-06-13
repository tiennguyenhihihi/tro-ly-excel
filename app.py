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

    with st.spinner("🚀 Đang xử lý bóc tách và làm sạch số seri... Vui lòng đợi."):
        try:
            # Dùng pdfplumber để đọc dữ liệu từ file
            with pdfplumber.open(uploaded_file) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    
                    if text:
                        # GIẢI PHÁP TRIỆT ĐỂ: Tìm tất cả các chuỗi chữ số xuất hiện trong văn bản
                        # Bất chấp việc chuỗi số bị dính dấu ngoặc kép, dấu phẩy hay ký tự xuống dòng \n
                        raw_matches = re.findall(r'\d+', text)
                        
                        for item in raw_matches:
                            # Làm sạch hoàn toàn, chỉ giữ lại ký tự số
                            clean_num = str(item).strip()
                            
                            # Kiểm tra nếu đúng là dãy số seri 18 chữ số của công ty bạn
                            if len(clean_num) == 18:
                                serial_numbers.append(clean_num)
                                    
        except Exception as e:
            st.error(f"Lỗi hệ thống khi giải mã file: {str(e)}")

    # Tiến hành gom dữ liệu và xuất file Excel
    if serial_numbers:
        # Loại bỏ các số trùng lặp
        serial_numbers = list(dict.fromkeys(serial_numbers))
        
        # Sắp xếp danh sách số seri theo thứ tự tăng dần từ nhỏ đến lớn
        serial_numbers.sort()

        # Đút dữ liệu vào bảng pandas
        df = pd.DataFrame(serial_numbers, columns=["Serial Number (SN)"])

        # Ghi ngầm vào bộ nhớ đệm dưới dạng file Excel
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        buffer.seek(0)

        st.success(f"🎉 Xuất file thành công! Đã tìm thấy {len(serial_numbers)} số seri hợp lệ.")

        # Tạo nút bấm lớn cho nhân viên tải file Excel thành phẩm về máy
        st.download_button(
            label="📥 BẤM VÀO ĐÂY ĐỂ TẢI FILE EXCEL VỀ",
            data=buffer,
            file_name="danh_sach_seri_chinh_thuc.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.error("Hệ thống vẫn chưa bắt được số seri. Vui lòng kiểm tra lại cấu trúc file PDF.")