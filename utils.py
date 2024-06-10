import streamlit as st
import io
import zipfile
from io import BytesIO
import PIL.Image as Image
from amazoncaptcha import AmazonCaptcha
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver import FirefoxOptions

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import requests
import shutil

from selenium import webdriver


def get_driver():
    firefoxOptions = FirefoxOptions()
    firefoxOptions.headless = True
    driver = webdriver.Firefox(
        options=firefoxOptions,
        executable_path="/home/appuser/.conda/bin/geckodriver",
    )
    return driver


def solve_captcha(driver):
    captcha = AmazonCaptcha.fromdriver(driver)
    solution = captcha.solve(True)
    if os.path.exists("not-solved-captcha.log"):
        with open("not-solved-captcha.log", "r") as f:
            url_captcha = f.readlines()[-1]
            captcha = AmazonCaptcha.fromlink(url_captcha)
            solution = captcha.solve()

    inputElement = driver.find_elements(by="id", value="captchacharacters")[0]
    inputElement.send_keys(solution)
    inputElement.send_keys(Keys.ENTER)


def download_image(image_url, folder, name):
    if not os.path.exists(folder):
        os.makedirs(folder)
    img_data = requests.get(image_url).content
    with open(folder + '/' + name + ".jpg", 'wb') as handler:
        handler.write(img_data)


def download_images_from_url(url_page):
    asin = url_page.split("/")[-1]


    delay = 3  # seconds
    captcha = False
    print(url_page)
    driver = get_driver()
    driver.get(url_page)


    with st.spinner("Connecting to Amazon..."):
        try:
            solve_captcha(driver)
        except:
            pass
        try:
            myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, 'sp-cc-rejectall-link')))
            myElem.click()
        except:
            pass



        title = driver.find_elements(by="id", value="productTitle")[0].text.strip()
        print(title)
        myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CLASS_NAME, 'imgTagWrapper')))
        myElem.click()

        time.sleep(1)
        image = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, 'ivLargeImage')))
        url = image.find_elements(By.TAG_NAME, "img")[0].get_attribute("src")
        download_image(url, f"output/{asin}", asin + "_" + str(0).zfill(2))

    elem = driver.find_element(By.ID, "ivImagesTab")
    images = elem.find_elements(By.CLASS_NAME, "ivThumbImage")



    for index in range(1, len(images)-1):
        delay=5
        retry = 0
        retries = 5


        result = None
        while result is None and retry<retries:
            try:
                my_bar = st.progress(index / (len(images)-1), text=f"Downloading image {index} of {len(images)}")
                button = WebDriverWait(driver, delay).until(
                    EC.visibility_of_element_located((By.ID, f'ivImage_{index}')))
                button.click()
                time.sleep(0.5)
                image = WebDriverWait(driver, delay).until(EC.visibility_of_element_located((By.ID, 'ivLargeImage')))
                url = image.find_elements(By.TAG_NAME, "img")[0].get_attribute("src")

                download_image(url, f"output/{asin}", asin + "_" + str(index).zfill(2))
                my_bar.empty()
                result=True

            except:
                retry +=1


    return title


def download_multiple_files(images, asin_to_download, root_folder):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "x") as zip:
        for zip_file in images:
            zip.write(os.path.join(root_folder, zip_file), zip_file)
    status_checkbox = st.checkbox("Clean all files after download", value=True)
    st.download_button(
        "Download all data",
        mime="application/zip",
        file_name=f"{asin_to_download}.zip",
        data=buf.getvalue(),
        on_click=post_download,
        kwargs={"clean_all": status_checkbox, "asin": asin_to_download},
    )


def post_download(asin, clean_all=False):
    if clean_all:
        if os.path.exists(f"output/{asin}"):
            shutil.rmtree(f"output/{asin}")
        if os.path.exists(f"to_download/{asin}"):
            shutil.rmtree(f"to_download/{asin}")
        #shutil.rmtree("output")

@st.cache_data
def load_images(uploaded_files, asin):
    files = {}
    for index, uploaded_file in enumerate(uploaded_files):
        if uploaded_file.endswith("jpg"):
            image = Image.open(f"output/{asin}/{uploaded_file}", "r")
            files[uploaded_file] = [image, image.resize((100,100))]
    return files

@st.cache_data
def load_images_uploaded(uploaded_files):
    files = {}
    for index, uploaded_file in enumerate(uploaded_files):
        bytes_data = uploaded_file.read()
        image = Image.open(BytesIO(bytes_data))
        files[uploaded_file.name] = [image, image.resize((100,100))]
    return files

def clean_files():
    shutil.rmtree("output", ignore_errors=True)
    shutil.rmtree("to_download", ignore_errors=True)
    os.makedirs("output")
    os.makedirs("to_download")

def get_filename_images(sel, asin_to_download):
    images = []
    index_pt = 1
    for index, key in enumerate(sel):
        ext = key.split(".")[-1]
        prfix = f'prefix_{key}'
        if "PT" in st.session_state[prfix]:
            suffix = f"PT{str(index_pt).zfill(2)}"
            index_pt += 1
        else:
            suffix = st.session_state[prfix]
        filename_zip = f"{asin_to_download}.{suffix}.{ext}"
        images.append(filename_zip)
    return images
