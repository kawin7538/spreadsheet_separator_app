# Spreadsheet Separator App

## Features
- Split from one sheet into multiple sheets in one file
- Split from one sheet into multiple files
- Split from multiple sheets in one file into multiple files

## How to easily run on dev
`streamlit run streamlit_app.py`

## How to convert to exe
`pyinstaller main.py --onedir --additional-hooks-dir=./hooks --collect-all streamlit --hidden-import "streamlit.web.cli" --add-data "streamlit_app.py;." --add-data ".streamlit/config.toml;.streamlit/" --clean --noconfirm`