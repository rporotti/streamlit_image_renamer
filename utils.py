import streamlit as st
import io
import PIL.Image as Image
import zipfile

from amazoncaptcha import AmazonCaptcha
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.firefox.service import Service

from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import numpy as np
import time
import os
import requests

from selenium.webdriver.common.action_chains import ActionChains

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType


def get_driver():
    firefoxOptions = FirefoxOptions()
    firefoxOptions.headless = True
    driver = webdriver.Firefox(
        options=firefoxOptions,
        executable_path="/home/appuser/.conda/bin/geckodriver",
    )
    return driver


def solve_captcha():
    captcha = AmazonCaptcha.fromdriver(driver)
    solution = captcha.solve(True)
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
    captcha = True
    print(url_page)
    driver = get_driver()
    driver.get(url_page)
    myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, 'sp-cc-rejectall-link')))
    myElem.click()

    if not captcha:
        solve_captcha()
        myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, 'sp-cc-rejectall-link')))
        myElem.click()
        captcha = True

    title = driver.find_elements(by="id", value="productTitle")[0].text.strip()
    print(title)
    myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CLASS_NAME, 'imgTagWrapper')))
    myElem.click()

    time.sleep(1)
    image = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, 'ivLargeImage')))
    url = image.find_elements(By.TAG_NAME, "img")[0].get_attribute("src")
    download_image(url, "output", asin + "_" + str(0))

    i = 1
    while True:
        try:
            button = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, f'ivImage_{i}')))
            button.click()
            time.sleep(0.5)

            image = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, 'ivLargeImage')))
            url = image.find_elements(By.TAG_NAME, "img")[0].get_attribute("src")

            download_image(url, "output", asin + "_" + str(i))
            i += 1
        except:
            break
    return title


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

@st.cache_data
def load_images():
    files = {}
    for index, uploaded_file in enumerate(uploaded_files):
        image = Image.open(f"output/{uploaded_file}", "r")
        files[uploaded_file] = image
    return files