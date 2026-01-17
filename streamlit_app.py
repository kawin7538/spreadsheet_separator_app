import io
import os
import zipfile
from datetime import datetime
import streamlit as st
import polars as pl
import fastexcel
import xlsxwriter

def process_one_sheet_to_many_sheets(source_file, selected_sheet_name: str, selected_column: str, len_unique_entity: int) -> str:
    progress_bar = st.progress(0, text="Extraction in progress...")
    
    source_file.seek(0)
    df = pl.read_excel(source_file, sheet_name=selected_sheet_name, engine='calamine')
    df = df.sort(by=selected_column)
    partitioned_data = df.partition_by(selected_column, as_dict=True, maintain_order=True)

    output_filepath = os.path.join("spreadsheet_separator_output", "output.xlsx")

    with xlsxwriter.Workbook(output_filepath) as workbook:
        for idx, (group_name, group_df) in enumerate(partitioned_data.items()):
            safe_sheet_name = group_name[0]
            
            group_df.write_excel(workbook=workbook, worksheet=safe_sheet_name)
            
            progress_bar.progress(value=(idx+1)/len_unique_entity, text=f"Extraction in progress ({idx+1} out of {len_unique_entity} sheet(s))...")

    progress_bar.empty()

    return output_filepath

def process_one_sheet_to_many_files(source_file, selected_sheet_name: str, selected_column: str, len_unique_entity: int) -> str:
    progress_bar = st.progress(0, text="Extraction in progress...")

    source_file.seek(0)
    df = pl.read_excel(source_file, sheet_name=selected_sheet_name, engine='calamine')

    output_filepath = os.path.join("spreadsheet_separator_output", "output.zip")

    partitioned_data = df.partition_by(selected_column, as_dict=True, maintain_order=True)

    with zipfile.ZipFile(output_filepath, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zf:

        for idx, (group_name, group_df) in enumerate(partitioned_data.items()):
            buffer = io.BytesIO()
            
            group_df.write_excel(buffer, worksheet=group_name[0])

            zf.writestr(f"{group_name[0].replace("/", "_")}.xlsx", buffer.getvalue())

            progress_bar.progress(value=(idx+1)/len_unique_entity, text=f"Extraction in progress ({idx+1} out of {len_unique_entity} sheet(s))...")

    progress_bar.empty()

    return output_filepath

def process_many_sheets_to_many_files(source_file, list_sheet_names: list) -> str:
    progress_bar = st.progress(0, text="Extraction in progress...")

    output_filepath = os.path.join("spreadsheet_separator_output", "output.zip")

    with zipfile.ZipFile(output_filepath, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zf:

        for idx, sheet_name in enumerate(list_sheet_names):
            source_file.seek(0)
            df = pl.read_excel(source_file, sheet_name=sheet_name, engine='calamine')
            
            buffer = io.BytesIO()
            df.write_excel(buffer)

            safe_filename = sheet_name.replace("/", "_")
            zf.writestr(f"{safe_filename}.xlsx", buffer.getvalue())

            progress_bar.progress(value=(idx+1)/len(list_sheet_names), text=f"Extraction in progress ({idx+1} out of {len(list_sheet_names)} sheet(s))...")

    progress_bar.empty()

    return output_filepath

def main():
    os.makedirs("spreadsheet_separator_output/", exist_ok=True)

    st.header("Spreadsheet Separator App")

    uploaded_file = st.file_uploader(label="Upload Excel File", accept_multiple_files=False, type=['xlsx'])
    if uploaded_file is not None:
        uploaded_file.seek(0)
        # fastexcel.read_excel returns a reader object that has metadata
        excel_reader = fastexcel.read_excel(uploaded_file.read())
        list_sheet_names = excel_reader.sheet_names

        with st.expander(f"`{len(list_sheet_names)}` sheet(s) found, See Data Preview"):
            inspected_sheet_name = st.selectbox(label="Select Sheet Name to inspect", options=list_sheet_names, index=0)
            uploaded_file.seek(0)
            inspected_df = pl.read_excel(uploaded_file, sheet_name=inspected_sheet_name, engine='calamine')
            st.write("First 5 rows preview:")
            st.dataframe(inspected_df.head(5))

        st.subheader("Configurations")

        if len(list_sheet_names)==1:
            list_separation_option = ["1 Sheet to Many Sheets in one file", "1 Sheet to Many Files"]
        else:
            list_separation_option = ["1 Sheet to Many Sheets in one file", "1 Sheet to Many Files", "Many Sheets to Many Files"]
        
        separation_option = st.radio(label="Select Separation Option", options=list_separation_option, index=None)

        if separation_option == "Many Sheets to Many Files":
            st.subheader("Summary")
            st.write(len(list_sheet_names), "sheet(s) from `", uploaded_file.name,"` will be extracted into", len(list_sheet_names), "file(s).")
            st.write("Please Proceed to continue")
            proceed_button = st.button("Proceed", type='primary')

            if proceed_button:
                output_filepath = process_many_sheets_to_many_files(uploaded_file, list_sheet_names)

                if output_filepath is not None:
                    st.toast("Extraction Completed", icon=":material/check:")
                    st.balloons()
                    st.subheader("Final Output")
                    st.write("Extraction Completed on", datetime.now())
                    with open(output_filepath, "rb") as fp:
                        st.download_button("Download .zip", fp, "output.zip", mime="application/zip", on_click='ignore', type='primary', icon=":material/download:")

        elif separation_option in ["1 Sheet to Many Sheets in one file", "1 Sheet to Many Files"]:
            if len(list_sheet_names)==1:
                selected_sheet_name = st.selectbox("Select Sheet Name to Proceed", options=list_sheet_names, index=0, disabled=True)
            else:
                selected_sheet_name = st.selectbox("Select Sheet Name to Proceed", options=list_sheet_names, index=None)

            if selected_sheet_name is not None:
                uploaded_file.seek(0)
                df_for_cols = pl.read_excel(uploaded_file, sheet_name=selected_sheet_name, engine='calamine')
                list_columns = df_for_cols.columns
                selected_column = st.selectbox("Select Column to Proceed", options=list_columns, index=None)

                if selected_column is not None:
                    len_unique_entity = df_for_cols.select(pl.col(selected_column).n_unique()).item()
                    st.subheader("Summary")
                    st.write("Sheet `", selected_sheet_name, "` from `", uploaded_file.name,"` will be extracted by `", selected_column, "` into", len_unique_entity, "file(s)." if separation_option=="1 Sheet to Many Files" else "sheet(s)")
                    st.write("Please Proceed to continue")
                    proceed_button = st.button("Proceed", type='primary')

                    if proceed_button:
                        if separation_option == "1 Sheet to Many Files":
                            output_filepath = process_one_sheet_to_many_files(uploaded_file, selected_sheet_name, selected_column, len_unique_entity)
                            if output_filepath is not None:
                                st.toast("Extraction Completed", icon=":material/check:")
                                st.balloons()
                                st.subheader("Final Output")
                                st.write("Extraction Completed on", datetime.now())
                                with open(output_filepath, "rb") as fp:
                                    st.download_button("Download .zip", fp, "output.zip", mime="application/zip", on_click='ignore', type='primary', icon=":material/download:")
                        else:
                            output_filepath = process_one_sheet_to_many_sheets(uploaded_file, selected_sheet_name, selected_column, len_unique_entity)
                            if output_filepath is not None:
                                st.toast("Extraction Completed", icon=":material/check:")
                                st.balloons()
                                st.subheader("Final Output")
                                st.write("Extraction Completed on", datetime.now())
                                with open(output_filepath, "rb") as fp:
                                    st.download_button("Download .xlsx", fp, "output.xlsx", mime="application/vnd.ms-excel", on_click='ignore', type='primary', icon=":material/download:")

if __name__ == '__main__':
    main()