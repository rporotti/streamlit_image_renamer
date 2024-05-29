import streamlit as st

from streamlit_sortables import sort_items
from utils import download_images_from_url, download_multiple_files, load_images, load_images_uploaded, clean_files, get_filename_images
import os

st.set_page_config(layout="wide")
if st.button("Clean temporary images"):
    clean_files()
option = st.selectbox("Select mode", ["From upload", "From URL"], key="mode")
prefixes = st.text_input("Insert prefixes (comma separated)", value="MAIN, PT")
prefixes = prefixes.replace(" ", "").split(",")

files = {}
if option == "From upload":
    uploaded_files = st.file_uploader("Choose a file", accept_multiple_files=True)
    files = load_images_uploaded(uploaded_files)
    asin = None
elif option == "From URL":
    url_page = st.text_input("Insert URL")
    download = False
    asin = url_page.split("/")[-1]
    if st.button("Start"):
        if not os.path.exists("output"):
            os.makedirs("output")
        if not os.path.exists("to_download"):
            os.makedirs("to_download")


        if not os.path.exists(f"output/{asin}"):
            os.makedirs(f"output/{asin}")
            if not any([asin in x for x in os.listdir(f"output/{asin}")]):
                title = download_images_from_url(url_page=url_page)
                download = True
                st.markdown(title)

    cols = st.columns(3)

if (option == "From upload" and files) or (option == "From URL" and os.path.exists(f"output/{asin}") and url_page!=""):
    if option == "From URL":

        if os.path.exists(f"output/{asin}"):

            uploaded_files = sorted(os.listdir(f"output/{asin}"))
            files = load_images(uploaded_files, asin)
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

    asin_to_download = st.text_input("ASIN", value=asin)
    if st.button("Submit"):
        if not os.path.exists(f"to_download/{asin}"):
            os.makedirs(f"to_download/{asin}")
        images = []
        index_pt = 1
        for index, key in enumerate(sel):
            ext = key.split(".")[-1]
            image = files[key][0]
            prfix = f'prefix_{key}'
            if "PT" in st.session_state[prfix]:
                suffix = f"PT{str(index_pt).zfill(2)}"
                index_pt += 1
            else:
                suffix = st.session_state[prfix]
            filename_zip = f"{asin_to_download}.{suffix}.{ext}"
            filename = f"to_download/{asin}/{asin_to_download}.{suffix}.{ext}"

            if image.mode == "JPEG":
                image.save(filename.format(im_format=image.format))
                # in most case, resulting jpg file is resized small one
            else:
                rgb_im = image.convert("RGB")
                rgb_im.save(filename.format(im_format=image.format))
                # some minor case, resulting jpg file is larger one, should meet your expectation

            images.append(filename_zip)
    if os.path.exists(f"to_download/{asin}"):
        images = get_filename_images(sel, asin_to_download)
        download_multiple_files(images, asin_to_download, root_folder=f"to_download/{asin}")