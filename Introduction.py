import streamlit as st

st.set_page_config(
    page_title="Introduction",
    page_icon="👋",
)

st.write("# Welcome! 👋")

st.sidebar.success("Select a demo above.")

st.markdown(
    """
    Welcome to the data visualization of the 'Challenges for Automatic Peer Review Process' database!  
    **👈 Select a visualization from the sidebar**

    ### This project was developed by:    
        - 💡 Gustavo Lúcius Fernandes
        - 💡 Karen Stéfany Martins
        - 💡 Gabriel Lima Canguçu
"""
)
