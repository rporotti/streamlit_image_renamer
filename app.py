import streamlit as st
from io import BytesIO
import io
import PIL.Image as Image
from streamlit_sortables import sort_items
import zipfile
st.set_page_config(layout="wide")
def download_multiple_files(images):


    buf = io.BytesIO()

    with zipfile.ZipFile(buf, "x") as zip:
        for zip_file in images:
            zip.write(zip_file)

    st.download_button(
        "Download all data",
        mime="application/zip",
        file_name="myimages.zip",
        data=buf.getvalue()
    )
cols = st.columns(3)
with cols[0]:
    uploaded_files = st.file_uploader("Choose a file", accept_multiple_files=True)
with cols[1]:
    if len(uploaded_files)>0:
        files = {}
        for index, uploaded_file in enumerate(uploaded_files):
            bytes_data = uploaded_file.read()
            files[uploaded_file.name] = bytes_data
        sel = sort_items([x.name for x in uploaded_files], direction="vertical")
    if len(uploaded_files) > 0:
        with cols[2]:
            for key in sel:
                st.image(files[key], width=100)
                st.text(key)
if len(uploaded_files) > 0:
    asin = st.text_input("ASIN")
    if st.button("Submit"):
        images = []
        for index, key in enumerate(sel):

            ext = key.split(".")[-1]
            print(files[key])
            image = Image.open(BytesIO(files[key]))
            if index == 0:
                filename = f"{asin}.MAIN.{ext}"
            else:
                filename = f"{asin}.PT{str(index).zfill(2)}.{ext}"
            image.save(filename.format(im_format=image.format))
            images.append(filename)
        download_multiple_files(images)

