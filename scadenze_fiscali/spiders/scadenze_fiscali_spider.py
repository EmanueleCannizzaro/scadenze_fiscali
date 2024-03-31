import logging
from scrapy import Spider
# from scrapy.selector import HtmlXPathSelector
from scrapy.selector import Selector
from scrapy.http.request import Request
from scadenze_fiscali.items import ScadenzeFiscaliItem
#from urlparse import urljoin
from urllib.parse import urljoin


logger = logging.getLogger(__name__)
logger.warning("This is a warning")
#from scrapy import log


class ScadenzeFiscaliSpider(Spider):
    name = "scadenze_fiscali"
    allowed_domains = ["agenziaentrate.gov.it"]
    year : int = 2012
    start_urls = [
        #f"http://www1.agenziaentrate.gov.it/documentazione/scadenzefiscali/index.htm?selezionetemporale=mese&mese={n:02}-{year}" for n in range(1, 12)
        f"https://www1.agenziaentrate.gov.it/servizi/scadenzario/main.php?mesesel={n:02}-2023" for n in range(1, 12)
    ]

    def parse(self, response):
        #hxs = HtmlXPathSelector(response)
        hxs = Selector(response)
        deadlines = hxs.select("//div[@id='lista_scad_fisc']/ul")
        items = []

        next_page = hxs.select("//div[@id='contenuti_una_colonna']/p[2]/a[last()]/@href").extract()

        if not not next_page:
            yield Request(urljoin(response.url, next_page[0]), self.parse)

        for deadline in deadlines:
            item = ScadenzeFiscaliItem()
            item['when'] = self.html_string(deadline, 'li[1]/text()')
            item['who'] = self.html_string(deadline, 'li[2]/text()')
            item['what'] = self.html_string(deadline, 'li[3]/text()')
            item['how'] = self.html_string(deadline, 'li[4]/text()')
            item['code'] = self.html_string(deadline, 'li[5]/text()')
            item['type'] = self.html_string(deadline, 'li[6]/text()')
            item['category'] = self.html_string(deadline, 'li[7]//a/text()')
            items.append(item)

        for item in items:
            yield item

    def html_string(self, item, xpath):
        res = []
        for i in item.select(xpath).extract():
            res.append(i.strip())

        return res
