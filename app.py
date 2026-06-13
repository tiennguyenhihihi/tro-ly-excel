import re
import pdfplumber
import pandas as pd
import streamlit as st
from fpdf import FPDF

# Cấu hình giao diện trang web
st.set_page_config(page_title="Trợ lý Xuất Số Seri sang PDF", layout="centered")

st.title("🛡️ Trợ lý Trích xuất và Xuất Số Seri sang PDF")
st.write("Hệ thống tự động đọc cột SN và trả về file PDF chứa danh sách số seri sạch.")

# Tạo nút cho nhân viên tải file PDF gốc lên
uploaded_file = st.file_uploader("Kéo và thả hoặc bấm để tải file PDF gốc vào đây", type=["pdf"])

if uploaded_file is not None:
    serial_numbers = []

    with st.spinner("🚀 Đang trích xuất số seri từ cột SN... Vui lòng đợi."):
        try:
            # Dùng pdfplumber để đọc dữ liệu văn bản thô
            with pdfplumber.open(uploaded_file) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        # Tìm toàn bộ các cụm số liên tiếp
                        raw_matches = re.findall(r'\d+', text)
                        for item in raw_matches:
                            clean_num = str(item).strip()
                            # Chỉ lấy đúng các dãy số seri có độ dài 18 chữ số của bạn
                            if len(clean_num) == 18:
                                serial_numbers.append(clean_num)
        except Exception as e:
            st.error(f"Lỗi hệ thống khi đọc file: {str(e)}")

    # Tiến hành gom dữ liệu và xuất file PDF mới
    if serial_numbers:
        # Lọc trùng và sắp xếp thứ tự
        serial_numbers = list(dict.fromkeys(serial_numbers))
        serial_numbers.sort()

        # --- KHỞI TẠO VÀ TẠO FILE PDF MỚI ---
        pdf_output = FPDF()
        pdf_output.add_page()
        
        # Cấu hình font chữ hệ thống mặc định (Helvetica) để không bị lỗi chữ
        pdf_output.set_font("Helvetica", "B", 16)
        pdf_output.cell(0, 10, "DANH SACH SO SERI (SN) MOI TRICH XUAT", ln=True, align="C")
        pdf_output.ln(10) # Xuống dòng
        
        # Tạo bảng danh sách số seri trong PDF mới
        pdf_output.set_font("Helvetica", "B", 12)
        pdf_output.cell(40, 10, "STT", border=1, align="C")
        pdf_output.cell(100, 10, "Serial Number (SN)", border=1, align="C")
        pdf_output.ln()
        
        pdf_output.set_font("Helvetica", "", 12)
        for i, sn in enumerate(serial_numbers, 1):
            pdf_output.cell(40, 8, str(i), border=1, align="C")
            pdf_output.cell(100, 8, str(sn), border=1, align="C")
            pdf_output.ln()

        # Xuất dữ liệu PDF ra bộ nhớ đệm ẩn
        pdf_bytes = pdf_output.output()

        st.success(f"🎉 Đã trích xuất thành công {len(serial_numbers)} số seri!")

        # Tạo nút bấm lớn để tải FILE PDF THÀNH PHẨM về máy
        st.download_button(
            label="📄 BẤM VÀO ĐÂY ĐỂ TẢI FILE PDF SỐ SERI VỀ",
            data=bytes(pdf_bytes),
            file_name="danh_sach_so_seri_thanh_pham.pdf",
            mime="application/pdf"
        )
    else:
        st.error("Hệ thống không tìm thấy số seri 18 chữ số nào hợp lệ. Vui lòng kiểm tra lại file PDF.")