from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time


def get_motorcycle_dict(limit=100):
    # Initializing the browser
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    browser = webdriver.Chrome(executable_path='chromedriver.exe', options=chrome_options)

    # For motorcycles
    browser.get('https://nh.craigslist.org/search/mca?query=motorcycle&sort=rel')
    motorcycle_post_dict = dict()

    links = [title.get_attribute('href') for title in browser.find_elements_by_class_name('result-title')]
    while True:
        next_button = browser.find_element_by_class_name('next')
        try:
            next_button.click()
            links.extend([title.get_attribute('href')
                          for title in browser.find_elements_by_class_name('result-title')])
        except:
            break
    if limit is not None:
        links = links[0:limit]

    # Now getting the data
    for link in links:
        if limit is None:
            print("Getting information for post:", len(motorcycle_post_dict) + 1, "of", len(links))
        else:
            print("Getting information for post:", len(motorcycle_post_dict) + 1, "of", limit)
        browser.get(link)
        attrgroups = browser.find_elements_by_class_name('attrgroup')
        post_title = attrgroups[0].text
        post_info = attrgroups[1].text
        try:
            motorcycle_post_dict[post_title] = {'price': browser.find_element_by_class_name('price').text}
        except:
            motorcycle_post_dict[post_title] = {'price': 'None'}
        for info in post_info.split("\n"):
            try:
                motorcycle_post_dict[post_title][info.split(":")[0].replace(" ", "")] = info.split(":")[1].replace(" ", "")
            except:
                continue

    browser.close()
    return motorcycle_post_dict


def get_car_dict(limit=100):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    browser = webdriver.Chrome(executable_path='chromedriver.exe', options=chrome_options)

    browser.get('https://nh.craigslist.org/search/cta?query=car&sort=rel')
    car_post_dict = dict()

    links = [title.get_attribute('href') for title in browser.find_elements_by_class_name('result-title')]
    while True:
        next_button = browser.find_element_by_class_name('next')
        try:
            next_button.click()
            links.extend([title.get_attribute('href')
                          for title in browser.find_elements_by_class_name('result-title')])
        except:
            break
    if limit is not None:
        links = links[0:limit]

    for link in links:
        try:
            if limit is not None:
                print("Getting information for post:", len(car_post_dict) + 1, "of", limit)
            else:
                print("Getting information for post:", len(car_post_dict) + 1, "of", len(links))
            browser.get(link)
            attrgroups = browser.find_elements_by_class_name('attrgroup')
            post_title = attrgroups[0].text
            post_info = attrgroups[1].text
            try:
                car_post_dict[post_title] = {'price': browser.find_element_by_class_name('price').text}
            except:
                car_post_dict[post_title] = {'price': 'None'}
            for info in post_info.split("\n"):
                try:
                    car_post_dict[post_title][info.split(":")[0].replace(" ", "")] = info.split(":")[1].replace(" ", "")
                except:
                    continue
        except:
            continue
    browser.close()
    return car_post_dict


def get_car_prices_from_vin(vin, zipcode):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    browser = webdriver.Chrome(executable_path='chromedriver.exe', options=chrome_options)
    browser.set_window_size(1024, 800)
    browser.get('https://www.carfax.com/value/')
    zipcode_box = browser.find_elements_by_class_name('cfx-input-text')[0]
    vin_box = browser.find_elements_by_class_name('cfx-input-text')[1]
    submit_box = browser.find_element_by_class_name('vehicle-input-form__input__submit')
    zipcode_box.send_keys(zipcode)
    vin_box.send_keys(vin)
    submit_box.click()
    time.sleep(2)
    price_output = browser.find_elements_by_class_name(
        'results__prices__list-item__price')
    if len(price_output) == 0:
        print("No results found :(")
        browser.close()
        return None
    price_dict = {
        'retail_value': price_output[0].text,
        'private_value': price_output[1].text,
        'trade_in': price_output[2].text
    }
    browser.close()
    return price_dict


def get_car_deals(car_dicts):
    deals = list()
    keys = list(car_dicts.keys())
    for title in keys:
        try:
            info = car_dicts[title]
            # year = title.split(" ")[0]
            # make = title.split(" ")[1]
            # model = title.split(" ")[2]
            # transmission = info['transmission']
            # car_type = info['type']
            # miles = info['odometer']
            price = info['price']
            if 'VIN' in info.keys():
                vin = info['VIN']
                carfax_prices = get_car_prices_from_vin(vin, '03820')
                if carfax_prices is not None:
                    deal = 'BAD'
                    # Now comparing the price
                    price = float(price.replace("$", "").replace(",", ""))
                    carfax_retail = float(carfax_prices['retail_value'].replace("$", "").replace(",", ""))
                    carfax_private = float(carfax_prices['private_value'].replace("$", "").replace(",", ""))

                    if price/carfax_retail < 0.85:
                        deal = 'GOOD'
                    if price/carfax_private < 0.9:
                        deal = 'GOOD'
                    if deal == 'BAD':
                        deals.append([title, price, 'BAD DEAL'])
                        print(title, 'for', price)
                        print("THATS A BAD DEAL")
                        print()
                    else:
                        deals.append([title, price, 'GOOD DEAL'])
                        print(title, 'for', price)
                        print("THATS A GOOD DEAL!")
                        print()
        except:
            continue
    return deals


car_dicts = get_car_dict(limit=None)
deal_output = get_car_deals(car_dicts)
