from selenium import webdriver
from selenium.common.exceptions import *
from webdriver_manager.chrome import ChromeDriverManager
import time
from pyvirtualdisplay import Display

# Set to false to show the chrome window, True to hide it
headless = False

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--proxy-server='direct://'")
chrome_options.add_argument("--proxy-bypass-list=*")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--ignore-certificate-errors')

if headless:
    browser = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
else:
    browser = webdriver.Chrome(ChromeDriverManager().install())
    
    
def get_additional_assets():
    all_assets = {
        'car': 4000,
        'speakers': 500
    }
    return sum(all_assets.values())


def get_american_century(headless=False):
    browser.get('https://www.americancentury.com/en.html')
    username_input = browser.find_elements_by_name('username')
    for username_input_option in username_input:
        try:
            username_input_option.send_keys('mashanahan456')
        except ElementNotInteractableException:
            continue
    submit_button = browser.find_elements_by_name('acct-login')[0]
    submit_button.click()
    password_input = browser.find_elements_by_name('password')
    for password_input_option in password_input:
        try:
            password_input_option.send_keys('Adminguy123,')
        except ElementNotInteractableException:
            continue
    login_button = browser.find_elements_by_id('okta-signin-submit')[0]
    login_button.click()

    # Check if text message verification is needed
    text_message_button = browser.find_elements_by_class_name('sms-request-button')
    if len(text_message_button) > 0:
        print("American Century needs to verify by text!")
        text_message_button[0].click()
        verification_code = input("What is the code?")
        verification_answer = browser.find_elements_by_name('answer')
        verification_answer[0].send_keys(verification_code)
        submit_button = browser.find_elements_by_class_name('button-primary')
        submit_button[0].click()

    # Now getting the balance
    account_balance = browser.find_elements_by_class_name('bal')[0].text
    formatted_balance = float(account_balance.replace("$", "").replace(",", ""))
    # browser.close()
    return formatted_balance


def get_bank_of_america(headless=False):
    browser.get('https://secure.bankofamerica.com/login/sign-in/signOnV2Screen.go')
    username = browser.find_elements_by_name('dummy-onlineId')
    password = browser.find_elements_by_name('dummy-passcode')
    username[0].send_keys('mashanahan456')
    password[0].send_keys('HammerThrow123')
    submit_button = browser.find_elements_by_name('enter-online-id-submit')
    submit_button[0].click()

    # Getting the account balance
    account_balance = browser.find_elements_by_class_name('balanceValue')
    formatted_account_balance = float(account_balance[0].text.replace("$", "").replace(",", ""))
    # browser.close()
    return formatted_account_balance


def get_fidelity_balance(headless=False):
    browser.get('https://login.fidelity.com/ftgw/Fidelity/RtlCust/Login/Init?AuthRedUrl='
                'https://oltx.fidelity.com/ftgw/fbc/oftop/portfolio#summary')
    time.sleep(1)
    username_form = browser.find_elements_by_class_name('fs-mask-username')[0]
    password_form = browser.find_elements_by_id('password')[0]
    enter_button = browser.find_elements_by_id('fs-login-button')[0]
    username_form.send_keys('mashanahan456')
    password_form.send_keys('Adminguy123,')
    enter_button.click()
    browser.get('https://oltx.fidelity.com/ftgw/fbc/oftop/portfolio#summary')
    time.sleep(5)
    all_accounts = browser.find_elements_by_class_name('js-total-balance-value')[0]
    fidelity_account_balance = all_accounts.text
    current_balance = float(fidelity_account_balance.split("$")[1].replace(",", ""))
    # browser.close()
    return current_balance


def get_current_net_worth():
    fidelity = get_fidelity_balance()
    american_century = get_american_century()
    bank_of_america = get_bank_of_america()
    other_assets = get_additional_assets()
    return sum([fidelity, american_century, bank_of_america, other_assets])


net_worth = get_current_net_worth()
