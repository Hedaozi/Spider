from datetime import datetime
from copy import deepcopy

class CnkiHeadersGenerator():

    Cookie_templete = {
        "Ecp_notFirstLogin": "EJHLyg;",
        "Ecp_ClientId": "2210313121801733141;",
        "Ecp_session": "1;",
        "ASP.NET_SessionId": "m2dpnredttnqcqhg42cxmh3e;",
        "SID_kns8": "123120;",
        "cnkiUserKey": "de6b2eae-6386-b38e-f5c5-de3c3296e3e0;",
        "SID_kns_new": "kns123110;",
        "CurrSortFieldType": "desc;",
        "Ecp_ClientIp": "211.71.28.244;",
        "SID_kcms": "124114;",
        "knsLeftGroupTag": "1;",
        "CurrSortField": "%e5%8f%91%e8%a1%a8%e6%97%b6%e9%97%b4%2f(%e5%8f%91%e8%a1%a8%e6%97%b6%e9%97%b4%2c%27TIME%27);",
        "c_m_LinID": "LinID=WEEvREcwSlJHSldSdmVqMDh6a1dqZUtoQzJxUnVSM29KOFFxRU1tdFBMbz0=$9A4hF_YAuvQ5obgVAqNKPCYcEjKensW4IQMovwHtwkF4VYPoHbKxJw!!&ot={};",
        "LID": "WEEvREcwSlJHSldSdmVqMDh6a1dqZUtoQzJxUnVSM29KOFFxRU1tdFBMbz0=$9A4hF_YAuvQ5obgVAqNKPCYcEjKensW4IQMovwHtwkF4VYPoHbKxJw!!;",
        "c_m_expire": "{};",
        "_pk_ses": "*;",
        'Ecp_LoginStuts": "{"IsAutoLogin":false,"UserName":"K10093","ShowName":"%E4%B8%AD%E5%9B%BD%E4%BA%BA%E6%B0%91%E5%A4%A7%E5%AD%A6","UserType":"bk","BUserName":"","BShowName":"","BUserType":"","r":"EJHLyg"};'
        "_pk_id": "dadb0bc4-6998-4db9-9914-9c74c34f7187.1615609138.29.1616551872.1616551767."
    }

    headers_templete = {
        "Host": "kns.cnki.net",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36 Edg/89.0.774.50",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6"
    }

    time_now = None

    @classmethod
    def get_updated_cookie(cls) -> str:
        cookie_updated = deepcopy(cls.Cookie_templete)
        cookie_updated["c_m_LinID"] = cookie_updated["c_m_LinID"].format(
            cls.time_now.strftime("%m/%d/%Y %H:%M:%S")
        )
        cookie_updated["c_m_expire"] = cookie_updated["c_m_expire"].format(
            cls.time_now.strftime("%Y-%m-%d %H:%M:%S")
        )
        Cookie = " ".join([item[0] + "=" + item[1] for item in cookie_updated.items()])
        return Cookie
    
    @classmethod
    def get_updated_headers(cls, Referer: str, update_time = False) -> dict:
        if update_time: cls.time_now = datetime.now()
        Cookie = cls.get_updated_cookie()
        headers = deepcopy(cls.headers_templete)
        headers.update({
            "Referer": Referer,
            "Cookie": Cookie
        })
        return headers

class NxgpHeadersGenerator():

    Cookie_templete = {
        "Ecp_notFirstLogin": "o9n38w;",
        "SID": "011105",
        "Ecp_ClientId": "2210313121801733141;",
        "Ecp_session": "1;",
        "Ecp_session": "1;",
        "Hm_lvt_dcec09ba2227fd02c55623c1bb82776a": "1615609138;",
        "cnkiUserKey": "de6b2eae-6386-b38e-f5c5-de3c3296e3e0;",
        "Ecp_ClientIp": "211.71.28.244;",
        "_pk_ref": "%5B%22%22%2C%22%22%2C1616672790%2C%22https%3A%2F%2Fwww.cnki.net%2F%22%5D;",
        "_pk_ses": "*;",
        "LID": "WEEvREcwSlJHSldSdmVqMDh6a1dqZUtoQzJxUnVSM29KOFFxRU1tdFBMbz0=$9A4hF_YAuvQ5obgVAqNKPCYcEjKensW4IQMovwHtwkF4VYPoHbKxJw!!;",
        'Ecp_LoginStuts': '{"IsAutoLogin":false,"UserName":"K10093","ShowName":"%E4%B8%AD%E5%9B%BD%E4%BA%BA%E6%B0%91%E5%A4%A7%E5%AD%A6","UserType":"bk","BUserName":"","BShowName":"","BUserType":"","r":"o9n38w"};',
        "c_m_LinID": "LinID=WEEvREcwSlJHSldSdmVqMDh6a1dqZUtoQzJxUnVSM29KOFFxRU1tdFBMbz0=$9A4hF_YAuvQ5obgVAqNKPCYcEjKensW4IQMovwHtwkF4VYPoHbKxJw!!&ot={};",
        "c_m_expire": "{};",
        "_pk_id": "dadb0bc4-6998-4db9-9914-9c74c34f7187.1615609138.34.1616673960.1616672790.", 
        "Hm_lpvt_dcec09ba2227fd02c55623c1bb82776a": "1616673960"
    }

    headers_templete = {
        "Host": "nxgp.cnki.net",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36 Edg/89.0.774.50",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Cookie": "JSESSIONID=720A6D638F02AA6BF122A9DEC746616D; SID=011105; Ecp_ClientId=2210313121801733141; Ecp_session=1; Hm_lvt_dcec09ba2227fd02c55623c1bb82776a=1615609138; cnkiUserKey=de6b2eae-6386-b38e-f5c5-de3c3296e3e0; Ecp_ClientIp=211.71.28.244; _pk_ref=%5B%22%22%2C%22%22%2C1616586995%2C%22https%3A%2F%2Fwww.cnki.net%2F%22%5D; LID=WEEvREcwSlJHSldSdmVqMDh6a1dqZUdpSC8rdXk5MmtPcG9FczJ4Nll3cz0=$9A4hF_YAuvQ5obgVAqNKPCYcEjKensW4IQMovwHtwkF4VYPoHbKxJw!!; _pk_id=dadb0bc4-6998-4db9-9914-9c74c34f7187.1615609138.30.1616587061.1616586995.; Hm_lpvt_dcec09ba2227fd02c55623c1bb82776a=1616587061"
    }
    
    time_now = None

    @classmethod
    def get_updated_cookie(cls) -> str:
        cookie_updated = deepcopy(cls.Cookie_templete)
        cookie_updated["c_m_LinID"] = cookie_updated["c_m_LinID"].format(
            cls.time_now.strftime("%m/%d/%Y %H:%M:%S")
        )
        cookie_updated["c_m_expire"] = cookie_updated["c_m_expire"].format(
            cls.time_now.strftime("%Y-%m-%d %H:%M:%S")
        )
        Cookie = " ".join([item[0] + "=" + item[1] for item in cookie_updated.items()])
        return Cookie
    
    @classmethod
    def get_updated_headers(cls, Referer: str) -> dict:
        cls.time_now = datetime.now()
        Cookie = cls.get_updated_cookie()
        headers = deepcopy(cls.headers_templete)
        headers.update({
            "Referer": Referer,
            "Cookie": Cookie
        })
        return headers
