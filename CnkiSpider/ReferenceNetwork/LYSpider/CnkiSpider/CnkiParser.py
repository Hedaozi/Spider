from lxml import etree
import lxml
import re

class CnkiParser():
    """To parse text."""

    re_paper_url = {
        "dbcode": r"(?<=dbcode\=).+?(?=&)",
        "dbname": r"(?<=dbname\=).+?(?=&)",
        "filename": r"(?<=filename\=).+?(?=&)",
        "v": r"(?<=v\=).+?$",
        "href": r"(?<=https://kns.cnki.net).+"
    }

    xpath_paper_html = {
        "Title": ["//h1/text()"],
        "Author": ["//h3[@class='author']/span/text()", "//h3[@class='author']/span/a/text()"], 
        "Magazine": ["//div[@class='top-tip']/span/a[1]/text()"],
        "Year": ["//div[@class='top-tip']/span/a[2]/text()"],
        "Abstract": ["//span[@class='abstract-text']/text()"],
        "Keywords": ["//p[@class='keywords']/a/text()"],
        "CitingTime": ["//input[@id='paramcitingtimes']/@value"],
        "DownloadTime": ["//p[@class='total-inform']/span[1]/text()"],
        "vl": ["//input[@id='listv']/@value"]
    }

    xpath_page_max = ".//span[@id='pc_CJFQ']/text()"

    xpath_essay_box = "//div[@class='essayBox']"
    xpath_essay_box_pcount_id = ".//span[@name='pcount']/@id"
    essay_box_type = "pc_CJFQ"
    xpath_essay_href = ".//a[@target='kcmstarget']/@href"

    parser = etree.HTMLParser(encoding = "utf-8")
    
    re_paper_href = {
        "dbcode": r"(?<=dbcode\=).+?(?=&)",
        "dbname": r"(?<=dbname\=).+?(?=&)",
        "filename": r"(?<=filename\=).+?(?=&)",
        "v": r"(?<=v\=).+?$"
    }

    @classmethod
    def parse_paper_url(cls, url: str) -> dict:
        """Get infomation from a url of a cnki paper detail page.
        Return a dict including dbcode, dbname, filename, v and href."""
        paper = {}
        for key in cls.re_paper_url.keys():
            match = cls.quick_match(cls.re_paper_url[key], url)
            paper.update({key: match})
        return paper

    @classmethod
    def parse_paper_href(cls, href: str) -> dict:
        """Get infomation from a url of a cnki paper detail page.
        Return a dict including dbcode, dbname, filename, v and href."""
        paper = {
            "href": href
        }
        for key in cls.re_paper_href.keys():
            match = cls.quick_match(cls.re_paper_href[key], href)
            paper.update({key: match})
        return paper

    @classmethod
    def quick_match(cls, reg_exp: str, string: str, index = 0) -> str:
        """Match a regular expression and a string. Return the certain item of results.
        reg_exp: Regular expression.
        string: String to be matched.
        index: The index of item returned. Default as 0.
        """
        pattern = re.compile(reg_exp)
        results = re.findall(pattern, string)
        return results[index]
    
    @classmethod
    def parse_paper_html(cls, html: str) -> dict:
        html_tree = etree.fromstring(html, parser = cls.parser)
        return cls.parse_paper_html_etree(html_tree)

    @classmethod
    def parse_ref_html(cls, html: str) -> list:
        html_tree = etree.fromstring(html, parser = cls.parser)
        return cls.parse_ref_html_etree(html_tree)
    
    @classmethod
    def parse_paper_html_etree(cls, html: lxml.etree._ElementTree) -> dict:
        info = dict()
        for item in cls.xpath_paper_html.items():
            info.update({
                item[0]: cls.try_catch_by_xpath(html, item[1])
            })
        return info

    @classmethod
    def parse_ref_html_etree(cls, html: lxml.etree._ElementTree) -> list:
        paper_count = html.xpath(cls.xpath_page_max)[0]
        paper_count = int(paper_count)
        page_max = (
            paper_count // 10 if paper_count % 10 == 0
            else paper_count // 10 + 1
        )

        essay_boxs = html.xpath(cls.xpath_essay_box)
        essay_box = list(filter(
            lambda essay_box: 
                cls.drop_spacing(essay_box.xpath(cls.xpath_essay_box_pcount_id)[0]) == cls.essay_box_type, 
            essay_boxs
        ))
        hrefs = essay_box[0].xpath(cls.xpath_essay_href)
        refs = [cls.parse_paper_href(href) for href in hrefs]

        info = {
            "page_max": page_max,
            "refs": refs
        }
        return info
    
    @classmethod
    def try_catch_by_xpath(xml: lxml.etree._ElementTree, xpaths: str, index: int = 0, sep: str = "\t"):
        if index >= len(xpaths):
            return None
        try:
            result = [element for element in xml.xpath(xpaths[index])]
            result = [r.replace(" ", "").replace("\r\n", "") for r in result]
            result = (
                sep.join(result) if result != []
                else cls.try_catch_by_xpath(xml, xpaths, index + 1, sep)
            )
            return result
        except:
            return cls.try_catch_by_xpath(xml, xpaths, index + 1, sep)
    
    @classmethod
    def drop_spacing(cls, string: str):
        return string.replace("\r\n", "").replace(" ", "")

