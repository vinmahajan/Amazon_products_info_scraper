import requests
from bs4 import BeautifulSoup
import pandas as pd

#scrape products info from one page
def scrape_products_info(page_url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'}
    response=requests.get(page_url, headers=headers)
    
    
    
    if response==None:
       print('Page is not available')
    
    
    
    
    soup=BeautifulSoup(response.content, "html.parser")
    s=soup.find('div', class_="s-main-slot s-result-list s-search-results sg-row")
    product_containers=s.find_all('div', class_="sg-col-20-of-24 s-result-item s-asin sg-col-0-of-12 sg-col-16-of-20 sg-col s-widget-spacing-small sg-col-12-of-16")

    products=[]
    #scrape info from each page
    for container in product_containers:

        '''Note-->#if information is not available it will return "NA"'''

        #to get product url
        try:
          product_url="https://www.amazon.in" + container.find('a')['href']
        except:
          product_url ="NA"

        #to get product name
        try:
          product_name=container.find('span', class_="a-size-medium a-color-base a-text-normal").text.strip()
        except:
          product_name  ="NA"

        #to get product price
        try:
          product_price=container.find('span', class_="a-price-whole").text.strip()
        except:
          product_price='NA'

        # to get product rating
        try:
          product_rating=container.find('span', class_="a-icon-alt").text.strip()[:3]
        except:
          product_rating  ="NA"

        # to get total number of reviews
        try:
          num_reviews=container.find('span', class_="a-size-base s-underline-text").text.strip()
        except:
          num_reviews  ="NA"

        #adding each product details in products list
        products.append({
                'Product URL': product_url,
                'Product Name': product_name,
                'Product Price': product_price,
                'Rating': product_rating,
                'Number of Reviews': num_reviews
            })
    return products     #return list of products found on one page

#scrape products info from multiple pages
def scrape_multiple_pages(url, no_pages):
    all_product=[]
    #loop through all pages
    for num in range(1, no_pages+1): 
        page_url=f'{url}&page={num}'
        products_on_pages=scrape_products_info(page_url)
        all_product.extend(products_on_pages)       #adding every product info in "all_product" list

    return all_product      #return list of all product info

#scrape additional information of each product
def scrape_additional_products_info(page_url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'}
    response=requests.get(page_url, headers=headers)
    soup=BeautifulSoup(response.content, "html.parser")
    
    #to get description
    try:
        description=". ".join([x.text.strip() for x in soup.find('div', {'id': 'feature-bullets'}).find_all('span')])
    except:
        description="NA"

    #to get product description
    try:
        product_description=soup.find('div', {'id': 'productDescription'}).find('span').text
    except:
        product_description="NA"

    #to get ASIN
    try:
        asin = soup.find('th', class_='a-color-secondary a-size-base prodDetSectionEntry', string=' ASIN ').find_next('td', class_='a-size-base prodDetAttrValue').text.strip()
    except:
        try:
            asin=soup.select('ul.a-unordered-list.a-nostyle.a-vertical.a-spacing-none.detail-bullet-list > li > span > span:nth-child(2)')[3].text
        except:
            asin = 'NA'

    #to get Manufacturer
    try:
        s=soup.find('table', class_="a-keyvalue prodDetTable")
        manufacturer = s.find('th', class_='a-color-secondary', string=' Manufacturer ').find_next('td', class_='a-size-base prodDetAttrValue').text.strip()
    except:
        try:
            manufacturer=soup.select('ul.a-unordered-list.a-nostyle.a-vertical.a-spacing-none.detail-bullet-list > li > span > span:nth-child(2)')[2].text
        except:
            manufacturer="NA"


    return {'Product URL': page_url,
            'Description':description,
            'ASIN':asin,
            'Product Description':product_description,
            'Manufacturer':manufacturer}    



url="https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_1"
num_of_pages=2

print('Collecting products info...')
data=scrape_multiple_pages(url, num_of_pages)
df=pd.DataFrame(data)


new_data=[]
for index, row in df.iterrows():
  url=row['Product URL']
  ndata=scrape_additional_products_info(url)
  new_data.append(ndata)
 
#combining all data
for i in range(len(data)):
  data[i].update(new_data[i])

pd.DataFrame(data).to_csv('products_information.csv', encoding='utf-8') #saving data in csv file

print(f"Found/Collected info of total {len(data)} products from {num_of_pages} pages. Saved in 'products_information.csv' file")
