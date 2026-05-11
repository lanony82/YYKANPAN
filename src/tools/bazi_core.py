#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
八字核心计算库
包含：农历转换、二十四节气、八字计算
"""

from datetime import datetime

# =========================================================
# 农历数据（1900-2100年）
# =========================================================

LUNAR_DATA = [
    0x04bd8, 0x04ae0, 0x0a570, 0x054d5, 0x0d260, 0x0d950, 0x16554, 0x056a0, 0x09ad0, 0x055d2,
    0x04ae0, 0x0a5b6, 0x0a4d0, 0x0d250, 0x1d255, 0x0b540, 0x0d6a0, 0x0ada2, 0x095b0, 0x14977,
    0x04970, 0x0a4b0, 0x0b4b5, 0x06a50, 0x06d40, 0x1ab54, 0x02b60, 0x09570, 0x052f2, 0x04970,
    0x06566, 0x0d4a0, 0x0ea50, 0x06e95, 0x05ad0, 0x02b60, 0x186e3, 0x092e0, 0x1c8d7, 0x0c950,
    0x0d4a0, 0x1d8a6, 0x0b550, 0x056a0, 0x1a5b4, 0x025d0, 0x092d0, 0x0d2b2, 0x0a950, 0x0b557,
    0x06ca0, 0x0b550, 0x15355, 0x04da0, 0x0a5b0, 0x14573, 0x052b0, 0x0a9a8, 0x0e950, 0x06aa0,
    0x0aea6, 0x0ab50, 0x04b60, 0x0aae4, 0x0a570, 0x05260, 0x0f263, 0x0d950, 0x05b57, 0x056a0,
    0x096d0, 0x04dd5, 0x04ad0, 0x0a4d0, 0x0d4d4, 0x0d250, 0x0d558, 0x0b540, 0x0b6a0, 0x195a6,
    0x095b0, 0x049b0, 0x0a974, 0x0a4b0, 0x0b27a, 0x06a50, 0x06d40, 0x0af46, 0x0ab60, 0x09570,
    0x04af5, 0x04970, 0x064b0, 0x074a3, 0x0ea50, 0x06b58, 0x055c0, 0x0ab60, 0x096d5, 0x092e0,
    0x0c960, 0x0d954, 0x0d4a0, 0x0da50, 0x07552, 0x056a0, 0x0abb7, 0x025d0, 0x092d0, 0x0cab5,
    0x0a950, 0x0b4a0, 0x0baa4, 0x0ad50, 0x055d9, 0x04ba0, 0x0a5b0, 0x15176, 0x052b0, 0x0a930,
    0x07954, 0x06aa0, 0x0ad50, 0x05b52, 0x04b60, 0x0a6e6, 0x0a4e0, 0x0d260, 0x0ea65, 0x0d530,
    0x05aa0, 0x076a3, 0x096d0, 0x04bd7, 0x04ad0, 0x0a4d0, 0x1d0b6, 0x0d250, 0x0d520, 0x0dd45,
    0x0b5a0, 0x056d0, 0x055b2, 0x049b0, 0x0a577, 0x0a4b0, 0x0aa50, 0x1b255, 0x06d20, 0x0ada0,
    0x14b63, 0x09370, 0x049f8, 0x04970, 0x064b0, 0x168a6, 0x0ea50, 0x06b20, 0x1a6c4, 0x0aae0,
    0x0a2e0, 0x0d2e3, 0x0c960, 0x0d557, 0x0d4a0, 0x0da50, 0x05d55, 0x056a0, 0x0a6d0, 0x055d4,
    0x052d0, 0x0a9b8, 0x0a950, 0x0b4a0, 0x0b6a6, 0x0ad50, 0x055a0, 0x0aba4, 0x0a5b0, 0x052b0,
    0x0b273, 0x06930, 0x07337, 0x06aa0, 0x0ad50, 0x14b55, 0x04b60, 0x0a570, 0x054e4, 0x0d160,
    0x0e968, 0x0d520, 0x0daa0, 0x16aa6, 0x056d0, 0x04ae0, 0x0a9d4, 0x0a2d0, 0x0d150, 0x0f252,
    0x0d520, 0x0dd40, 0x0b5a0, 0x056d0
]

GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
MONTH_NAMES = ['正月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '十一月', '十二月']
DAY_NAMES = [
    '初一', '初二', '初三', '初四', '初五', '初六', '初七', '初八', '初九', '初十',
    '十一', '十二', '十三', '十四', '十五', '十六', '十七', '十八', '十九', '二十',
    '廿一', '廿二', '廿三', '廿四', '廿五', '廿六', '廿七', '廿八', '廿九', '三十'
]


# =========================================================
# 农历计算
# =========================================================

def get_lunar_year_days(year):
    info = LUNAR_DATA[year - 1900]
    leap_month = info & 0xf
    leap_days = 30 if (info >> 16) & 0x1 else 29 if leap_month > 0 else 0
    normal_days = 0
    for i in range(12):
        normal_days += 30 if (info & (1 << (15 - i))) else 29
    return normal_days + leap_days


def get_leap_month(year):
    info = LUNAR_DATA[year - 1900]
    return info & 0xf


def get_lunar_month_days(year, month, leap_month, is_leap):
    info = LUNAR_DATA[year - 1900]
    if month == leap_month and is_leap:
        return 30 if (info >> 16) & 0x1 else 29
    month_bit = 1 << (16 - month)
    return 30 if (info & month_bit) else 29


def get_lunar_date(date):
    base_date = datetime(1900, 1, 31)
    days_diff = (date - base_date).days
    lunar_year = 1900
    while lunar_year < 2100:
        year_days = get_lunar_year_days(lunar_year)
        if days_diff < year_days:
            break
        days_diff -= year_days
        lunar_year += 1
    lunar_month = 1
    leap_month = get_leap_month(lunar_year)
    is_leap = False
    while lunar_month <= 12:
        month_days = get_lunar_month_days(lunar_year, lunar_month, leap_month, is_leap)
        if days_diff < month_days:
            break
        days_diff -= month_days
        if leap_month > 0 and lunar_month == leap_month and not is_leap:
            is_leap = True
        else:
            lunar_month += 1
            is_leap = False
    lunar_day = days_diff + 1
    gan_idx = (lunar_year - 4) % 10
    zhi_idx = (lunar_year - 4) % 12
    year_ganzhi = f"{GAN[gan_idx]}{ZHI[zhi_idx]}"
    return {
        'year_ganzhi': year_ganzhi,
        'month': lunar_month,
        'day': lunar_day,
        'month_name': MONTH_NAMES[lunar_month - 1],
        'day_name': DAY_NAMES[lunar_day - 1],
        'is_leap': is_leap
    }


def get_lunar_date_string(date):
    lunar = get_lunar_date(date)
    return f"{lunar['year_ganzhi']}年 {lunar['month_name']} {lunar['day_name']}"


# =========================================================
# 二十四节气计算（寿星万年历近似算法）
# =========================================================

TERM_ORDER = [
    ("小寒", 1), ("大寒", 1), ("立春", 2), ("雨水", 2),
    ("惊蛰", 3), ("春分", 3), ("清明", 4), ("谷雨", 4),
    ("立夏", 5), ("小满", 5), ("芒种", 6), ("夏至", 6),
    ("小暑", 7), ("大暑", 7), ("立秋", 8), ("处暑", 8),
    ("白露", 9), ("秋分", 9), ("寒露", 10), ("霜降", 10),
    ("立冬", 11), ("小雪", 11), ("大雪", 12), ("冬至", 12),
]

_C21 = {
    "小寒": 5.4055, "大寒": 20.12, "立春": 3.87, "雨水": 18.73,
    "惊蛰": 5.63, "春分": 20.646, "清明": 4.81, "谷雨": 20.1,
    "立夏": 5.52, "小满": 21.04, "芒种": 5.678, "夏至": 21.37,
    "小暑": 7.108, "大暑": 22.83, "立秋": 7.5, "处暑": 23.13,
    "白露": 7.646, "秋分": 23.042, "寒露": 8.318, "霜降": 23.438,
    "立冬": 7.438, "小雪": 22.36, "大雪": 7.18, "冬至": 21.94,
}

_C20 = {
    "小寒": 6.11, "大寒": 20.84, "立春": 4.6295, "雨水": 19.4599,
    "惊蛰": 6.3826, "春分": 21.4155, "清明": 5.59, "谷雨": 20.888,
    "立夏": 6.318, "小满": 21.86, "芒种": 6.5, "夏至": 22.2,
    "小暑": 7.928, "大暑": 23.65, "立秋": 8.35, "处暑": 23.95,
    "白露": 8.44, "秋分": 23.822, "寒露": 9.098, "霜降": 24.218,
    "立冬": 8.218, "小雪": 23.08, "大雪": 7.9, "冬至": 22.6,
}

SEASONS = {
    "春季": ["立春", "雨水", "惊蛰", "春分", "清明", "谷雨"],
    "夏季": ["立夏", "小满", "芒种", "夏至", "小暑", "大暑"],
    "秋季": ["立秋", "处暑", "白露", "秋分", "寒露", "霜降"],
    "冬季": ["立冬", "小雪", "大雪", "冬至", "小寒", "大寒"],
}

TERM_SEASON = {}
for _season, _terms in SEASONS.items():
    for _term in _terms:
        TERM_SEASON[_term] = _season


def calc_solar_term_day(year, term_name):
    y = year % 100
    c = _C21[term_name] if year >= 2000 else _C20[term_name]
    return int(y * 0.2422 + c) - int(y / 4)


def get_solar_terms_for_year(year):
    result = []
    for name, month in TERM_ORDER:
        day = calc_solar_term_day(year, name)
        result.append((name, datetime(year, month, day)))
    return result


def get_solar_term_info(date):
    dt = datetime(date.year, date.month, date.day)
    terms = (get_solar_terms_for_year(date.year - 1)
             + get_solar_terms_for_year(date.year)
             + get_solar_terms_for_year(date.year + 1))
    prev_term = None
    today_term = None
    next_term = None
    for name, term_date in terms:
        diff = (term_date - dt).days
        if diff == 0:
            today_term = (name, TERM_SEASON.get(name, ""))
        elif diff < 0:
            days_ago = -diff
            if prev_term is None or days_ago < prev_term[2]:
                prev_term = (name, TERM_SEASON.get(name, ""), days_ago)
        elif diff > 0:
            if next_term is None or diff < next_term[2]:
                next_term = (name, TERM_SEASON.get(name, ""), diff)
    return {"prev": prev_term, "today": today_term, "next": next_term}


# =========================================================
# 八字计算
# =========================================================

class BaziCalculator:
    GAN = GAN
    ZHI = ZHI

    SHI_CHEN = {
        '子': '23:00-01:00', '丑': '01:00-03:00', '寅': '03:00-05:00', '卯': '05:00-07:00',
        '辰': '07:00-09:00', '巳': '09:00-11:00', '午': '11:00-13:00', '未': '13:00-15:00',
        '申': '15:00-17:00', '酉': '17:00-19:00', '戌': '19:00-21:00', '亥': '21:00-23:00',
    }

    def __init__(self, dt):
        self.dt = dt

    def get_solar_term_index(self):
        year = self.dt.year
        dt = datetime(year, self.dt.month, self.dt.day)
        jie = [
            ("小寒", 1, 11), ("立春", 2, 0), ("惊蛰", 3, 1), ("清明", 4, 2),
            ("立夏", 5, 3), ("芒种", 6, 4), ("小暑", 7, 5), ("立秋", 8, 6),
            ("白露", 9, 7), ("寒露", 10, 8), ("立冬", 11, 9), ("大雪", 12, 10),
        ]
        result = 10
        for name, month, idx in jie:
            day = calc_solar_term_day(year, name)
            if dt >= datetime(year, month, day):
                result = idx
        return result

    def calc_year_gan(self):
        year = self.dt.year
        lichun_day = calc_solar_term_day(year, "立春")
        if self.dt.month < 2 or (self.dt.month == 2 and self.dt.day < lichun_day):
            year -= 1
        return GAN[(year - 4) % 10]

    def calc_year_zhi(self):
        year = self.dt.year
        lichun_day = calc_solar_term_day(year, "立春")
        if self.dt.month < 2 or (self.dt.month == 2 and self.dt.day < lichun_day):
            year -= 1
        return ZHI[(year - 4) % 12]

    def calc_month_gan(self, year_gan):
        start = {'甲':'丙','己':'丙','乙':'戊','庚':'戊','丙':'庚','辛':'庚','丁':'壬','壬':'壬','戊':'甲','癸':'甲'}
        month_idx = self.get_solar_term_index()
        s = start.get(year_gan, '丙')
        idx = (GAN.index(s) + month_idx) % 10
        return GAN[idx]

    def calc_month_zhi(self):
        return ['寅','卯','辰','巳','午','未','申','酉','戌','亥','子','丑'][self.get_solar_term_index()]

    def calc_day_gan_zhi(self):
        y, m, d = self.dt.year, self.dt.month, self.dt.day
        if y >= 2000:
            base = (y % 100 + 7) * 5 + 15 + (y % 100 + 19) // 4
        else:
            base = (y % 100 + 3) * 5 + 55 + (y % 100 - 1) // 4
        base %= 60
        is_leap = (y % 4 == 0 and y % 100 != 0) or (y % 400 == 0)
        month_days = [31, 29 if is_leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        day_of_year = sum(month_days[:m-1]) + d
        total = (base + day_of_year) % 60
        if total == 0:
            total = 60
        return (GAN[(total - 1) % 10], ZHI[(total - 1) % 12])

    def get_hour_zhi(self):
        hour = self.dt.hour
        if hour == 23:
            hour = -1
        return ZHI[((hour + 1) // 2) % 12]

    def calc_hour_gan(self, day_gan, hour_zhi):
        start = {'甲':'甲','己':'甲','乙':'丙','庚':'丙','丙':'戊','辛':'戊','丁':'庚','壬':'庚','戊':'壬','癸':'壬'}
        s = start.get(day_gan, '甲')
        idx = (GAN.index(s) + ZHI.index(hour_zhi)) % 10
        return GAN[idx]

    def get_nayin(self, gan, zhi):
        table = {
            ('甲','子'):'海中金',('乙','丑'):'海中金',('丙','寅'):'炉中火',('丁','卯'):'炉中火',
            ('戊','辰'):'大林木',('己','巳'):'大林木',('庚','午'):'路旁土',('辛','未'):'路旁土',
            ('壬','申'):'剑锋金',('癸','酉'):'剑锋金',('甲','戌'):'山头火',('乙','亥'):'山头火',
            ('丙','子'):'涧下水',('丁','丑'):'涧下水',('戊','寅'):'城头土',('己','卯'):'城头土',
            ('庚','辰'):'白蜡金',('辛','巳'):'白蜡金',('壬','午'):'杨柳木',('癸','未'):'杨柳木',
            ('甲','申'):'泉中水',('乙','酉'):'泉中水',('丙','戌'):'屋上土',('丁','亥'):'屋上土',
            ('戊','子'):'霹雳火',('己','丑'):'霹雳火',('庚','寅'):'松柏木',('辛','卯'):'松柏木',
            ('壬','辰'):'长流水',('癸','巳'):'长流水',('甲','午'):'沙中金',('乙','未'):'沙中金',
            ('丙','申'):'山下火',('丁','酉'):'山下火',('戊','戌'):'平地木',('己','亥'):'平地木',
            ('庚','子'):'壁上土',('辛','丑'):'壁上土',('壬','寅'):'金箔金',('癸','卯'):'金箔金',
            ('甲','辰'):'覆灯火',('乙','巳'):'覆灯火',('丙','午'):'天河水',('丁','未'):'天河水',
            ('戊','申'):'大驿土',('己','酉'):'大驿土',('庚','戌'):'钗钏金',('辛','亥'):'钗钏金',
            ('壬','子'):'桑柘木',('癸','丑'):'桑柘木',('甲','寅'):'大溪水',('乙','卯'):'大溪水',
            ('丙','辰'):'沙中土',('丁','巳'):'沙中土',('戊','午'):'天上火',('己','未'):'天上火',
            ('庚','申'):'石榴木',('辛','酉'):'石榴木',('壬','戌'):'大海水',('癸','亥'):'大海水',
        }
        return table.get((gan, zhi), '未知')


def get_bazi_data(date):
    calc = BaziCalculator(date.replace(hour=12))
    year_gan = calc.calc_year_gan()
    year_zhi = calc.calc_year_zhi()
    month_gan = calc.calc_month_gan(year_gan)
    month_zhi = calc.calc_month_zhi()
    day_gan, day_zhi = calc.calc_day_gan_zhi()
    year_str = f"{year_gan}{year_zhi}"
    month_str = f"{month_gan}{month_zhi}"
    day_str = f"{day_gan}{day_zhi}"
    hours = []
    for zhi in ZHI:
        hour_gan = calc.calc_hour_gan(day_gan, zhi)
        hours.append({
            'zhi': zhi,
            'time': BaziCalculator.SHI_CHEN[zhi],
            'hour': f"{hour_gan}{zhi}",
            'nayin': calc.get_nayin(hour_gan, zhi)
        })
    return year_str, month_str, day_str, hours


# =========================================================
# 五运六气 (Wǔyùn Liùqì — Five Movements & Six Qi)
#
# A classical Chinese system mapping each year's Heavenly Stem
# and Earthly Branch to climatic/energetic patterns:
#   • 五运 (Five Movements): the year's dominant element (木火土金水)
#     derived from the Heavenly Stem, marked 太过 (excess, yang stem)
#     or 不及 (deficient, yin stem).
#   • 六气 (Six Qi): six climatic forces that govern the year in
#     two halves — 司天 (Governing Heaven, 1st half) and
#     在泉 (Governing Earth, 2nd half) — derived from the Earthly
#     Branch.  The year is further divided into six ~60-day periods
#     (初之气 through 终之气), each with a fixed "host qi" (主气)
#     and a rotating "guest qi" (客气) that modifies the climate.
# =========================================================

# The six qi in their standard cycle order
SIX_QI = [
    '厥阴风木',   # 0 — wind / wood
    '少阴君火',   # 1 — sovereign fire
    '太阴湿土',   # 2 — dampness / earth
    '少阳相火',   # 3 — ministerial fire
    '阳明燥金',   # 4 — dryness / metal
    '太阳寒水',   # 5 — cold / water
]

QI_PERIOD_NAMES = ['初之气', '二之气', '三之气', '四之气', '五之气', '终之气']

# Solar terms that mark the START of each qi period
_QI_BOUNDARY_TERMS = ['大寒', '春分', '小满', '大暑', '秋分', '小雪']

# Heavenly Stem → (element, excess/deficient)
_TIANGAN_WUYUN = {
    '甲': ('土', '太过'), '己': ('土', '不及'),
    '乙': ('金', '不及'), '庚': ('金', '太过'),
    '丙': ('水', '太过'), '辛': ('水', '不及'),
    '丁': ('木', '不及'), '壬': ('木', '太过'),
    '戊': ('火', '太过'), '癸': ('火', '不及'),
}

# Earthly Branch → index into SIX_QI for 司天
_DIZHI_SITIAN = {
    '子': 1, '午': 1,
    '丑': 2, '未': 2,
    '寅': 3, '申': 3,
    '卯': 4, '酉': 4,
    '辰': 5, '戌': 5,
    '巳': 0, '亥': 0,
}

# Annual-movement health tips
_WUYUN_TIPS = {
    '木运太过': '风气偏盛，肝木旺，宜疏肝理气、健脾',
    '木运不及': '肝气弱，燥金乘之，宜养肝柔筋',
    '火运太过': '暑热偏盛，心火旺，宜清心安神',
    '火运不及': '心阳弱，寒水乘之，宜温养心阳',
    '土运太过': '湿气偏盛，脾湿重，宜健脾化湿',
    '土运不及': '脾气弱，风木乘之，宜益气健脾',
    '金运太过': '燥气偏盛，肺燥重，宜润肺生津',
    '金运不及': '肺气弱，火热乘之，宜养阴清肺',
    '水运太过': '寒气偏盛，肾寒重，宜温阳散寒',
    '水运不及': '肾气弱，湿土乘之，宜补肾固本',
}

# Guest-qi climate effect (brief description)
_GUEST_QI_EFFECT = {
    '厥阴风木': '客风加持，多风',
    '少阴君火': '客火加温，偏热',
    '太阴湿土': '客湿覆之，偏湿',
    '少阳相火': '客火助热，暑气较重',
    '阳明燥金': '客燥敛降，偏干燥',
    '太阳寒水': '客寒临之，偏寒凉',
}

# Host-qi (主气) seasonal climate
_HOST_QI_CLIMATE = {
    '厥阴风木': '风气主令，乍暖还寒',
    '少阴君火': '君火当令，天气渐热',
    '太阴湿土': '湿气主令，多雨潮湿',
    '少阳相火': '相火主令，暑热炎盛',
    '阳明燥金': '燥金主令，秋高气爽',
    '太阳寒水': '寒水主令，天寒地冻',
}

# Health tips per qi period (养生提示)
_HEALTH_TIPS = {
    '厥阴风木': '🌿 防风护肝，忌熬夜动怒，多吃绿叶蔬菜',
    '少阴君火': '❤️ 养心安神，午休片刻，少食辛辣，多饮花茶',
    '太阴湿土': '🍵 健脾祛湿，少食生冷瓜果，适当运动排汗',
    '少阳相火': '🔥 清热降暑，多食苦瓜绿豆，避免剧烈运动',
    '阳明燥金': '🍐 润肺防燥，多食梨藕银耳，注意皮肤保湿',
    '太阳寒水': '🧣 温肾散寒，早睡晚起，泡脚驱寒，忌贪凉',
}

# Trading sector hints mapped to five elements (仅供娱乐参考)
_TRADING_TIPS = {
    '木运太过': '📈 木旺利农林、家具、造纸板块；木克土，地产建材或承压',
    '木运不及': '📉 木弱林业偏淡；金来乘木，关注有色金属、军工反弹',
    '火运太过': '📈 火旺利光伏、新能源、电子科技；火克金，贵金属或承压',
    '火运不及': '📉 科技板块偏弱；水来乘火，关注水利、环保、航运',
    '土运太过': '📈 土旺利地产、建材、农业板块；土克水，水务航运或承压',
    '土运不及': '📉 地产建材偏淡；木来乘土，关注农林、家具板块机会',
    '金运太过': '📈 金旺利有色金属、军工、银行；金克木，农林纸业或承压',
    '金运不及': '📉 金属板块偏弱；火来乘金，关注光伏、新能源、电力',
    '水运太过': '📈 水旺利水务、航运、酿酒板块；水克火，新能源科技或承压',
    '水运不及': '📉 航运水务偏淡；土来乘水，关注地产基建、建材板块',
}


def calc_wuyun_liuqi(dt):
    """
    Calculate 五运六气 for the given datetime.

    Returns a dict with:
      sui_yun    — e.g. "水运太过"
      sitian     — 司天 qi name
      zaiquan    — 在泉 qi name
      period_name — e.g. "二之气"
      host_qi    — 主气 for this period
      guest_qi   — 客气 for this period
      comment    — human-readable summary
    """
    calc = BaziCalculator(dt)
    year_gan = calc.calc_year_gan()
    year_zhi = calc.calc_year_zhi()

    # ── 岁运 (annual movement) ──
    wuxing, excess = _TIANGAN_WUYUN[year_gan]
    sui_yun = f"{wuxing}运{excess}"

    # ── 司天 & 在泉 ──
    sitian_idx = _DIZHI_SITIAN[year_zhi]
    zaiquan_idx = (sitian_idx + 3) % 6
    sitian = SIX_QI[sitian_idx]
    zaiquan = SIX_QI[zaiquan_idx]

    # ── current qi period (based on solar-term boundaries) ──
    terms = (get_solar_terms_for_year(dt.year - 1)
             + get_solar_terms_for_year(dt.year))
    boundary_set = set(_QI_BOUNDARY_TERMS)
    boundaries = sorted(
        [(n, d) for n, d in terms if n in boundary_set],
        key=lambda x: x[1],
    )
    today = datetime(dt.year, dt.month, dt.day)
    current_period = 5  # default: 终之气 (before first 大寒)
    for name, term_dt in boundaries:
        if today >= datetime(term_dt.year, term_dt.month, term_dt.day):
            current_period = _QI_BOUNDARY_TERMS.index(name)
    period_name = QI_PERIOD_NAMES[current_period]

    # ── 主气 (host qi) — fixed cycle every year ──
    host_qi = SIX_QI[current_period]

    # ── 客气 (guest qi) — rotates with 司天 at step 3 (index 2) ──
    guest_qi_idx = (sitian_idx + current_period - 2) % 6
    guest_qi = SIX_QI[guest_qi_idx]

    # ── human-readable comment ──
    annual_tip = _WUYUN_TIPS.get(sui_yun, '')
    host_desc = _HOST_QI_CLIMATE.get(host_qi, '')
    guest_desc = _GUEST_QI_EFFECT.get(guest_qi, '')
    comment = (
        f"{year_gan}{year_zhi}年{sui_yun}，{annual_tip}。"
        f"当前{period_name}，{host_desc}；{guest_desc}。"
    )

    health_tip = _HEALTH_TIPS.get(host_qi, '')
    trading_tip = _TRADING_TIPS.get(sui_yun, '')

    return {
        'sui_yun': sui_yun,
        'sitian': sitian,
        'zaiquan': zaiquan,
        'period_name': period_name,
        'period_index': current_period + 1,
        'host_qi': host_qi,
        'guest_qi': guest_qi,
        'comment': comment,
        'health_tip': health_tip,
        'trading_tip': trading_tip,
    }