class NxgpParser():
    """Similar to CnkiParser(). But for nxpg.cnki.net"""
    xpath_paper_html = {
        "Title": ["//div[@class='wx-tit']/h1/text()"],
        "Author": ["//div[@class='wx-tit']/h3[@id='authorpart']//a/text()", "//div[@class='wx-tit']/h3/span/text()"], 
        "Magazine": ["//div[@class='container']//div[@class='top-tip']/span/a[1]/text()"],
        "Year": ["//div[@class='container']//div[@class='top-tip']/span/a[2]/text()"],
        "PageRange": ["//div[@class='container']//div[@class='top-tip']/span/text()"],
        "Abstract": ["//span[@id='ChDivSummary']/text()"],
        "Keywords": ["//p[@class='keywords']/a/text()"],
        "CitingTime": ["//input[@id='paramcitingtimes']/@value"],
        "DownloadTime": ["//p[@class='total-inform']/span[1]/text()"],
        "dbcode": ["//input[@id='paramdbcode']/@value"],
        "dbname": ["//input[@id='paramdbname']/@value"],
        "v": ["//input[@id='paramkcmslink']/@value"]
    }

    xpath_page_max = ".//span[@id='pc_JOURNAL']/text()"

    xpath_essay_box = "//div[@class='essayBox']"
    xpath_essay_box_pcount_id = ".//span[@name='pcount']/@id"
    essay_box_type = "pc_JOURNAL"
    xpath_essay_href = ".//a[@target='kcmstarget']/@href"
    xpath_essay_filename = ".//input[@class='exportparams']/@value"

    parser = etree.HTMLParser(encoding = "utf-8")

    @classmethod
    def quick_match(cls, reg_exp: str, string: str, index = 0) -> str:
        """Match a regular expression and a string. Return the certain item of results.
        reg_exp: Regular expression.
        string: String to be matched.
        index: The index of item returned. Default as 0.
        """
        pattern = re.compile(reg_exp)
        results = re.findall(pattern, string)
        return results[index]
    
    @classmethod
    def parse_paper_html(cls, html: str) -> dict:
        html_tree = etree.fromstring(html, parser = cls.parser)
        return cls.parse_paper_html_etree(html_tree)

    @classmethod
    def parse_ref_html(cls, html: str) -> list:
        html_tree = etree.fromstring(html, parser = cls.parser)
        return cls.parse_ref_html_etree(html_tree)
    
    @classmethod
    def parse_paper_html_etree(cls, html: lxml.etree._ElementTree) -> dict:
        info = dict()
        for item in cls.xpath_paper_html.items():
            info.update({
                item[0]: cls.try_catch_by_xpath(html, item[1])
            })
        return info

    @classmethod
    def parse_ref_html_etree(cls, html: lxml.etree._ElementTree) -> list:
        paper_count = html.xpath(cls.xpath_page_max)[0]
        paper_count = int(paper_count)
        page_max = (
            paper_count // 10 if paper_count % 10 == 0
            else paper_count // 10 + 1
        )

        essay_boxs = html.xpath(cls.xpath_essay_box)
        essay_box = list(filter(
            lambda essay_box: 
                cls.drop_spacing(essay_box.xpath(cls.xpath_essay_box_pcount_id)[0]) == cls.essay_box_type, 
            essay_boxs
        ))
        hrefs = essay_box[0].xpath(cls.xpath_essay_href)
        filenames = essay_box[0].xpath(cls.xpath_essay_filename)
        filenames = [filename.split("!")[1] for filename in filenames]
        refs = [{"href": hrefs[i], "filename": filenames[i]} for i in range(len(hrefs))]

        info = {
            "page_max": page_max,
            "refs": refs
        }
        return info
    
    @classmethod
    def try_catch_by_xpath(cls, xml: lxml.etree._ElementTree, xpaths: str, index: int = 0, sep: str = "\t"):
        if index >= len(xpaths):
            return None
        try:
            result = [element for element in xml.xpath(xpaths[index])]
            result = [r.replace(" ", "").replace("\r", "").replace("\n", "") for r in result]
            result = (
                sep.join(result) if result != []
                else cls.try_catch_by_xpath(xml, xpaths, index + 1, sep)
            )
            return result
        except:
            return cls.try_catch_by_xpath(xml, xpaths, index + 1, sep)
    
    @classmethod
    def drop_spacing(cls, string: str):
        return string.replace("\r\n", "").replace(" ", "")