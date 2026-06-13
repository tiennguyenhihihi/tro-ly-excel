import streamlit as st
import pdfplumber
import pandas as pd
from io import BytesIO

st.set_page_config(
    page_title="PDF → Excel Serial Extractor",
    page_icon="📄",
    layout="centered"
)

st.title("📄 PDF → Excel Serial Extractor")
st.write("Kéo thả file PDF, hệ thống sẽ tìm cột SN và xuất Excel.")

uploaded_file = st.file_uploader(
    "Chọn file PDF",
    type=["pdf"]
)

def extract_sn(pdf_file):
    serials = []

    with pdfplumber.open(pdf_file) as pdf:

        for page in pdf.pages:

            tables = page.extract_tables()

            for table in tables:

                if not table or len(table) < 2:
                    continue

                headers = [
                    str(x).strip().upper()
                    if x else ""
                    for x in table[0]
                ]

                if "SN" not in headers:
                    continue

                sn_index = headers.index("SN")

                for row in table[1:]:

                    if (
                        row
                        and len(row) > sn_index
                        and row[sn_index]
                    ):

                        serials.append(
                            str(row[sn_index]).strip()
                        )

    serials = list(dict.fromkeys(serials))

    return serials

if uploaded_file:

    with st.spinner("Đang đọc PDF..."):

        serials = extract_sn(uploaded_file)

        if len(serials) == 0:

            st.error(
                "Không tìm thấy cột SN trong PDF."
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
                label="📥 Tải file Excel",
                data=excel_buffer,
                file_name="SN_Output.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )