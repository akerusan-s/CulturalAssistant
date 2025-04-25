""" A module for items parsing from https://www.sima-land.ru. Shop was chosen randomly. """

import requests
import json
from bs4 import BeautifulSoup
from tqdm import tqdm


BASE_URL = 'https://www.sima-land.ru'                                       # shop URL; shop was chosen randomly

output_csv = open("../../data/raw/goods_1_50.csv", "w", encoding="UTF-8")   # save every 50 pages of the shop
output_csv.write("name\tcategory\tprice\trating\turl\tdescription\n")       # information that will be parsed

# 750 pages of items, 20 entities each
for page_num in tqdm(range(1, 751), desc="Page processed"):
    # API function, returns json with items system information on a current page
    response = requests.get(f"{BASE_URL}/iapi/product-list/items/v1/default-view/?page={page_num}&sort=rating"
                            "&currency=RUB&per-page=20&category_id=690&page_type=category&f=null&with_adult=1"
                            "&modifier_limit=5&settlement_id=27490597",
                            timeout=60).text

    response_dict = json.loads(response)

    # items per page processing
    for item in response_dict['items']:

        name = item['name']

        try:
            # some information (item name, rating, URL) stored in json
            price = str(item['prices']['main'])
            rating = str(item['rating']['value'])
            url = BASE_URL + item['url']

            # some information (item description, category) not stored in json
            # item card visited
            soup_per_item = BeautifulSoup(
                requests.get(url, timeout=60).text,
                "html.parser"
            )

            description_tag = soup_per_item.find(
                "div",
                class_="WD7t_o iBWXrD"
            )
            # NULL description processing
            if description_tag is not None:
                description = " ".join(
                    list(
                        map(
                            lambda x: x.text,
                            description_tag.find_all("p")
                        )
                    )
                )
            else:
                description = ""

            category = soup_per_item.find(
                "div",
                class_="FCOHHE UHKXSB"
            ).find_all(
                "span",
                class_="IPwfOk"
            )[2].find("a").text

            output_csv.write("\t".join([name, category, price, rating, url, description]) + "\n")

        except Exception as e:
            print()
            print("Bad Request")
            print(item)
            print(e)
            print()

    # save every 50 pages of the shop (for stability reasons, approximately every 80 pages there is a net problem)
    if page_num % 50 == 0 and page_num != 750:
        output_csv.close()
        output_csv = open(f"../../data/raw/goods_{page_num + 1}_{page_num + 50}.csv",
                          "w",
                          encoding="UTF-8")
        output_csv.write("name\tcategory\tprice\trating\turl\tdescription\n")

output_csv.close()
