from PyInstaller.utils.hooks import copy_metadata

# This ensures all of Streamlit's version info and dependencies are copied
datas = copy_metadata('streamlit')