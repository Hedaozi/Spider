from pandas import DataFrame, ExcelFile, concat

class NameList():
    def __init__(self, path: str):
        self.path = path
        self.Read()
        return
    
    def Read(self):
        with ExcelFile(self.path, engine = "openpyxl") as excelFile:
            self.nameListDuplicated = excelFile.parse("Dup")
            self.nameListNotDuplicated = excelFile.parse("NoDup")
        return

    def IsDupName(self, name):
        return name in self.Duplicated

    @property
    def Duplicated(self) -> list:
        return [record["name_Pure"] for record in self.nameListDuplicated.to_dict("records")]

    @property
    def NotDuplicated(self) -> list:
        return [record["name_Pure"] for record in self.nameListNotDuplicated.to_dict("records")]

    @property
    def Names(self)  -> list:
        names = list(set(self.Duplicated) | set(self.NotDuplicated))
        return [{"name": name} for name in sorted(names)]

class CnkiQueryData():
    def __init__(self, data: list, nameList: NameList):
        self.data = data
        self.nameList = nameList
        self.isGeneratePeopleInfo = False
        self.isGeneratePeopleWorks = False
        return
    
    # Attributes
    @property
    def PeopleInfo(self) -> DataFrame:
        if not self.isGeneratePeopleInfo:
            self.peopleInfo = DataFrame([
                {
                    "Name": personInfo["name"],
                    "IsDupName":  self.nameList.IsDupName(personInfo["name"]),
                    "WorksCount": personInfo["WorksCount"]
                }
                for personInfo in self.data
            ])
            self.isGeneratePeopleInfo = True
        return self.peopleInfo

    @property
    def PeopleWorks(self) -> DataFrame:
        if not self.isGeneratePeopleWorks:
            self.peopleWorks = concat([
                DataFrame([
                    {
                        "AuthorFocused": personWorks["name"],
                        "IsDupName": self.nameList.IsDupName(personWorks["name"]),
                        "WorksCount": personWorks["WorksCount"],
                        "Title": personWork["TitleInList"],
                        "AuthorsCount": len(personWork["AuthorInList"]),
                        "Authors": personWork["AuthorInList"],
                        "Source": personWork["SourceInList"],
                        "Date": personWork["DateInList"],
                        "Type": personWork["TypeInList"],
                        "Cited": (
                            0 if personWork["CitedInList"] == None
                            else int(personWork["CitedInList"])
                        ),
                        "Downloaded": (
                            0 if personWork["DownloadedInList"] == None
                            else int(personWork["DownloadedInList"])
                        ),
                        "AuthorsDepartment": personWork["AuthorDepartment"],
                        "Keywords": personWork["Keywords"],
                        "Abstract": personWork["Abstract"]
                    }
                    for personWork in personWorks["Works"]
                ])
                for personWorks in self.data
            ])
            self.peopleWorks.reset_index(drop = True)
            self.isGeneratePeopleWorks = True
        return self.peopleWorks

    @property
    def AuthorsCountMax(self) -> int:
        peopleWorks = self.PeopleWorks
        authorsCountMax = peopleWorks["AuthorsCount"].max()
        return authorsCountMax
