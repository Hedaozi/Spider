import requests

from json import dump, load

from pandas import DataFrame

import time
from datetime import datetime

from traceback import format_exc

from CnkiSpider.CnkiHeadersGenerator import CnkiHeadersGenerator, NxgpHeadersGenerator
from CnkiSpider.CnkiParser import CnkiParser, NxgpParser
from CnkiSpider.SimpleQueue import SimpleQueue

class CnkiSpider():
    """Get CNKI papers' information and reference relationships.
    __init__(self, reftypes: list[int], sleep_time: float = 0.2)
        reftypes: Reference types while searching for in certain depth.
        sleep_time: The number of seconds between two requests, default as 0.2.

    Properties
        reference_list
        paper_information_dataframe
        reference_network

    Methods
        start_from_a_paper(self, center_paper)
        continue_spider(self)
        fix_error(self)
        output_working_image(self, path)

    Staticmethods
        get_paper_info(paper)
        get_refs(paper)
        get_refs_first_page(paper)
        get_refs_later_page(paper, page)
        generate_url_paper(paper)
        generate_url_ref(paper, page)
        get_html(url, headers)
        load_working_image(path)
    """
    def __init__(self, reftypes: list, sleep_time: float = 0.2):
        self.__reftypes = reftypes
        self.__sleep_time = sleep_time
        self.__depth_max = len(self.__reftypes)
        self.__papers = dict()
        self.__ref_net = list()
        self.__search_queue = SimpleQueue()
        self.__errors = SimpleQueue()
        self.__errors_info = SimpleQueue()
        return
    
    def start_from_a_paper(self, center_paper: dict):
        """Start spider
        center_paper: A dict or a url string.
            dict. {"dbcode": str, "dbname": str, "filename": str, "v": str, "depth": int,"Referer": str}
            string. A copy from browser.
        """
        paper = (
            center_paper if type(center_paper) == dict
            else CnkiParser.parse_paper_url(center_paper)
        )
        self.__search_queue.add(paper)
        self.__start_spider()
        return
    
    def continue_spider(self):
        if self.__search_queue.head >= 1:
            self.__search_queue.add(self.__search_queue.last_one)

        self.__start_spider()
        return

    def fix_error(self):
        error_items = self.__errors.pop_all()
        self.__errors_info.clean()
        self.__search_queue.add_items(error_items)
        self.__start_spider()
        return
    
    def __start_spider(self):
        while not self.__search_queue.is_empty:
            print(self.__search_queue.head, self.__search_queue.tail, sep = ", ", end = ": ")
            paper = self.__search_queue.pop()
            paper.update({
                "Time": datetime.now().strftime("%m/%d/%Y %H:%M:%S")
            })

            try:
                paper.update(CnkiSpider.get_paper_info(paper))
                if paper["filename"] not in self.__papers.keys():
                    self.__papers.update({
                        paper["filename"]: paper
                    })
            except:
                self.__errors.add(paper)
                self.__errors_info.add({
                    "PaperInformation": format_exc()
                })
                print(format_exc())

            try:
                if paper["depth"] < self.__depth_max:
                    reftype = self.__reftypes[paper["depth"]]
                    refs = CnkiSpider.get_refs(paper, reftype)
                    for ref in refs:
                        if self.__reftypes[paper["depth"]] == 1:
                            self.__ref_net.append((paper["filename"], ref["filename"]))
                        else:
                            self.__ref_net.append((ref["filename"], paper["filename"]))
                        ref.update({
                            "depth": paper["depth"] + 1,
                            "Referer": CnkiSpider.generate_url_paper(paper)
                        })
                        if not ref["filename"] in self.__papers.keys(): 
                            self.__search_queue.add(ref)
            except:
                self.__errors.add(paper)
                self.__errors_info.add({
                    "PaperReference": format_exc()
                })
                print(format_exc())

            self.__sleep()
        return
    
    @staticmethod
    def get_paper_info(paper: dict) -> dict:
        """Get information of a paper."""
        Referer = paper["Referer"]
        headers = CnkiHeadersGenerator.get_updated_headers(Referer, update_time = True)

        url = CnkiSpider.generate_url_paper(paper)
        
        print("Collecting {}".format(CnkiSpider.generate_url_paper(paper)))
        html = CnkiSpider.get_html(url, headers)
        paper_new = CnkiParser.parse_paper_html(html)
        paper_new.update({
            "Referer": url
        })
        print(paper_new)
        return paper_new

    @staticmethod
    def get_refs(paper: dict, reftype: int) -> list:
        """Get reference.
        Firstly parse the first list page and get the number of list pages.
        Then parse other list pages."""
        refs = list()
        first_page = CnkiSpider.get_refs_page(paper, 1, reftype)
        refs.extend(first_page["refs"])
        print(first_page["refs"])

        for i in range(2, first_page["page_max"] + 1):
            page = CnkiSpider.get_refs_page(paper, i, reftype)
            refs.extend(page["refs"])
            print(page["refs"])

        return refs
    
    @staticmethod
    def get_refs_page(paper: dict, page: int, reftype: int) -> list:
        """Get the reference pages.
        The referer of first list page is the detail page.
        The referer of later list page is last list page."""
        Referer = (
            CnkiSpider.generate_url_paper(paper) if page == 1
            else CnkiSpider.generate_url_ref(paper, page - 1, reftype)
        )
        headers = CnkiHeadersGenerator.get_updated_headers(Referer)

        url = CnkiSpider.generate_url_ref(paper, page, reftype)
        print("Collecting {}".format(url))
        html = CnkiSpider.get_html(url, headers)

        papers_new = CnkiParser.parse_ref_html(html)
        for paper_new in papers_new["refs"]:
            paper_new.update({
                "Referer": url
            })
        return papers_new

    @staticmethod
    def generate_url_paper(paper: dict) -> str:
        """Generate url of paper."""
        href = paper["href"]
        index = "https://kns.cnki.net"
        return index + href
    
    @staticmethod
    def generate_url_ref(paper: dict, page: int, reftype: int) -> str:
        """Generate url of reference."""
        dbcode = paper["dbcode"]
        dbname = paper["dbname"]
        filename = paper["filename"].lower()
        vl = paper["vl"]
        url = (
            "https://kns.cnki.net/kcms/detail/frame/list.aspx?" + 
            "dbcode={}&dbname={}&filename={}".format(dbcode, dbname, filename) + 
            "&RefType={}&vl={}".format(reftype, vl)
        )
        url = (
            url + "&CurDBCode=CJFD&page={}".format(page) if page >=2 
            else url
        )
        return url
    
    @staticmethod
    def get_html(url: str, headers: dict) -> str:
        """Get html code of a url."""
        response = requests.get(url, headers = headers)
        return response.text
    
    def output_working_image(self, path: str):
        working_image = {
            "depth_max": self.__depth_max,
            "reftypes": self.__reftypes,
            "sleep_time": self.__sleep_time,
            "papers": self.__papers,
            "ref_net": self.__ref_net,
            "search_queue": self.__search_queue.as_dict,
            "errors": self.__errors.as_dict,
            "errors_info": self.__errors_info.as_dict
        }
        with open(path, "w", encoding = "utf8") as f:
            dump(working_image, f, ensure_ascii = False, indent = 4)
        return working_image
    
    @staticmethod
    def load_working_image(path: str):
        with open(path, "r", encoding = "utf8") as f:
            working_image = load(f)
        cnki_spider = CnkiSpider(
            reftypes = working_image["reftypes"],
            sleep_time = working_image["sleep_time"]
        )
        cnki_spider.__papers = working_image["papers"]
        cnki_spider.__ref_net = working_image["ref_net"]
        cnki_spider.__search_queue = SimpleQueue.load_from_dict(working_image["search_queue"])
        cnki_spider.__errors = SimpleQueue.load_from_dict(working_image["errors"])
        cnki_spider.__errors_info = SimpleQueue.load_from_dict(working_image["errors_info"])
        return cnki_spider
    
    @property
    def reference_list(self):
        """The first column is citer and the second column is cited."""
        return DataFrame(self.__ref_net)

    @property
    def reference_network(self):
        """The first column is citer and the second column is cited."""
        return DataFrame(self.__ref_net)

    @property
    def paper_information_dataframe(self):
        """Every record is a paper."""
        return DataFrame(self.__papers.values())

    def __sleep(self):
        time.sleep(self.__sleep_time)
        return


