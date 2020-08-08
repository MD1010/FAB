import time

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from seleniumwire import webdriver
from webdriver_manager.chrome import ChromeDriverManager

from consts import app


class SeleniumLogin:
    def output_on_start(**kwargs):
        print("STARTED ", kwargs)

    def output_on_end(**kwargs):
        print("FINISHED ", kwargs)

    def __init__(self):
        options = Options().add_argument('--headless')
        driver = webdriver.Chrome(ChromeDriverManager().install(),options=options)
        # options = Options()
        # options.add_argument('--headless')
        # options.add_argument('--disable-gpu')
        # driver.scopes = ["https://utas.external.s3.fut.ea.com/ut/auth"]
        # driver.get(app.SIGN_IN_URL)
        # driver.find_element_by_xpath("//*[@id='email']").send_keys("laviil1612@gmail.com")
        # driver.find_element_by_xpath("//*[@id='password']").send_keys("Lidor10397")
        # driver.find_element_by_class_name("btn-next").click()
        # driver.find_element_by_class_name("btn-next").click()
        # driver.find_element_by_xpath("//*[@id='oneTimeCode']").send_keys(Keys.CONTROL, "a")
        # driver.find_element_by_xpath("//*[@id='oneTimeCode']").send_keys("96989058")
        # driver.find_element_by_class_name("btn-next").click()
        # time.sleep(20)
        # driver.find_element_by_xpath("/html/body/main/div/div/div/button[1]").click()

        for request in driver.requests:
            if request.response:
                print(request)
