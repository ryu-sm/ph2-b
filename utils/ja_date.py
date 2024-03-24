from datetime import date, datetime


epochYear = {
    1942: "昭和17",
    1943: "昭和18",
    1944: "昭和19",
    1945: "昭和20",
    1946: "昭和21",
    1947: "昭和22",
    1948: "昭和23",
    1949: "昭和24",
    1950: "昭和25",
    1951: "昭和26",
    1952: "昭和27",
    1953: "昭和28",
    1954: "昭和29",
    1955: "昭和30",
    1956: "昭和31",
    1957: "昭和32",
    1958: "昭和33",
    1959: "昭和34",
    1960: "昭和35",
    1961: "昭和36",
    1962: "昭和37",
    1963: "昭和38",
    1964: "昭和39",
    1965: "昭和40",
    1966: "昭和41",
    1967: "昭和42",
    1968: "昭和43",
    1969: "昭和44",
    1970: "昭和45",
    1971: "昭和46",
    1972: "昭和47",
    1973: "昭和48",
    1974: "昭和49",
    1975: "昭和50",
    1976: "昭和51",
    1977: "昭和52",
    1978: "昭和53",
    1979: "昭和54",
    1980: "昭和55",
    1981: "昭和56",
    1982: "昭和57",
    1983: "昭和58",
    1984: "昭和59",
    1985: "昭和60",
    1986: "昭和61",
    1987: "昭和62",
    1988: "昭和63",
    1989: "平成元",
    1990: "平成2",
    1991: "平成3",
    1992: "平成4",
    1993: "平成5",
    1994: "平成6",
    1995: "平成7",
    1996: "平成8",
    1997: "平成9",
    1998: "平成10",
    1999: "平成11",
    2000: "平成12",
    2001: "平成13",
    2002: "平成14",
    2003: "平成15",
    2004: "平成16",
    2005: "平成17",
    2006: "平成18",
    2007: "平成19",
    2008: "平成20",
    2009: "平成21",
    2010: "平成22",
    2011: "平成23",
    2012: "平成24",
    2013: "平成25",
    2014: "平成26",
    2015: "平成27",
    2016: "平成28",
    2017: "平成29",
    2018: "平成30",
    2019: "令和1",
    2020: "令和2",
    2021: "令和3",
    2022: "令和4",
    2023: "令和5",
    2024: "令和6",
    2025: "令和7",
    2026: "令和8",
    2027: "令和9",
    2028: "令和10",
    2029: "令和11",
    2030: "令和12",
    2031: "令和13",
    2032: "令和14",
    2033: "令和15",
}


def gen_ja_apply_datetime():
    now_datetime = datetime.now()
    year = now_datetime.year
    ja_year = epochYear.get(year)
    if ja_year:
        return now_datetime.strftime(f"%Y（{ja_year}）年%m月%d日 %H:%M")
    else:
        return now_datetime.strftime(f"%Y年%m月%d日 %H:%M")


def format_js_date_ymd(date_str):
    if not date_str:
        return ""
    now_datetime = datetime.strptime(date_str, "%Y/%m/%d")
    year = now_datetime.year
    ja_year = epochYear.get(year)
    if ja_year:
        return now_datetime.strftime(f"%Y（{ja_year}）年%m月%d日")
    else:
        return now_datetime.strftime(f"%Y年%m月%d日")


def format_js_date_ym(date_str):
    if not date_str:
        return ""
    now_datetime = datetime.strptime(date_str, "%Y/%m")
    year = now_datetime.year
    ja_year = epochYear.get(year)
    if ja_year:
        return now_datetime.strftime(f"%Y（{ja_year}）年%m月")
    else:
        return now_datetime.strftime(f"%Y年%m月")
