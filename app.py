import streamlit as st
import pandas as pd
import fitz
import pytesseract
from PIL import Image
import re
from io import BytesIO
import tempfile

st.set_page_config(
    page_title="PDF Serial Extractor",
    page_icon="📄",
    layout="centered"
)

st.title("📄 PDF → Excel Serial Extractor")

st.write(
    "Kéo thả file PDF vào đây, hệ thống sẽ tự động đọc cột SN và xuất Excel."
)

uploaded_file = st.file_uploader(
    "Chọn PDF",
    type=["pdf"]
)

def extract_serials(pdf_path):
    serials = []

    doc = fitz.open(pdf_path)

    for page in doc:
        pix = page.get_pixmap(
            matrix=fitz.Matrix(3, 3),
            alpha=False
        )

        img = Image.fromarray(
            __import__("numpy").frombuffer(
                pix.samples,
                dtype="uint8"
            ).reshape(
                pix.height,
                pix.width,
                pix.n
            )
        )

        text = pytesseract.image_to_string(
            img,
            config="--psm 6"
        )

        found = re.findall(
            r"\b\d{10,25}\b",
            text
        )

        serials.extend(found)

    doc.close()

    # bỏ trùng
    serials = list(dict.fromkeys(serials))

    return serials

if uploaded_file:

    with st.spinner("Đang xử lý PDF..."):

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as tmp:
            tmp.write(uploaded_file.read())
            pdf_path = tmp.name

        serials = extract_serials(pdf_path)

        df = pd.DataFrame({
            "SN": serials
        })

        excel_buffer = BytesIO()

        with pd.ExcelWriter(
            excel_buffer,
            engine="openpyxl"
        ) as writer:
            df.to_excel(
                writer,
                index=False,
                sheet_name="Serials"
            )

        excel_buffer.seek(0)

    st.success(
        f"Tìm thấy {len(serials)} serial."
    )

    st.dataframe(df.head(20))

    st.download_button(
        label="📥 Tải Excel",
        data=excel_buffer,
        file_name="SN_Output.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )