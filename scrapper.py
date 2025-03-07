import re
import time
import pandas as PD
from selenium import webdriver
from colorama import init, Fore
from bs4 import BeautifulSoup as BS
from google.cloud import language_v1
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options

class YogonetScrapper:
    '''Class to scrap Yogonet webpage, Analyze it with pandas and upload it to BigQuery.'''
    
    def __init__(self):
        init() # colorama inizialization
        firefox_path = "/usr/bin/firefox-esr"
        service = Service("/usr/local/bin/geckodriver")
        options = Options()
        options.add_argument("-headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.binary_location = firefox_path
        self.web_driver = webdriver.Firefox(service=service, options=options)
        self.noticias = []
        self.gcnl_client = language_v1.LanguageServiceClient()
        try:
            self.main()
        except Exception as e:
            print(Fore.RED + str(e))
        finally:
            self.web_driver.quit()
    
    def goto_and_soup(self,url):
        '''Method to load webpage and soup html'''
        self.web_driver.get(url)
        time.sleep(5)
        soup = BS(self.web_driver.page_source, "html.parser")
        return soup

    def create_payload(self, noticia):
        '''Method to create noticia payload and fix value if needed'''
        #here we search the values/fields asked for the challenge
        data = noticia.find("div",class_="volanta_item_listado_noticias")
        title = data.a['title']
        link = data.a['href']
        data.b.decompose()
        kicker = data.a.text.strip() if data.a else None
        image = noticia.find("img")['src'] if noticia.find("img") else None
        if (not kicker or not title) and link:
            print(Fore.YELLOW + "value in noticia is None, fixing it ...")
            soup = self.goto_and_soup(link)
            kicker = soup.find("div",class_="volanta_noticia fuente_roboto_slab").text.strip() if soup.find("div",class_="volanta_noticia fuente_roboto_slab") else None
            title = soup.find("h1",class_="titulo_noticia fuente_roboto_slab").text.strip() if soup.find("h1",class_="titulo_noticia fuente_roboto_slab") else None
            image = soup.find("div",class_="slot contenido_fijo imagen_noticia").img['src'] if soup.find("div",class_="slot contenido_fijo imagen_noticia") else None
            #if once again the value is not found, we have to see where to find it so we raise an exception
            if (not kicker or not title or not image) and link: 
                print(kicker)
                print(title)
                print(image)
                raise Exception(f"value in noticia still None, check link: {link}")
        
        payload = {
            "kicker": kicker,
            "title": title,
            "link": link,
            "image": image,
        }

        print(Fore.GREEN + "- - - - - - - - - - - - - -"   )
        print(f"Noticia - {title}")
        print(link)

        return payload

    def get_all_news(self):
        '''Method to get all news
        IMPORTANT:
        - This method scrapes all the news/noticias available in the webpage but just in the first category
        theres more than 16000 news so for this challenge i'll get the first 2 pages per category
        '''
        URL = "https://www.yogonet.com/international/"
        soup = self.goto_and_soup(URL)
        categories_container = soup.find("div", class_="contenedor_items_hijos")
        categories_data = [{"category": x.text.strip(), "url": x['href']} for x in categories_container.find_all("a")]
        print(Fore.YELLOW + f"Categories found: {len(categories_data)}")
        for category in categories_data:
            paginator = 1
            while True:
                print(Fore.YELLOW + f"Category: {category['category']} - Page {paginator}")
                soup = self.goto_and_soup(category['url'] + f"?buscar=&pagina={paginator}")
                noticias = soup.find_all("div", class_="item_listado_noticias")
                for noticia in noticias:
                    payload = self.create_payload(noticia)
                    if payload['link'] not in [x['link'] for x in self.noticias]:
                        self.noticias.append(payload)
                print(Fore.YELLOW + f"Noticias found: {len(noticias)}")
                if len(noticias) == 0 or paginator == 2:
                    break
                paginator += 1
        return None #?

    def get_front_news(self):
        '''Method to get yogonet front page news
           IMPORTANT:
           - Method not used'''
        #First get the news/noticas html
        URL = "https://www.yogonet.com/international/"
        soup = self.goto_and_soup(URL)
        noticias = soup.find_all("div", class_="contenedor_dato_modulo")

        #once we have all the noticias we can create the payloads
        print(Fore.YELLOW + f"Noticias found: {len(noticias)}")
        for nro ,noticia in enumerate(noticias):
            nro += 1
            payload =self.create_payload_news(nro, noticia)
            if payload['link'] not in [x['link'] for x in self.noticias]:
                self.noticias.append(payload)
        
        print(Fore.YELLOW + f"Noticas scrapped: {len(self.noticias)}")

    #PANDAS PROCESS
    def pandas_process(self):
        '''Method to process data with pandas'''
        df = PD.DataFrame(self.noticias)
        # - Word count in title
        df['word_count'] = df['title'].apply(lambda x: len(x.split()))
        # - Character count in title
        df['character_count'] = df['title'].apply(lambda x: len(x))
        #List of words that start with a capital letter in Title
        def capitalized_words(title):
            capitalized_words = re.findall(r'\b[A-Z][a-z]*\b', title)
            return capitalized_words if capitalized_words else None
        df['capitalized_words'] = df['title'].apply(capitalized_words)
        
        return df

    #EXTRACT ADDITIONAL DATA
    def extract_additional_data(self, title):
        '''Method to analyz title and get person, organization and location data using Google CLoud Natural Language'''
        document = language_v1.Document(content=title, type_=language_v1.Document.Type.PLAIN_TEXT)
        response = self.gcnl_client.analyze_entities(document=document)
        
        persons = []
        organizations = []
        locations = []
        
        for entity in response.entities:
            if entity.type == language_v1.Entity.Type.PERSON:
                persons.append(entity.name)
            elif entity.type == language_v1.Entity.Type.ORGANIZATION:
                organizations.append(entity.name)
            elif entity.type == language_v1.Entity.Type.LOCATION:
                locations.append(entity.name)
        if not persons:
            persons = None
        if not organizations:
            organizations = None
        if not locations:
            locations = None
        return persons, organizations, locations

    #BIGQUERY UPLOAD
    def upload_to_bigquery(self, df):
        '''Method to upload data to BigQuery'''
        df.to_gbq(destination_table='yogonet_dataset.news', project_id='challenge-452921', if_exists='replace')

    def main(self):
        '''Run method'''
        #extract yogonet data
        self.get_all_news()
        #pandas process
        df = self.pandas_process()
        #extract additional data
        df[['persons', 'organizations', 'locations']] = df['title'].apply(lambda x: PD.Series(self.extract_additional_data(x)))

        print(df.head())
        #upload to bigquery
        self.upload_to_bigquery(df)
        print(Fore.GREEN + "Data uploaded to BigQuery")

if __name__ == "__main__":
    YogonetScrapper()