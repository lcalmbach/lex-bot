import streamlit as st
from streamlit_option_menu import option_menu
import lex_bot


# https://icons.getbootstrap.com/?q=image
menu_icons = ["house", "bank", "chat-dots"]

__version__ = "0.0.1"
__author__ = "Lukas Calmbach"
__author_email__ = "lcalmbach@gmail.com"
VERSION_DATE = "2024-12-28"
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
    st.set_page_config(
        page_title="Lex-Bot",
        page_icon=APP_ICON,
        layout="wide",
        initial_sidebar_state="expanded",
    )


def main():
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
