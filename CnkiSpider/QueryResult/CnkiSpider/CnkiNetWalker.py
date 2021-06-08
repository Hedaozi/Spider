from pandas.core.frame import DataFrame
from PiePieSpider.Content import *
from .CnkiQueryTemplate import *
from pandas import read_html
from itertools import chain
from traceback import format_exc
import time

class WorksCollection(RequestGetter):
    # Static Members
    emptyFlag = "抱歉，暂无数据，可尝试更换检索词。"

    worksEmptyXpath = ["//p[@class='no-content']"]

    worksCountXpath = ["//div[@id='countPageDiv']//em/text()"]

    worksXpath = ["//div[@class='middle']"]

    workInformationXpaths = {
        "Title": [
            ".//a[@class='fz14']/text()", 
            ".//h6/a/text()"
        ],
        "Href": [".//a[@class='fz14']/@href"],
        "Author": [
            ".//div[@class='authorinfo']//p/a//text()",
            ".//div[@class='authorinfo']//p/text()"
        ],
        "AuthorDepartment": [
            ".//div[@class='authorinfo']//span/a//text()",
            ".//div[@class='authorinfo']//span//text()"],
        "Type": [".//p[@class='baseinfo']/em/text()"],
        "Source": [".//p[@class='baseinfo']/span/a/text()"],
        "Date": [".//p[@class='baseinfo']//span[@class='date']/text()"],
        "Cited": [".//p[@class='baseinfo']//a[@class='KnowledgeNetLink']//text()"],
        "Downloaded": [".//p[@class='baseinfo']//a[@class='downloadCnt']//text()"],
        "Abstract": [".//p[@class='abstract']/text()[2]"],
        "Keywords": [".//p[@class='keywords']//a/text()"]
    }

    # Construct Method
    def __init__(self, url: str, headers: dict):
        super().__init__(url, headers)
        self.isParseElementTree = False
        self.isEmpty = None
        self.isGetDetails = False
        self.isGetList = False
        self.isGetWorks = False
        return

    # Methods
    def GetDetails(self):
        if self.IsEmpty:
            return
        self.details = [
            self.DropDimension(self.DropAllSpacing(dict([
                (label, XmlParser.TryCatchXpath(worksElementTree, xpath)) 
                for label, xpath in self.workInformationXpaths.items()
            ])))
            for worksElementTree in XmlParser.TryCatchXpath(self.ElementTree, self.worksXpath)
        ]
        for work in self.details:
            if isinstance(work["Author"], str):
                work["Author"] = [work["Author"]]
        self.isGetDetails = True
        return

    def GetList(self):
        if self.IsEmpty:
            return
        self.list = read_html(self.Text, encoding = "utf8")[0]
        self.list.drop(["Unnamed: 0", "操作"], axis = 1, inplace = True)
        self.list.rename(
            columns = {
                "题名": "TitleInList", 
                "作者": "AuthorInList", 
                "来源": "SourceInList", 
                "发表时间": "DateInList", 
                "数据库": "TypeInList", 
                "被引": "CitedInList", 
                "下载": "DownloadedInList"
            }, 
            inplace = True
        )
        self.list["AuthorInList"] = self.list["AuthorInList"].apply(
            lambda author: self.SplitAuthor(author)
        )
        self.list["CitedInList"] = self.list["CitedInList"].apply(
            lambda cited: str(int(cited)) if str(cited) != "nan" else None
        )
        self.list["DownloadedInList"] = self.list["DownloadedInList"].apply(
            lambda downloaded: str(int(downloaded)) if str(downloaded) != "nan" else None
        )
        self.isGetList = True
        return

    def GetWorks(self):
        if self.IsEmpty:
            return
        self.works = deepcopy(self.Details)
        records = self.List.to_dict("records")
        for index, work in enumerate(self.works):
            work.update(records[index])
            work.update({
                "TitleSame": work["Title"] == work["TitleInList"],
                "AuthorSame": work["Author"] == work["AuthorInList"],
                "SourceSame": work["Source"] == work["SourceInList"],
                "DateSame": work["Date"] == work["DateInList"],
                "TypeSame": work["Type"].replace("【","").replace("】", "") == work["TypeInList"],
                "CitedSame": work["Cited"] == work["CitedInList"],
                "DownloadedSame": work["Downloaded"] == work["DownloadedInList"]
            })
        self.isGetWorks = True
        return

    # Attributes
    @property
    def Text(self) -> str:
        return super().Text.replace("<font class=Mark>", "").replace("</font>", "")

    @property
    def IsEmpty(self) -> bool:
        if self.isEmpty == None:
            self.isEmpty = (self.emptyFlag in self.Text)
        return self.isEmpty

    @property
    def ElementTree(self) -> etree._ElementTree:
        if not self.isParseElementTree:
            self.elementTree = XmlParser.ElementTree(self.Text)
            self.isParseElementTree = True
        return self.elementTree

    @property
    def WorksCount(self) -> int:
        if self.IsEmpty:
            return 0
        else:
            return int(XmlParser.TryCatchXpath(self.ElementTree, self.worksCountXpath)[0])

    @property
    def Details(self) -> list:
        if self.IsEmpty:
            return list()
        if not self.isGetDetails:
            self.GetDetails()
        return self.details
    
    @property
    def List(self) -> DataFrame:
        if self.IsEmpty:
            return list()
        if not self.isGetList:
            self.GetList()
        return self.list
    
    @property
    def Works(self) -> list:
        if self.IsEmpty:
            return list()
        if not self.isGetWorks:
            self.GetWorks()
        return self.works

    # Utils
    @classmethod
    def SplitAuthor(cls, author: str):
        result = author.split(";")
        result = list(chain(*[splited.split(",") for splited in result]))
        result = list(chain(*[splited.split("，") for splited in result]))
        result = [r[:-1] if len(r) > 0 and r[-1] == " " else r for r in result]
        return result

    @classmethod
    def DropAllSpacing(cls, obj):
        if isinstance(obj, list):
            return [cls.DropAllSpacing(item) for item in obj]
        if isinstance(obj, tuple):
            return tuple([cls.DropAllSpacing(item) for item in obj])
        if isinstance(obj, dict):
            return dict([(key, cls.DropAllSpacing(value)) for key, value in obj.items()])
        elif isinstance(obj, str):
            return XmlParser.DropAllSpacing(obj)
        else:
            return obj

    @classmethod
    def DropDimension(cls, obj):
        if isinstance(obj, list):
            if len(obj) == 1:
                return obj[0]
            else:
                return [cls.DropDimension(item) for item in obj]
        if isinstance(obj, tuple):
            return tuple([cls.DropDimension(item) for item in obj])
        if isinstance(obj, dict):
            return dict([(key, cls.DropDimension(value)) for key, value in obj.items()])
        else:
            return obj

