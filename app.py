import streamlit as st
import pandas as pd
import os
import pandas as pd
import gspread
from gspread_dataframe import get_as_dataframe, set_with_dataframe

def local_css(css_code):
    st.markdown(f'<style>{css_code}</style>', unsafe_allow_html=True)

local_css("""
    body {
        background-color: #f5f6fa;
        color: #2f3640;
        font-family: 'Segoe UI', sans-serif;
    }
    .stButton>button {
        background-color: #4B8BBE;
        color: white;
        padding: 8px 20px;
        border-radius: 10px;
        font-weight: bold;
        margin-top: 10px;
    }
    .stSelectbox, .stTextInput {
        border-radius: 10px;
    }
""")


# Excel file path
EXCEL_PATH = "books.xlsx"

# Load the Excel sheet
@st.cache_data
def load_books():
    if os.path.exists(EXCEL_PATH):
        return pd.read_excel(EXCEL_PATH, sheet_name="BOOKS")
    else:
        return pd.DataFrame(columns=["Titre", "Auteur(s)", "Langue", "Lieu de stockage"])

# Load books
df = load_books()

# App title
st.title("📚 Family Book Library")

# Sidebar menu
with st.sidebar:
    st.markdown(
        """
        <style>
        .sidebar-title {
            font-size: 24px;
            font-weight: bold;
            color: #4B8BBE;
            text-align: center;
            margin-bottom: 20px;
        }
        </style>
        """, unsafe_allow_html=True
    )
    st.markdown("<div class='sidebar-title'>📚 Library Menu</div>", unsafe_allow_html=True)
    menu = st.radio("Choose action:", ["📖 View Books", "🔍 Search", "➕ Add Book", "🗑️ Delete Book"])

# VIEW
if menu == "📖 View Books":
    st.subheader("📚 Book Collection")
    for i, row in df.iterrows():
        with st.container():
            st.markdown(
                f"""
                <div style='
                    background-color: #ffffff;
                    border-radius: 10px;
                    padding: 15px;
                    margin-bottom: 10px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                '>
                    <h4 style='margin-bottom: 5px;'>{row['Titre']}</h4>
                    <p style='margin: 0;'><strong>Author:</strong> {row['Auteur(s)']}</p>
                    <p style='margin: 0;'><strong>Language:</strong> {row['Langue']} &nbsp;&nbsp; <strong>Location:</strong> {row['Lieu de stockage']}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

#SEARCH
elif menu == "🔍 Search":
    st.subheader("Search Library")
    tab1, tab2 = st.tabs(["🔍 By Title / Author", "📊 Raw Table View"])

    with tab1:
        search_term = st.text_input("Enter title keyword:")
        authors = df["Auteur(s)"].dropna().unique().tolist()
        selected_author = st.selectbox("Filter by author (optional)", ["All"] + sorted(authors))

        filtered_df = df

        if search_term:
            filtered_df = filtered_df[filtered_df["Titre"].str.contains(search_term, case=False, na=False)]

        if selected_author != "All":
            filtered_df = filtered_df[filtered_df["Auteur(s)"] == selected_author]

        if not filtered_df.empty:
            for i, row in filtered_df.iterrows():
                with st.container():
                    st.markdown(
                        f"""
                        <div style='
                            background-color: #ffffff;
                            border-radius: 10px;
                            padding: 15px;
                            margin-bottom: 10px;
                            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        '>
                            <h4 style='margin-bottom: 5px;'>{row['Titre']}</h4>
                            <p style='margin: 0;'><strong>Author:</strong> {row['Auteur(s)']}</p>
                            <p style='margin: 0;'><strong>Language:</strong> {row['Langue']} &nbsp;&nbsp; <strong>Location:</strong> {row['Lieu de stockage']}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
        else:
            st.warning("No matching book found.")

    with tab2:
        st.dataframe(df)


# ADD
elif menu == "➕ Add Book":
    st.subheader("Add a New Book")

    title = st.text_input("Book Title")
    author = st.text_input("Author(s)")
    language = st.selectbox("Language", ["FRA", "ENG", "AR"])
    location = st.text_input("Storage Location (e.g. BOX PANINI)")

    if st.button("Add Book"):
        if not title.strip():
            st.warning("Book title is required.")
        elif title in df["Titre"].values:
            st.info("This book already exists.")
        else:
            # Create and append new row
            new_row = {
                "Titre": title,
                "Auteur(s)": author,
                "Langue": language,
                "Lieu de stockage": location
            }
            df.loc[len(df)] = new_row

            # Save to Excel
            df.to_excel(EXCEL_PATH, sheet_name="BOOKS", index=False)

            # 🔁 Clear cache so next view is updated
            st.cache_data.clear()

            st.success(f"✅ '{title}' was added to the library!")
#DELETE
elif menu == "🗑️ Delete Book":
    st.subheader("Delete a Book from the Library")

    if df.empty:
        st.info("Library is empty.")
    else:
        book_titles = df["Titre"].tolist()
        book_to_delete = st.selectbox("Select a book to delete", book_titles)

        confirm = st.checkbox("⚠️ Yes, I’m sure I want to delete this book.")

        if st.button("Delete"):
            if confirm:
                df = df[df["Titre"] != book_to_delete]
                df.to_excel(EXCEL_PATH, sheet_name="BOOKS", index=False)
                st.cache_data.clear()
                st.success(f"🗑️ '{book_to_delete}' was deleted.")
            else:
                st.warning("Please confirm before deleting.")

