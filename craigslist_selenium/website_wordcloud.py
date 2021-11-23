# Get all the text from a webpage
# Now links or menu items or login information, just paragraphs headers and other text
from selenium import webdriver
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt


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
    browser = webdriver.Chrome(executable_path='chromedriver.exe', options=chrome_options)
else:
    browser = webdriver.Chrome(executable_path='chromedriver.exe')
# browser = webdriver.Chrome(ChromeDriverManager().install())


def get_head_url(url):
    if 'www' in url:
        return url.split("www")[1].split(".")[1]
    else:
        return url.split("https://")[1].split(".")[0]


def get_page_text_and_links(site_url):
    browser.get(site_url)
    all_h1 = browser.find_elements_by_tag_name('h1')
    all_h2 = browser.find_elements_by_tag_name('h2')
    all_h3 = browser.find_elements_by_tag_name('h3')
    all_h4 = browser.find_elements_by_tag_name('h4')
    all_h5 = browser.find_elements_by_tag_name('h5')
    all_p = browser.find_elements_by_tag_name('p')
    all_span = browser.find_elements_by_tag_name('span')
    all_strong = browser.find_elements_by_tag_name('strong')

    all_text_list = list()
    for t in all_h1:
        all_text_list.append(t.text.lower())
    for t in all_h2:
        all_text_list.append(t.text.lower())
    for t in all_h3:
        all_text_list.append(t.text.lower())
    for t in all_h4:
        all_text_list.append(t.text.lower())
    for t in all_h5:
        all_text_list.append(t.text.lower())
    for t in all_p:
        all_text_list.append(t.text.lower())
    for t in all_span:
        all_text_list.append(t.text.lower())
    for t in all_strong:
        all_text_list.append(t.text.lower())

    # Format the results into a single string
    site_string = ' '.join(all_text_list)

    # Now getting the links
    site_head_url = get_head_url(site_url)
    all_links = browser.find_elements_by_tag_name('a')
    cleaned_links = list()
    for link in all_links:
        try:
            if link.get_attribute('href') is not None and site_head_url == get_head_url(link.get_attribute('href')):
                cleaned_links.append(link.get_attribute('href'))
        except IndexError:
            continue
    unique_clean_links = list(set(cleaned_links))

    # Now removing media
    non_media_links = [link for link in unique_clean_links if link[-1] == '/']
    return {'text': site_string, 'link_list': non_media_links}


def create_wordcloud(string_in):
    stop_list = set(STOPWORDS)
    wordcloud = WordCloud(width=1000, height=650,
                          background_color="black",
                          max_words=50, stopwords=stop_list).generate(string_in)

    plt.figure()
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    # plt.title(site_url + "\n")
    plt.show()


def get_all_site_text(site_url, page_limit=2):
    # Start at the landing page, get all the text and all the links on that page
    links_to_search = [site_url]
    searched_links = list()
    all_site_text = list()
    search_counter = 0
    while len(links_to_search) > 0 and search_counter < page_limit:
        for idx, link in enumerate(links_to_search):
            print('Searching page: {0}'.format(link))
            search_counter += 1
            if search_counter >= page_limit:
                break
            searched_links.append(link)
            links_to_search.pop(idx)
            site_url_output = get_page_text_and_links(site_url=link)
            all_site_text.append(site_url_output['text'])
            for new_link in site_url_output['link_list']:
                if new_link not in searched_links:
                    links_to_search.append(new_link)
    browser.close()

    all_all_site_text = ''
    for site_text in all_site_text:
        all_all_site_text = all_all_site_text + site_text.replace("\n", " ").replace(".", " ")

    create_wordcloud(all_all_site_text)


get_all_site_text(site_url='https://www.i-qlair.com')
