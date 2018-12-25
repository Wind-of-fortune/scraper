# -*- coding: utf-8 -*-
import time

import scrapy

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from settings import domain, url

class CompParserSpider(scrapy.Spider):
    name = 'comp_parser'
    allowed_domains = domain
    start_urls = url

    price_dict = {}

    def parse(self, response):

        opts = Options()
        opts.add_argument("--headless")

        driver = webdriver.Firefox(options=opts)
        driver.set_page_load_timeout(200)
        driver.get(self.start_urls[-1])

        driver.maximize_window()

        for i in range(5):
            try:
                html = driver.find_element_by_tag_name('html')
                html.send_keys(Keys.END)
                time.sleep(2)
            except Exception:
                pass

        counter = 0
        for i in range(1000):
            counter += 1
            if counter % 10 == 0:
                time.sleep(30)
            try:
                button = driver.find_element_by_css_selector('button.infinite-next')
                button.click()
                if counter > 50:
                    time.sleep(3)
                else:
                    time.sleep(2)
                html = driver.find_element_by_tag_name('html')
                html.send_keys(Keys.END)
                if counter > 50:
                    time.sleep(3)
                else:
                    time.sleep(2)
            except Exception as e:
                print('exception ---- ', e)
                break

        time.sleep(1)
        links = []
        items_selen = driver.find_elements_by_css_selector('span.ellipsisBlock')
        for i in items_selen:
            link = i.find_element_by_css_selector('a')
            link = link.get_attribute('href')
            links.append(link)
        links = links[4:]  # delete first 4 adds on the site

        items_prices = []
        prices = driver.find_elements_by_css_selector('span.price.actual-price')
        for i in prices:
            prices = i.text.strip()
            items_prices.append(prices)
        items_prices = items_prices[4:]  # delete first 4 adds on the site
        prices = [float(i[:-1]) for i in items_prices]

        price_dict = dict(zip(links,prices))
        self.price_dict = price_dict

        links = []
        for key, val in price_dict.items():
            links.append(key)

        for url in links:
            time.sleep(2)
            yield scrapy.Request(url=url, callback=self.parse_detail)

    def parse_detail(self, response):
        product_name = response.css('div.product-name > h1::text').extract_first().strip()

        product_price, display_size, display_features, display_coating, resolution, touchscreen, operating_system, \
        weight, colour, cpu_manufacturer, cpu_model, cpu_cores, cpu_speed, cpu_turbo_speed, ram, max_ram, ram_type, \
        ram_slots_in_use, total_ram_slots, graphics_controller, vram, hdd, ssd, lan, max_battery_runtime = [None] * 25

        for key, val in self.price_dict.items():
            if key == response.request.url:
                product_price = val

        table = response.css('table.data-table > tbody > tr > td::text').extract()
        t = []
        for i in table:
            t.append(i.strip())

        for i in range(len(t)):
            if t[i] == 'Display size':
                try:
                    s = t[i+1]
                    s = s.split('(')
                    display_size = float(s[-1][:-2])
                except Exception:
                    pass
            if t[i] == 'Display Features':
                try:
                    display_features = t[i+1]
                except Exception:
                    pass
            if t[i] == 'Display coating':
                display_coating = t[i+1]
            if t[i] == 'Resolution':
                resolution = t[i+1]
            if t[i] == 'Touchscreen':
                touchscreen = t[i+1]
            if t[i] == 'Operating System':
                operating_system = t[i+1]
            if t[i] == 'Weigth':
                weight = t[i+1]
            if t[i] == 'Colour':
                colour = t[i+1]

            if t[i] == 'CPU Manufacturer':
                cpu_manufacturer = t[i+1]
            if t[i] == 'CPU Modell':
                cpu_model = t[i+1]
            if t[i] == 'CPU Cores':
                cpu_cores = t[i+1]
            if t[i] == 'CPU Speed':
                cpu_speed = t[i+1]
            if t[i] == 'CPU Turbo Speed':
                cpu_turbo_speed = t[i+1]

            if t[i] == 'RAM':
                ram = t[i+1]
            if t[i] == 'Max. RAM':
                max_ram = t[i+1]
            if t[i] == 'RAM type':
                ram_type = t[i+1]
            if t[i] == 'No. of RAM slots in use':
                try:
                    ram_slots_in_use = int(t[i+1])
                except Exception:
                    pass
            if t[i] == 'No. of total RAM slots':
                try:
                    total_ram_slots = int(t[i+1])
                except Exception:
                    pass

            if t[i] == 'Graphics Controller':
                graphics_controller = t[i+1]
            if t[i] == 'VRAM':
                vram = t[i+1]

            if t[i] == 'HDD capacity':
                hdd = t[i+1]
            if t[i] == 'SSD Storage':
                ssd = t[i+1]

            if t[i] == 'Wireless LAN (Wi-Fi)':
                lan = t[i+1]

            if t[i] == 'Max. Battery Runtime (approx.)':
                max_battery_runtime = t[i+1]

        yield {
            'product_name': product_name,
            'product_price': product_price,
            'display_size': display_size,
            'display_features': display_features,
            'display_coating': display_coating,
            'resolution': resolution,
            'touchscreen': touchscreen,
            'operating_system': operating_system,
            'weight': weight,
            'colour': colour,

            'cpu_manufacturer': cpu_manufacturer,
            'cpu_model': cpu_model,
            'cpu_cores': cpu_cores,
            'cpu_speed': cpu_speed,
            'cpu_turbo_speed': cpu_turbo_speed,

            'ram': ram,
            'max_ram': max_ram,
            'ram_type': ram_type,
            'ram_slots_in_use': ram_slots_in_use,
            'total_ram_slots': total_ram_slots,

            'graphics_controller': graphics_controller,
            'vram': vram,

            'hdd': hdd,
            'ssd': ssd,

            'lan': lan,

            'max_battery_runtime': max_battery_runtime,
            'item_link': response.request.url,
        }

