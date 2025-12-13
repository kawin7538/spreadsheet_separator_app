import io
import os
from typing import List
import tempfile
import zipfile
import streamlit as st
import pandas as pd

def process_one_sheet_to_many_files(excel_file: pd.ExcelFile, selected_sheet_name: str, selected_column: str, len_unique_entity: int) -> str:
    progress_bar = st.progress(0, text="Extraction in progress...")
    selected_df = excel_file.parse(selected_sheet_name)

    os.makedirs("spreadsheet_separator_output/", exist_ok=True)

    output_filepath = os.path.join("spreadsheet_separator_output", "output.zip")

    with zipfile.ZipFile(output_filepath, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zf:

        for idx, (group_name, data) in enumerate(selected_df.groupby(selected_column)):
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                data.to_excel(writer, index=False, sheet_name=str(group_name))

            zf.writestr(f"{str(group_name).replace("/", "_")}.xlsx", buffer.getvalue())

            progress_bar.progress(value=(idx+1)/len_unique_entity, text=f"Extraction in progress ({idx+1} out of {len_unique_entity} sheet(s))...")

    progress_bar.empty()

    return output_filepath

def process_many_sheets_to_many_files(excel_file: pd.ExcelFile) -> str:
    progress_bar = st.progress(0, text="Extraction in progress...")
    list_sheet_names = excel_file.sheet_names

    os.makedirs("spreadsheet_separator_output/", exist_ok=True)

    output_filepath = os.path.join("spreadsheet_separator_output", "output.zip")

    with zipfile.ZipFile(output_filepath, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zf:

        for idx in range(len(list_sheet_names)):
            selected_df = excel_file.parse(list_sheet_names[idx])
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
                selected_df.to_excel(writer, index=False, sheet_name=list_sheet_names[idx])

            zf.writestr(f"{list_sheet_names[idx].replace("/", "_")}.xlsx", buffer.getvalue())

            progress_bar.progress(value=(idx+1)/len(list_sheet_names), text=f"Extraction in progress ({idx+1} out of {len(list_sheet_names)} sheet(s))...")

    progress_bar.empty()

    return output_filepath

def main():
    st.header("Spreadsheet Separator App")

    uploaded_file = st.file_uploader(label="Upload Excel File", accept_multiple_files=False, type=['xlsx'])
    if uploaded_file is not None:
        excel_file = pd.ExcelFile(uploaded_file, engine='openpyxl')

        list_sheet_names = excel_file.sheet_names
        with st.expander(f"`{len(list_sheet_names)}` sheet(s) found, See Data Preview"):
            inspected_sheet_name = st.selectbox(label="Select Sheet Name to inspect", options=list_sheet_names, index=0)
            inspected_df = excel_file.parse(inspected_sheet_name, nrows=5)
            st.write("First 5 rows preview:")
            st.dataframe(inspected_df)

        st.subheader("Configurations")

        if len(excel_file.sheet_names)==1:
            list_separation_option = ["1 Sheet to Many Sheets in one file", "1 Sheet to Many Files"]
        else:
            list_separation_option = ["1 Sheet to Many Sheets in one file", "1 Sheet to Many Files", "Many Sheets to Many Files"]
        
        separation_option = st.radio(label="Select Separation Option", options=list_separation_option, index=None)

        if separation_option == "Many Sheets to Many Files":
            list_sheet_names = excel_file.sheet_names
            st.subheader("Summary")
            st.write(len(list_sheet_names), "sheet(s) from `", uploaded_file.name,"` will be extracted into", len(list_sheet_names), "file(s).")
            st.write("Please Proceed to continue")
            proceed_button = st.button("Proceed", type='primary')

            if proceed_button:
                output_filepath = process_many_sheets_to_many_files(excel_file=excel_file)

                if output_filepath is not None:
                    st.success("Extraction Completed")
                    st.subheader("Final Output")
                    with open(output_filepath, "rb") as fp:
                        st.download_button("Download Extracted File", fp, "output.zip", mime="application/zip", on_click='ignore', type='primary')

        elif separation_option in ["1 Sheet to Many Sheets in one file", "1 Sheet to Many Files"]:
            if len(list_sheet_names)==1:
                selected_sheet_name = st.selectbox("Select Sheet Name to Proceed", options=list_sheet_names, index=0, disabled=True)
            else:
                selected_sheet_name = st.selectbox("Select Sheet Name to Proceed", options=list_sheet_names, index=None)

            if selected_sheet_name is not None:
                list_columns = excel_file.parse(selected_sheet_name, nrows=1).columns
                selected_column = st.selectbox("Select Column to Proceed", options=list_columns, index=None)

                if selected_column is not None:
                    len_unique_entity = excel_file.parse(selected_sheet_name, usecols=[selected_column])[selected_column].nunique()
                    st.subheader("Summary")
                    st.write("Sheet `", selected_sheet_name, "` from `", uploaded_file.name,"` will be extracted by `", selected_column, "` into", len_unique_entity, "file(s)." if separation_option=="1 Sheet to Many Files" else "sheet(s)")
                    st.write("Please Proceed to continue")
                    proceed_button = st.button("Proceed", type='primary')

                    if proceed_button:
                        if separation_option == "1 Sheet to Many Files":
                            output_filepath = process_one_sheet_to_many_files(excel_file=excel_file, selected_sheet_name=selected_sheet_name, selected_column=selected_column, len_unique_entity=len_unique_entity)
                            if output_filepath is not None:
                                st.success("Extraction Completed")
                                st.subheader("Final Output")
                                with open(output_filepath, "rb") as fp:
                                    st.download_button("Download Extracted File", fp, "output.zip", mime="application/zip", on_click='ignore', type='primary')
                        else:
                            output_filepath = ""

if __name__ == '__main__':
    main()