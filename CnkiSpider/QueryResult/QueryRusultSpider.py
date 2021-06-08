from CnkiSpider.CnkiNetWalker import Person
from CnkiSpider.CnkiData import NameList, CnkiQueryData
from PiePieSpider.Frame import SimpleSpiderFrame, WorkImage
import requests
from pandas import ExcelWriter

if __name__ == "__main__":
    requests.packages.urllib3.disable_warnings()
    nameList = NameList("Example_NameList.xlsx")
    names = nameList.Names

    workImagePath = "Data/WorkImage.json"
    with open("Data/LogFile.txt", "a", encoding = "utf8") as logFile:
        # Create an instance of spider
        spider = SimpleSpiderFrame(Person, logFile = logFile)

        # If new start:
        spider.NewStart(names, workImagePath, 30)

        # If continue
        """
        spider.Continue(
            outputPath = workImagePath, 
            groupSize = 30, 
            workImagePath = workImagePath
        )
        """

    data = WorkImage.FromJson(workImagePath).dataStorage
    queryData = CnkiQueryData(data, nameList)

    with ExcelWriter("Data/ExampleResult.xlsx", engine = "xlsxwriter") as excelWriter:
        queryData.PeopleInfo.to_excel(excelWriter, sheet_name = "PeopleInfo", index = False)
        queryData.PeopleWorks.to_excel(excelWriter, sheet_name = "PeopleWorks", index = False)