class NxgpSpider():
    """Get CNKI papers' information and reference relationships.
    __init__(self, reftypes: list[int], sleep_time: float = 0.2)
        reftypes: Reference types while searching for in certain depth.
        sleep_time: The number of seconds between two requests, default as 0.2.

    Properties
        reference_list
        paper_information_dataframe
        reference_network

    Methods
        start_from_a_paper(self, center_paper)
        continue_spider(self)
        fix_error(self)
        output_working_image(self, path)

    Staticmethods
        get_paper_info(paper)
        get_refs(paper)
        get_refs_first_page(paper)
        get_refs_later_page(paper, page)
        generate_url_paper(paper)
        generate_url_ref(paper, page)
        get_html(url, headers)
        load_working_image(path)
    """
    def __init__(self, reftypes: list, sleep_time: float = 0.2):
        self.__reftypes = reftypes
        self.__sleep_time = sleep_time
        self.__depth_max = len(self.__reftypes)
        self.__papers = dict()
        self.__ref_net = list()
        self.__search_queue = SimpleQueue()
        self.__errors = SimpleQueue()
        self.__errors_info = SimpleQueue()
        return
    
    def start_from_a_paper(self, center_paper: dict):
        """Start spider
        center_paper: A dict or a url string.
            dict. {"dbcode": str, "dbname": str, "filename": str, "v": str, "depth": int,"Referer": str}
            string. A copy from browser.
        """
        paper = (
            center_paper if type(center_paper) == dict
            else self.__parse_paper_url(center_paper)
        )
        self.__search_queue.add(paper)
        self.__start_spider()
        return
    
    def continue_spider(self):
        if self.__search_queue.head >= 1:
            self.__search_queue.add(self.__search_queue.last_one)

        self.__start_spider()
        return

    def fix_error(self):
        error_items = self.__errors.pop_all()
        self.__errors_info.clean()
        self.__search_queue.add_items(error_items)
        self.__start_spider()
        return
    
    def __start_spider(self):
        while not self.__search_queue.is_empty:
            print(self.__search_queue.head, self.__search_queue.tail, sep = ", ", end = ": ")
            paper = self.__search_queue.pop()
            paper.update({
                "Time": datetime.now().strftime("%m/%d/%Y %H:%M:%S")
            })

            try:
                paper.update(self.get_paper_info(paper))
                if paper["filename"] not in self.__papers.keys():
                    self.__papers.update({
                        paper["filename"]: paper
                    })
                else:
                    self.__papers["filename"] = self.update_dict_item(self.__papers["filename"], paper)
            except:
                self.__errors.add(paper)
                self.__errors_info.add({
                    "PaperInformation": format_exc()
                })
                print(format_exc())

            try:
                if paper["depth"] < self.__depth_max:
                    reftype = self.__reftypes[paper["depth"]]
                    refs = self.get_refs(paper, reftype)
                    for ref in refs:
                        if self.__reftypes[paper["depth"]] == "refer":
                            self.__ref_net.append((paper["filename"], ref["filename"]))
                        else:
                            self.__ref_net.append((ref["filename"], paper["filename"]))
                        ref.update({
                            "depth": paper["depth"] + 1,
                            "Referer": self.generate_url_paper(paper)
                        })
                        if not ref["filename"] in self.__papers.keys(): 
                            self.__search_queue.add(ref)
            except:
                self.__errors.add(paper)
                self.__errors_info.add({
                    "PaperReference": format_exc()
                })
                print(format_exc())

            self.__sleep()

        self.__ref_net = list(set(self.__ref_net))
        return
    
    @classmethod
    def get_paper_info(cls, paper: dict) -> dict:
        """Get information of a paper."""
        Referer = paper["Referer"]
        headers = NxgpHeadersGenerator.get_updated_headers(Referer)

        url = cls.generate_url_paper(paper)
        
        print("Collecting {}".format(cls.generate_url_paper(paper)))
        html = cls.get_html(url, headers)
        print(html)
        paper_new = NxgpParser.parse_paper_html(html)
        paper_new.update({
            "Referer": url
        })
        return paper_new

    @classmethod
    def update_dict_item(cls, dict_old: dict, dict_new: dict):
        for key in dict_new:
            if key in dict_old:
                dict_old[key] = (
                    dict_new[key] if dict_old[key] == None
                    else dict_old[key]
                )
        return dict_old

    @classmethod
    def get_refs(cls, paper: dict, reftype: int) -> list:
        """Get reference.
        Firstly parse the first list page and get the number of list pages.
        Then parse other list pages."""
        refs = list()
        first_page = cls.get_refs_page(paper, 1, reftype)
        refs.extend(first_page["refs"])

        for i in range(2, first_page["page_max"] + 1):
            print("Collecting Reference {} / {}".format(i, first_page["page_max"]))
            page = cls.get_refs_page(paper, i, reftype)
            refs.extend(page["refs"])

        return refs
    
    @classmethod
    def get_refs_page(cls, paper: dict, page: int, reftype: int) -> list:
        """Get the reference pages.
        The referer of first list page is the detail page.
        The referer of later list page is last list page."""
        Referer = (
            cls.generate_url_paper(paper) if page == 1
            else cls.generate_url_ref(paper, page - 1, reftype)
        )
        headers = NxgpHeadersGenerator.get_updated_headers(Referer)

        url = cls.generate_url_ref(paper, page, reftype)
        print("Collecting {}".format(url))
        html = cls.get_html(url, headers)

        papers_new = NxgpParser.parse_ref_html(html)
        for paper_new in papers_new["refs"]:
            paper_new.update({
                "Referer": url
            })
        return papers_new

    @classmethod
    def generate_url_paper(cls, paper: dict) -> str:
        """Generate url of paper."""
        href = paper["href"]
        index = "https://nxgp.cnki.net/"
        return index + href
    
    @classmethod
    def generate_url_ref(cls, paper: dict, page: int, reftype: str) -> str:
        """Generate url of reference."""
        v = paper["v"]
        url = "https://nxgp.cnki.net/kcms/quoted/{}?{}&vl=".format(reftype, v)
        url = (
            url + "&curdbcode=CJFD&page={}".format(page) if page >= 2 
            else url
        )
        return url
    
    @classmethod
    def get_html(cls, url: str, headers: dict) -> str:
        """Get html code of a url."""
        response = requests.get(url, headers = headers)
        return response.text
    
    def output_working_image(self, path: str):
        working_image = {
            "depth_max": self.__depth_max,
            "reftypes": self.__reftypes,
            "sleep_time": self.__sleep_time,
            "papers": self.__papers,
            "ref_net": self.__ref_net,
            "search_queue": self.__search_queue.as_dict,
            "errors": self.__errors.as_dict,
            "errors_info": self.__errors_info.as_dict
        }
        with open(path, "w", encoding = "utf8") as f:
            dump(working_image, f, ensure_ascii = False, indent = 4)
        return working_image
    
    @classmethod
    def load_working_image(cls, path: str):
        with open(path, "r", encoding = "utf8") as f:
            working_image = load(f)
        nxgp_spider = cls(
            reftypes = working_image["reftypes"],
            sleep_time = working_image["sleep_time"]
        )
        nxgp_spider.__papers = working_image["papers"]
        nxgp_spider.__ref_net = working_image["ref_net"]
        nxgp_spider.__search_queue = SimpleQueue.load_from_dict(working_image["search_queue"])
        nxgp_spider.__errors = SimpleQueue.load_from_dict(working_image["errors"])
        nxgp_spider.__errors_info = SimpleQueue.load_from_dict(working_image["errors_info"])
        return nxgp_spider
    
    @property
    def reference_list(self):
        """The first column is citer and the second column is cited."""
        return DataFrame(self.__ref_net)

    @property
    def reference_network(self):
        """The first column is citer and the second column is cited."""
        return DataFrame(self.__ref_net)

    @property
    def paper_information_dataframe(self):
        """Every record is a paper."""
        return DataFrame(self.__papers.values())

    def __sleep(self):
        time.sleep(self.__sleep_time)
        return
