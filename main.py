import streamlit.web.cli as stcli
import os, sys

def resolve_path(path):
    if getattr(sys, "frozen", False):
        # If the 'frozen' flag is set, we are in bundled-app mode!
        basedir = sys._MEIPASS
    else:
        # Normal development mode
        basedir = os.path.dirname(__file__)
    return os.path.join(basedir, path)

if __name__ == "__main__":
    # Point to the bundled app.py
    app_path = resolve_path("streamlit_app.py")
    
    # Mock the command line arguments
    sys.argv = [
        "streamlit",
        "run",
        app_path,
        "--global.developmentMode=false",
    ]
    
    # Run the Streamlit CLI
    sys.exit(stcli.main())