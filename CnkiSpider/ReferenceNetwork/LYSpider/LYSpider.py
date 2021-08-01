from CnkiSpider.CnkiSpider import CnkiSpider, NxgpSpider
from traceback import format_exc

if 0:#__name__ == "__main__":
    try:
        ## "refer" for NxpgSpider is equal to "1" in CnkiSpider. And "citation" is equal to "3"
        nxgp_spider = NxgpSpider(reftypes = ["citation", "refer"])
        center_paper = {
            "href": "/kcms/detail?v=3uoqIhG8C44YLTlOAiTRKlTbz1094wJQVZnatvxrRBKJ9QVJcwU3YQwgLjySCSixDkn21cvHFgRdx0NUcdYi2XCvo2Yul0cQ&uniplatform=NZKPT",
            "filename": "BDZK198904000",
            "depth": 0,
            "Referer": ""
        }
        nxgp_spider.start_from_a_paper(center_paper)
        nxgp_spider.paper_information_dataframe.to_csv("nxgp_paper_information.csv", encoding = "utf8")
        nxgp_spider.reference_network.to_csv("nxgp_reference_network.csv", encoding = "utf8")
    except:
        print(format_exc())
    finally:
        nxgp_spider.output_working_image("nxgp_working_image.json")

        
if 0:#__name__ == "__main__":
    try:
        cnki_spider = CnkiSpider.load_working_image("working_image.json")
        cnki_spider.fix_error()
        cnki_spider.paper_information_dataframe.to_csv("paper_information.csv", encoding = "utf8")
        cnki_spider.reference_network.to_csv("reference_network.csv", encoding = "utf8")
    except:
        print(format_exc())
    finally:
        cnki_spider.output_working_image("working_image.json")
