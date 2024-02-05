import streamlit as st
from io import BytesIO
import io
import PIL.Image as Image
from streamlit_sortables import sort_items
import zipfile

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

uploaded_files = st.file_uploader("Choose a file", accept_multiple_files=True)

if len(uploaded_files)>0:
    files = {}
    for index, uploaded_file in enumerate(uploaded_files):
        bytes_data = uploaded_file.read()
        files[uploaded_file.name] = bytes_data
    sel = sort_items([x.name for x in uploaded_files])
    cols = st.columns(6)
    index = 0
    for key in sel:

        with cols[index]:
            st.image(files[key])
            st.text(key)
        index += 1

    asin = st.text_input("ASIN")
    if st.button("Submit"):
        images = []
        for index, key in enumerate(sel):

            ext = key.split(".")[-1]
            print(files[key])
            image = Image.open(BytesIO(files[key]))
            image.save(f"{asin}.{index}.{ext}".format(im_format=image.format))
            images.append(f"{asin}.{index}.{ext}")
        download_multiple_files(images)

