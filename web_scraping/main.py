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


all_products = []
all_keys = []


def fetch_category_items(url, products, keys):
    num = num_of_scroll_pages(
        "https://www.shufersal.co.il/" + url + "/fragment?q=:relevance&page=0")  # tells us the number of pages this
    # category has, so we can run on all of them
    for page in range(0, num):
        soups = get_html_into_soup("https://www.shufersal.co.il/" + url + "/fragment?q=:relevance&page=" + str(
            page))  # iterate over all pages in this category
        ls1 = soups.find_all(data_food_equals_true)  # find all food items
        for lin in ls1:
            code = lin['data-product-code']
            fetch_one_item(code, products, keys)


def fetch_one_item(code, products, keys):
    soup3 = get_html_into_soup("https://www.shufersal.co.il/online/he/p/" + code + "/json")  # get item page
    item = {'name': soup3.find("h3", {"id": "modalTitle"}).getText()}
    price_per_amount = soup3.find("div", {"class": "smallText"}).getText().split('ש"ח ל-')
    units = price_per_amount[1]
    item[units] = price_per_amount[0]
    nutrition_list = soup3.find_all("div", {"class": "nutritionItem"})  # get all nutrition data
    if len(nutrition_list) == 0:  # for mis-categorized items (non-food items)
        return
    for nutrition in nutrition_list:
        curr_key = nutrition.find("div", {"class": "text"}).getText()
        item[curr_key] = nutrition.findChildren('div')[0]['title']
        if curr_key not in keys:
            keys.append(curr_key)
    products.append(item)


soup = get_html_into_soup("https://www.shufersal.co.il/online/he/A")

ls = soup.find_all(has_data_category)
lt = []
for li in ls:
    lt.append(li.findChildren("a", recursive=False)[0]['href'])

for i in range(len(lt)):
    if len(lt[i]) >= 14:
        if lt[i][11] == '%':  # tells if it's a page which we can immediately do web scraping on
            fetch_category_items(lt[i], all_products, all_keys)
        elif len(lt[i]) == 14:  # tells that the href is url of page that has sub categories in it
            soup1 = get_html_into_soup("https://www.shufersal.co.il/" + lt[i])
            sec = soup1.find("section ", {"class": "categoryBannerComponent  categoryLinksSection beStyle"})
            if sec:
                lst = sec.findChildren("a")[0]['href']
                for section in lst:
                    fetch_category_items(lt[i], all_products, all_keys)
