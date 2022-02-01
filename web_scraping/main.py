from bs4 import BeautifulSoup
import urllib.request


def has_data_category(tag):
    return tag.has_attr('data-category')


def get_html_into_soup(string):
    html = urllib.request.urlopen(string)
    soupy = BeautifulSoup(html, 'html.parser')
    return soupy


def data_food_equals_true(tag):
    return tag.has_attr('data-food') and (tag['data-food'] == "true")


def num_of_scroll_pages(url):
    soupy = get_html_into_soup(url)
    return int(soupy.find_all('div')[0]['data-pages'])


soup = get_html_into_soup("https://www.shufersal.co.il/online/he/A")

ls = soup.find_all(has_data_category)
list = []
for li in ls:
    list.append(li.findChildren("a", recursive=False)[0]['href'])

all_products = []
all_keys = []
for i in range(len(list)):
    if len(list[i]) >= 14:
        if list[i][11] == '%':  # tells if it's a page which we can immediatly do web scraping on
            num = num_of_scroll_pages("https://www.shufersal.co.il/" + list[i] + "/fragment?q=:relevance&page=0")  # tells us the number of pages this category has, so we can run on all of them
            print("https://www.shufersal.co.il/" + list[i] + "/fragment?q=:relevance&page=0")
            for page in range(0, num):
                soup1 = get_html_into_soup("https://www.shufersal.co.il/" + list[i] + "/fragment?q=:relevance&page=" + str(page)) #iterate over all pgaes in this category
                ls1 = soup1.find_all(data_food_equals_true) #find all food items
                for li in ls1:
                    code = li['data-product-code']
                    soup3 = get_html_into_soup("https://www.shufersal.co.il/online/he/p/" + code + "/json") # get item page
                    item = {}
                    item['name'] = soup3.find("h3", {"id": "modalTitle"}).getText()
                    price_per_amount = soup3.find("div", {"class": "smallText"}).getText().split('ש"ח ל-')
                    units = price_per_amount[1]
                    item[units] = price_per_amount[0]
                    nutrition_list = soup3.find_all("div", {"class": "nutritionItem"}) # get all nutrition data
                    for nutri in nutrition_list:
                        curr_key = nutri.find("div", {"class": "text"}).getText()
                        item[curr_key] = nutri.findChildren('div')[0]['title']
                        if curr_key not in all_keys:
                            all_keys.append(curr_key)
                    print(item)
                    all_products.append(item)
