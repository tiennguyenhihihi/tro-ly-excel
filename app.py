import streamlit as st
import fitz
import pytesseract
import pandas as pd
import re
import numpy as np

from PIL import Image
from io import BytesIO

st.set_page_config(
    page_title="PDF -> Excel Serial Extractor",
    page_icon="📄"
)

st.title("📄 PDF → Excel Serial Extractor")

st.write(
    "Kéo thả file PDF, hệ thống tự động đọc Serial Number và xuất Excel."
)

uploaded_file = st.file_uploader(
    "Chọn file PDF",
    type=["pdf"]
)

def extract_serials(pdf_file):

    serials = []

    pdf_bytes = pdf_file.read()

    doc = fitz.open(
        stream=pdf_bytes,
        filetype="pdf"
    )

    for page in doc:

        pix = page.get_pixmap(
            matrix=fitz.Matrix(3, 3),
            alpha=False
        )

        img = Image.fromarray(
            np.frombuffer(
                pix.samples,
                dtype=np.uint8
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

        serials = extract_serials(
            uploaded_file
        )

    if len(serials) == 0:

        st.error(
            "Không tìm thấy serial nào."
        )

    else:

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
                sheet_name="SN"
            )

        excel_buffer.seek(0)

        st.success(
            f"Tìm thấy {len(serials)} Serial Number"
        )

        st.dataframe(df.head(20))

        st.download_button(
            "📥 Tải file Excel",
            excel_buffer,
            file_name="SN_Output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )