import streamlit as st
from io import BytesIO
import PIL.Image as Image
from streamlit_sortables import sort_items
from utils import download_images_from_url, download_multiple_files, load_images
st.set_page_config(layout="wide")

option = st.selectbox("Select mode", ["From upload", "From URL"], key="mode")
prefixes = st.text_input("Insert prefixes (comma separated)", value="MAIN, PT")
prefixes = prefixes.replace(" ", "").split(",")


if option=="From upload":

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
                for index, key in enumerate(sel):
                    cols_ = st.columns(2)
                    with cols_[0]:
                        st.image(files[key], width=100)
                        st.text(key)
                    with cols_[1]:
                        default_value = ("MAIN" if index==0 else "PT")
                        if default_value in prefixes:
                            default_index = prefixes.index(default_value)
                        st.selectbox("Prefix", prefixes, key=f"prefix_{key}", index=default_index)
    if len(uploaded_files) > 0:
        asin = st.text_input("ASIN")
        if st.button("Submit"):
            images = []
            for index, key in enumerate(sel):

                ext = key.split(".")[-1]
                print(files[key])
                image = Image.open(BytesIO(files[key]))
                prfix = f'prefix_{key}'
                if "PT" in prfix:
                    filename = f"{asin}.PT{str(index).zfill(2)}.{ext}"
                else:
                    filename = f"{asin}.{st.session_state[prfix]}.{ext}"
                image.save(filename.format(im_format=image.format))
                images.append(filename)
            download_multiple_files(images)

elif option=="From URL":
    url_page = st.text_input("Insert URL")

    print(url_page)

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
        # with cols[0]:
        #    uploaded_files = st.file_uploader("Choose a file", accept_multiple_files=True)
        uploaded_files = sorted(os.listdir("output"))
        with cols[0]:

            sel = sort_items([x for x in uploaded_files], direction="vertical")
            files = load_images()
            with cols[1]:
                for key in sel:
                    st.image(files[key], width=100)

                    st.text(key)

        if len(uploaded_files) > 0:
            asin = st.text_input("ASIN")
            if st.button("Submit"):
                images = []
                os.makedirs("to_download")
                for index, key in enumerate(sel):

                    ext = key.split(".")[-1]
                    print(files[key])
                    image = files[key]
                    if index == 0:
                        filename = f"{asin}.MAIN.{ext}"
                    else:
                        filename = f"{asin}.PT{str(index).zfill(2)}.{ext}"
                    image.save("to_download/" + filename.format(im_format=image.format))
                    images.append("to_download/" + filename)
                download_multiple_files(images)
                shutil.rmtree("output", ignore_errors=True)
                shutil.rmtree("to_download", ignore_errors=True)
                os.makedirs("output")

