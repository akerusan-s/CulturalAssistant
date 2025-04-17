import requests
from tqdm import tqdm
from bs4 import BeautifulSoup


BASE_URL = 'https://www.sima-land.ru'

html_doc = requests.get("https://www.sima-land.ru/tvorchestvo/?c_id=690&is_catalog=1").text
soup = BeautifulSoup(html_doc, 'html.parser')
groups = soup.find("ul", class_="OVrpD4").find_all("li", class_="mufu24")

for group in tqdm(groups, position=0, desc="Category", leave=False):
    output_csv = open(f"goods_group{groups.index(group)}.csv", "w", encoding="UTF-8")
    output_csv.write("name;category;price;url;description\n")

    category = group.find("span").text

    cat_href = BASE_URL + group.find("a")['href']
    soup_per_group = BeautifulSoup(
        requests.get(cat_href, timeout=60).text,
        'html.parser'
    )

    if soup_per_group.find("a", class_="Ky7lus") is not None:
        num_of_pages = int(soup_per_group.find("a", class_="Ky7lus").text)
    else:
        num_of_pages = 1

    for i in tqdm(range(num_of_pages), position=1, desc="Page", leave=False):
        # print(f"Category: {groups.index(group)}/{len(groups)}     \tPage: {i + 1}/{num_of_pages}")
        soup_per_page = BeautifulSoup(
            requests.get(f"https://www.sima-land.ru/tovary-dlya-vyazaniya/p{i + 1}/", timeout=60).text,
            'html.parser'
        )

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
                output_csv.write(";".join([name, category, price, href, description]) + "\n")

            except Exception as e:
                print("Bad request:", href)
                print("Page:", i + 1)
                print("Group index:", groups.index(group))

    output_csv.close()
