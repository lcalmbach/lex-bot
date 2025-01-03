import streamlit as st
from streamlit_option_menu import option_menu
import lex_bot


# more icons: https://icons.getbootstrap.com/?q=image
menu_icons = ["house", "bank", "chat-dots"]

__version__ = "0.0.5"
__author__ = "Lukas Calmbach"
__author_email__ = "lcalmbach@gmail.com"
VERSION_DATE = "2025-01-03"
APP_NAME = "Lex-Bot"
GIT_REPO = "https://github.com/lcalmbach/lex-bot"
SOURCE_URL = "https://data.bs.ch/explore/dataset/100354/"

menu_options = ["Über die App", "Gesetze", "Lex-Chat"]

APP_INFO = f"""<div style="background-color:silver; padding: 10px;border-radius: 15px; border:solid 1px grey;">
    <small>App von <a href="mailto:{__author_email__}">{__author__}</a><br>
    Version: {__version__} ({VERSION_DATE})<br>
    Quelle: <a href="{SOURCE_URL}">data.bs</a><br>
    <a href="{GIT_REPO}">git-repo</a></small></div>
    """
APP_ICON = "⚖️"

def init():
    """
    Initializes the Streamlit application with specific configuration settings.

    This function sets the page configuration for the Streamlit app, including
    the page title, page icon, layout, and initial sidebar state.

    Parameters:
    None

    Returns:
    None
    """
    st.set_page_config(
        page_title="Lex-Bot",
        page_icon=APP_ICON,
        layout="wide",
        initial_sidebar_state="expanded",
    )
    

def main():
    """
    Main function to initialize the application and handle the sidebar menu actions.

    This function performs the following steps:
    1. Initializes the application by calling the `init()` function.
    2. Checks if "lex" is in the Streamlit session state; if not, it initializes a new `Lex` bot instance.
    3. Creates a sidebar with a title and an option menu for navigation.
    4. Determines the selected menu action and calls the corresponding method on the `Lex` bot instance:
        - `show_info()` for the first menu option.
        - `show_stats()` for the second menu option.
        - `show_chat()` for the third menu option.
    5. Adds additional information to the sidebar using markdown.

    Note:
        - `st` refers to the Streamlit module.
        - `lex_bot` is a module containing the `Lex` class.
        - `APP_NAME`, `APP_ICON`, `menu_options`, `menu_icons`, and `APP_INFO` are predefined constants.

    Returns:
        None
    """
    init()
    if "lex" not in st.session_state:
        st.session_state.lex = lex_bot.Lex()
    with st.sidebar:
        st.sidebar.title(f"{APP_NAME} {APP_ICON}")
        menu_action = option_menu(
            None,
            menu_options,
            icons=menu_icons,
            menu_icon="cast",
            default_index=0,
        )
    index = menu_options.index(menu_action)
    if index == 0:
        st.session_state.lex.show_info()
    if index == 1:
        st.session_state.lex.show_stats()
    if index == 2:
        st.session_state.lex.show_chat()

    st.sidebar.markdown(APP_INFO, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
