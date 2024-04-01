import streamlit as st

from streamlit_sortables import sort_items
from utils import download_images_from_url, download_multiple_files, load_images, load_images_uploaded
import os
import shutil

st.set_page_config(layout="wide")

option = st.selectbox("Select mode", ["From upload", "From URL"], key="mode")
prefixes = st.text_input("Insert prefixes (comma separated)", value="MAIN, PT")
prefixes = prefixes.replace(" ", "").split(",")

files = {}
if option == "From upload":
    uploaded_files = st.file_uploader("Choose a file", accept_multiple_files=True)
    files = load_images_uploaded(uploaded_files)
    sortable = True
elif option == "From URL":
    url_page = st.text_input("Insert URL")
    download = False
    if url_page != "":
        if not os.path.exists("output"):
            os.makedirs("output")
        asin = url_page.split("/")[-1]

        if not any([asin in x for x in os.listdir("output")]):
            title = download_images_from_url(url_page=url_page)
            download = True
            st.markdown(title)
        cols = st.columns(3)
        uploaded_files = sorted(os.listdir("output"))
        files = load_images(uploaded_files)
        sortable = True

if files:

    cols = st.columns(2)
    with cols[0]:
        sel = sort_items(list(files.keys()), direction="vertical")
        with cols[1]:
            for index, key in enumerate(sel):
                cols_ = st.columns(2)
                with cols_[0]:
                    st.image(files[key][1])
                    st.text(key)
                with cols_[1]:
                    default_value = ("MAIN" if index == 0 else "PT")
                    if default_value in prefixes:
                        default_index = prefixes.index(default_value)
                    st.selectbox("Prefix", prefixes, key=f"prefix_{key}", index=default_index)

    asin = st.text_input("ASIN")
    if st.button("Submit"):
        images = []
        for index, key in enumerate(sel):
            ext = key.split(".")[-1]
            image = files[key][0]
            prfix = f'prefix_{key}'
            if "PT" in prfix:
                filename = f"{asin}.PT{str(index).zfill(2)}.{ext}"
            else:
                filename = f"{asin}.{st.session_state[prfix]}.{ext}"
            image.save(filename.format(im_format=image.format))
            images.append(filename)
        download_multiple_files(images)
        shutil.rmtree("output", ignore_errors=True)
        shutil.rmtree("to_download", ignore_errors=True)
        os.makedirs("output")
