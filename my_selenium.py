import pickle
import json
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

import constants

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

import os.path

def save_obj(obj, name):
    with open(name + '.txt', 'w') as f:
        f.write(json.dumps(obj))


def load_obj(name):
    with open(name + '.txt', 'r') as f:
        return json.load(f)

def start_login(email, password):
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get(constants.WEB_APP_URL)
    fileName = 'cookies'

    if os.path.isfile(fileName+".txt"):
        driver.delete_all_cookies()
        cookies = load_obj(fileName)
        print(cookies)
        for cookie in cookies:
            cookie['expiry'] = int(cookie['expiry'])

            driver.add_cookie(cookie)
        driver.get(constants.WEB_APP_URL)
        driver.implicitly_wait(20)
        el = driver.find_elements_by_css_selector(".ut-login .ut-login-content .btn-standard")[0]
        print(el)
        driver.implicitly_wait(60)
        el.click()

        #Log In btn

    # else:
    #     driver.get("https://signin.ea.com/p/web2/login?execution=e1639509631s1&initref=https%3A%2F%2Faccounts.ea.com%3A443%2Fconnect%2Fauth%3Fprompt%3Dlogin%26accessToken%3Dnull%26client_id%3DFIFA-20-WEBCLIENT%26response_type%3Dtoken%26display%3Dweb2%252Flogin%26locale%3Den_US%26redirect_uri%3Dhttps%253A%252F%252Fwww.easports.com%252Ffifa%252Fultimate-team%252Fweb-app%252Fauth.html%26release_type%3Dprod%26scope%3Dbasic.identity%2Boffline%2Bsignin%2Bbasic.entitlement%2Bbasic.persona")
    #     emailField = driver.find_element_by_id("email")
    #     passwordField = driver.find_element_by_id("password")
    #     logInButton = driver.find_element_by_id("btnLogin")
    #     emailField.send_keys(email)
    #     passwordField.send_keys(password)
    #     logInButton.click()
    #     driver.find_element_by_xpath("//input[@name='codeType' and @value='SMS']").click()
    #     #send the email verfication
    #     driver.find_element_by_class_name("btn-next").click()
    #
    #     input1 = input("Enter your code ")
    #     if input1:
    #         driver.find_element_by_id("oneTimeCode").send_keys(input1)
    #         driver.find_element_by_id("btnSubmit").click()
    #         save_obj(driver.get_cookies(),fileName)


    # """get the confirmation password"""
    # driver.implicitly_wait(20)


    # confirmationCode = checkMailForConfirmation(driver, email)

    #     checkMainForConfirmation(email)
    # driver.close()


def checkMailForConfirmation(driver, email):
    #new tab
    # driver.execute_script('''window.open("https://accounts.google.com/ServiceLogin?service=mail#identifier","_blank");''')
    confirmationCode = ""
    return confirmationCode