class WorksCollections():
    # Construct Method
    def __init__(self, name: str, logFile = None):
        self.name, self.logFile = name, logFile
        self.isGetWorks = False
        return

    # Methods
    @classmethod
    def GetWorksCount(cls, name: str) -> tuple:
        firstPage = WorksCollection(queryUrl, GetHeaders())
        DetialsFormData = GetFormData(name)
        firstPage.Post(DetialsFormData)
        time.sleep(0.5)
        worksCount = firstPage.WorksCount
        firstPage.GetDetails()
        ListFormData = GetFormData(name, details = False)
        firstPage.Post(ListFormData)
        time.sleep(0.5)
        firstPage.GetList()
        return worksCount, firstPage.Works
    
    @classmethod
    def GetPageWorks(cls, name: str, curPage: int = 2) -> list:
        page = WorksCollection(queryUrl, GetHeaders())
        DetialsFormData = GetFormData(name, curPage = curPage)
        page.Post(DetialsFormData)
        time.sleep(0.5)
        page.GetDetails()
        ListFormData = GetFormData(name, curPage = curPage, details = False)
        page.Post(ListFormData)
        time.sleep(0.5)
        page.GetList()
        return page.Works

    @classmethod
    def GetWorks(cls, name: str, logFile = None) -> tuple:
        cls.ReportProcess(1, logFile = logFile)
        worksCount, firstPageWorks = cls.GetWorksCount(name)
        if worksCount == 0:
            return worksCount, list()
        works = firstPageWorks
        pagesCount = worksCount // 50 + (not (worksCount % 50 == 0))
        for pageIndex in range(2, pagesCount + 1):
            cls.ReportProcess(pageIndex, pagesCount = pagesCount, logFile = logFile)
            curPageWorks = cls.GetPageWorks(name, pageIndex)
            works.extend(curPageWorks)
        return worksCount, works

    @classmethod
    def ReportProcess(cls, curPage: int, pagesCount = "Unknown", logFile = None):
        content = "Curent page index: {}, Pages count: {}.".format(curPage, pagesCount)
        print(content)
        if not logFile == None:
            logFile.write(content + "\n")
        return

    # Attributes
    @property
    def Works(self) -> list:
        if not self.isGetWorks:
            self.worksCount, self.works = self.GetWorks(self.name, self.logFile)
            self.isGetWorks = True
        return self.works
    
    @property
    def WorksCount(self) -> int:
        return self.worksCount

class Person():
    def __init__(self, personInfo, logFile = None):
        self.personInfo, self.logFile = personInfo, logFile
        self.name = personInfo["name"]
        self.worksCollections = WorksCollections(self.name, logFile)
        return

    @property
    def Result(self) -> tuple:
        self.ReportProcess()
        try:
            result = deepcopy(self.personInfo)
            result.update({
                "Works": self.worksCollections.Works,
                "WorksCount": self.worksCollections.WorksCount
            })
            return False, (result, list())
        except:
            return True, format_exc()

    def ReportProcess(self):
        content = "Collecting information about {}....".format(self.name)
        print(content)
        if not self.logFile == None:
            self.logFile.write(content + "\n")
