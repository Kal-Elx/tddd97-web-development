import time
from selenium import webdriver

SIGNUP_INFO = {
    'signup_email': 'peter@pan.com',
    'signup_password': '123456',
    'repeat_signup_password': '123456',
    'first_name': 'Peter',
    'family_name': 'Pan',
    'city': 'London',
    'country': 'Neverland',
}
SIGNIN_INFO = {
    'login_email': 'peter@pan.com',
    'login_password': '123456',
}
SAMPLE_MSG = 'The moment you doubt whether you can fly, you cease for ever to be able to do it.'
HOME_TAB_INFO = {
    'home_panel_info_first_name': 'peter@pan.com',
    'home_panel_info_first_name': 'Peter',
    'home_panel_info_family_name': 'Pan',
    'home_panel_info_city': 'London',
    'home_panel_info_country': 'Neverland',
}
BROWSE_TAB_INFO = {
    'browse_panel_info_first_name': 'peter@pan.com',
    'browse_panel_info_first_name': 'Peter',
    'browse_panel_info_family_name': 'Pan',
    'browse_panel_info_city': 'London',
    'browse_panel_info_country': 'Neverland',
}

SLEEP_TIME = 1
LOAD_TIME = 0.2


def sign_up():
    for id, val in SIGNUP_INFO.items():
        elem = driver.find_element_by_id(id)
        elem.clear()
        elem.send_keys(val)
    driver.find_element_by_xpath(
        "//select[@name='gender']/option[text()='Male']").click()
    driver.find_element_by_id('signup_button').click()

    # Assert that we are on the home tab after sign up and it was successful
    # by checking that the info the info panel contains the right values.
    time.sleep(LOAD_TIME)
    for id, val in HOME_TAB_INFO.items():
        elem = driver.find_element_by_id(id)
        assert(elem.get_attribute('innerHTML') == val)


def sign_out():
    driver.find_element_by_id('account_tab').click()
    driver.find_element_by_id('sign_out_button').click()

    # Assert that we are back to welcome screen by finding the logo and slogan.
    time.sleep(LOAD_TIME)
    logo_and_slogan = driver.find_element_by_id('logo_and_slogan')
    assert(logo_and_slogan.get_attribute('alt') ==
           'Twidder - Socialize with other people around the world')


def sign_in():
    for id, val in SIGNIN_INFO.items():
        elem = driver.find_element_by_id(id)
        elem.clear()
        elem.send_keys(val)
    driver.find_element_by_xpath(
        "//select[@name='gender']/option[text()='Male']").click()
    driver.find_element_by_id('login_button').click()

    # Assert that we are on the home tab after sign in and it was successful
    # by checking that the info the info panel contains the right values.
    time.sleep(LOAD_TIME)
    for id, val in HOME_TAB_INFO.items():
        elem = driver.find_element_by_id(id)
        assert(elem.get_attribute('innerHTML') == val)


def post_message():
    driver.find_element_by_id('home_tab').click()
    textbox = driver.find_element_by_id('post_message_textarea_home_panel')
    textbox.clear()
    textbox.send_keys(SAMPLE_MSG)
    driver.find_element_by_id('post_message_button').click()
    driver.find_element_by_id('home_message_wall_refresh_button').click()

    # Assert that the newly posted message is on the user's message wall.
    time.sleep(LOAD_TIME)
    messages = driver.find_elements_by_xpath(
        "//dd[contains(text(), '{0}')]".format(SAMPLE_MSG))
    assert(len(messages) == 1)


def search_user():
    driver.find_element_by_id('browse_tab').click()
    elem = driver.find_element_by_id('user_email')
    elem.clear()
    elem.send_keys(SIGNUP_INFO['signup_email'])
    driver.find_element_by_id('search_user_button').click()

    # Assert that we are on the browse tab after search and that we found the
    # user by checking that info in the info panel contains the right values.
    time.sleep(LOAD_TIME)
    for id, val in BROWSE_TAB_INFO.items():
        elem = driver.find_element_by_id(id)
        assert(elem.get_attribute('innerHTML') == val)


if __name__ == '__main__':
    driver = webdriver.Chrome('./chromedriver')
    driver.get('http://127.0.0.1:5000/clean_db')
    sign_up()
    time.sleep(SLEEP_TIME)
    sign_out()
    time.sleep(SLEEP_TIME)
    sign_in()
    time.sleep(SLEEP_TIME)
    post_message()
    time.sleep(SLEEP_TIME)
    search_user()
    time.sleep(SLEEP_TIME)
    driver.close()
