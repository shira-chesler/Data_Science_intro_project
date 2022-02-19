from bs4 import BeautifulSoup
import urllib.request
import urllib.parse
from datetime import datetime
import pickle
import os.path


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
all_keys = ['product_name', 'code', 'category_name']


def fetch_category_items(url, products, keys):
    url = urllib.parse.urlparse(url).path
    num = num_of_scroll_pages(
        "https://www.shufersal.co.il/" + url + "/fragment?q=:relevance&page=0")  # tells us the number of pages this
    # category has, so we can run on all of them
    soup_category = get_html_into_soup("https://www.shufersal.co.il/" + url + "/fragment?q=:relevance&page=0")
    category_name = soup_category.find("div", {"id": "filterCollapseSubCategories"}) \
        .findChild("div", {"class": "title js-facet-name"}, recursive=False).getText().strip()
    if category_name not in keys:
        keys.append(category_name)
    for page in range(0, num):
        if page % 10 == 0:
            print(get_time() + ": this is page number " + str(page + 1) + " out of " + str(num) + " pages ")
        soups = get_html_into_soup("https://www.shufersal.co.il/" + url + "/fragment?q=:relevance&page=" + str(
            page))  # iterate over all pages in this category
        ls1 = soups.find_all(data_food_equals_true)  # find all food items
        for lin in ls1:
            code = lin['data-product-code']
            fetch_one_item(code, products, keys, category_name)


def fetch_one_item(code, products, keys, category_name):
    soup3 = get_html_into_soup("https://www.shufersal.co.il/online/he/p/" + code + "/json")  # get item page
    name = soup3.find("h3", {"id": "modalTitle"}).getText()
    name.replace(name, ",", " ")
    item = {'product_name': name, 'code': code, 'category_name': category_name}
    nutrition_list = soup3.find_all("div", {"class": "nutritionItem"})  # get all nutrition data
    if len(nutrition_list) == 0:  # for mis-categorized items (non-food items)
        return
    for nutrition in nutrition_list:
        curr_key = nutrition.find("div", {"class": "text"}).getText()
        item[curr_key] = nutrition.findChildren('div')[0]['title']
        if curr_key not in keys:
            keys.append(curr_key)
    products.append(item)


def write_to_csv(products, keys, file_name):
    with open(file_name + '.csv', 'w', encoding='utf-8') as f:
        for key_index in range(len(keys)):
            if key_index == len(keys) - 1:
                f.write("%s" % keys[key_index])
            else:
                f.write("%s," % keys[key_index])
        f.write("\n")
        for o_item in products:
            for o_key in keys:
                if o_key in o_item:
                    f.write("%s," % (o_item[o_key]))
                else:
                    f.write("0,")
            f.write("\n")
    f.close()


# test(all_products, all_keys)
# print(urllib.parse.urlparse('/online/he/A31'))

def get_time():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    return current_time


soup = get_html_into_soup("https://www.shufersal.co.il/online/he/A")

ls = soup.find_all(has_data_category)
lt = []
for li in ls:
    lt.append(li.findChildren("a", recursive=False)[0]['href'])

if os.path.isfile('data.dump'):
    all_dump = pickle.load(open("data.dump", "rb"))
    all_products = all_dump["prods"]
    all_keys = all_dump["keys"]
else:
    all_dump = {"index": -1, "prods": all_products, "keys": all_keys}

for i in range(len(lt)):
    print(get_time() + ": iteration " + str(i + 1) + " out of " + str(len(lt)))
    if all_dump["index"] + 1 > i:
        print("Skipping " + str(i + 1) + " already in dump file")
        continue
    print(lt[i])
    if len(lt[i]) >= 14:
        if lt[i][11] == '%':  # tells if it's a page which we can immediately do web scraping on
            fetch_category_items(lt[i], all_products, all_keys)
        elif len(lt[i]) == 14:  # tells that the href is url of page that has sub categories in it
            soup1 = get_html_into_soup("https://www.shufersal.co.il/" + lt[i])
            sec = soup1.find("section", {"class": "categoryBannerComponent"})
            if sec:
                lst = sec.findChildren("a")
                for section in lst:
                    fetch_category_items(section['href'], all_products, all_keys)
    all_dump["index"] = i
    pickle.dump(all_dump, open("data.dump", "wb"))

write_to_csv(all_products, all_keys, 'data_for_classification')
