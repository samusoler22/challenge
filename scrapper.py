import os
import time
import pandas as PD
from selenium import webdriver
from colorama import init, Fore
from bs4 import BeautifulSoup as BS
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options

class YogonetScrapper:
    '''Class to scrap Yogonet webpage, Analyze it with pandas and upload it to BigQuery.
    TODO:
    - Add pandas analysis method
    - Add BigQuery upload method
    '''
    
    def __init__(self):
        init() # colorama inizialization
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        gecko_path = os.path.join(self.current_dir, "geckodriver.exe")
        firefox_path = "C:\\Program Files\\Mozilla Firefox\\firefox.exe"
        service = Service(gecko_path)
        options = Options()
        options.add_argument("-headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.binary_location = firefox_path
        self.web_driver = webdriver.Firefox(service=service, options=options)
        self.noticias = []
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
    
    def create_payload(self, nro ,noticia):
        '''Method to create noticia payload and fix value if needed'''
        #here we search the values asked for the challenge
        kicker = noticia.find("div",class_="volanta fuente_roboto_slab").text.strip() if noticia.find("div",class_="volanta fuente_roboto_slab") else None
        title = noticia.find("h2",class_="titulo fuente_roboto_slab").a.text.strip() if noticia.find("h2",class_="titulo fuente_roboto_slab") else None
        link = noticia.find("h2",class_="titulo fuente_roboto_slab").a['href'] if noticia.find("h2",class_="titulo fuente_roboto_slab") else None
        image = noticia.find("img")['src'] if noticia.find("img") else None
        #if one of them is not found but we have a link, we can try to get the values from the link
        if (not kicker or not title or not image) and link:
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
                raise Exception(f"value in noticia {nro} still None, check link: {link}")
            #print(f"fixed noticia {nro}")
        
        print(Fore.GREEN + f"noticia {nro} - {title}")
        payload = {
            "kicker": kicker,
            "title": title,
            "link": link,
            "image": image,
        }

        return payload

    def get_yogonet_data(self):
        '''Method to get yogonet data'''
        #First get the news/noticas html
        URL = "https://www.yogonet.com/international/"
        soup = self.goto_and_soup(URL)
        noticias = soup.find_all("div", class_="contenedor_dato_modulo")

        #once we have all the noticias we can create the payloads
        print(Fore.YELLOW + f"Noticias found: {len(noticias)}")
        for nro ,noticia in enumerate(noticias):
            nro += 1
            payload =self.create_payload(nro, noticia)
            if payload['link'] not in [x['link'] for x in self.noticias]:
                self.noticias.append(payload)
        
        print(Fore.YELLOW + f"Noticas scrapped: {len(self.noticias)}")

    def main(self):
        '''Run method'''
        #extract yogonet data
        self.get_yogonet_data()

if __name__ == "__main__":
    YogonetScrapper()