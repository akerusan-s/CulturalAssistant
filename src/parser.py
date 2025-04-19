import requests
from tqdm import tqdm
from bs4 import BeautifulSoup


BASE_URL = 'https://www.sima-land.ru'


output_csv = open("goods_1_50.csv", "w", encoding="UTF-8")
output_csv.write("name\tcategory\tprice\turl\tdescription\n")

for page_num in tqdm(range(1, 751), desc="Page parsed"):
    html_doc = requests.get(f"https://www.sima-land.ru/tvorchestvo/p={page_num}/?c_id=690&is_catalog=1", timeout=60).text
    soup_per_page = BeautifulSoup(html_doc, 'html.parser')

    hrefs = map(
        lambda x: BASE_URL + x['href'],
        soup_per_page.find_all("a", class_="odeaio PfpX13")
    )

    for href in hrefs:
        try:
            soup_per_item = BeautifulSoup(
                requests.get(href, timeout=60).text,
                "html.parser"
            )

            name = soup_per_item.find("h1", class_="_9EfqO").text

            description_tag = soup_per_item.find("div", class_="WD7t_o iBWXrD")
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

            price_tag = soup_per_item.find("div", class_="EQXPxB").find("span", class_="C1_ch0 X8KFZ9").text
            price = "".join(
                filter(
                    lambda x: x.isdigit(),
                    list(price_tag)
                )
            )

            category = soup_per_item.find("div", class_="FCOHHE UHKXSB").find_all("span", class_="IPwfOk")[2].find("a").text

            output_csv.write("\t".join([name, category, price, href, description]) + "\n")

        except Exception as e:
            print("Bad request:", href)
            print("Page:", page_num)

    if page_num % 50 == 0:
        output_csv.close()
        output_csv = open(f"../data/raw/goods_{page_num + 1}_{page_num + 50}.csv",
                          "w",
                          encoding="UTF-8")
        output_csv.write("name\tcategory\tprice\turl\tdescription\n")

output_csv.close()
