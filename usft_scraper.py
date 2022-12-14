import datetime
from lib2to3.pgen2.pgen import generate_grammar
import requests

from bs4 import BeautifulSoup

# 星座判定用のリスト
SIGN = {
  "capricorn": (119, "山羊"),
  "aquarius": (218, "水瓶"),
  "pisces": (320, "魚"),
  "aries": (419, "牡羊"),
  "taurus": (520, "牡牛"),
  "gemini": (621, "双子"),
  "cancer": (722, "蟹"),
  "leo": (822, "獅子"),
  "virgo": (922, "乙女"),
  "libra": (1023, "天秤"),
  "scorpio": (1122, "蠍"),
  "sagittarius": (1221, "射手")
}
BLOOD_TYPE = ["A", "B", "O", "AB"]

# VOGUE HOLOSCOPEのサイトから占い情報を取得する関数
def vogue_horoscpope_parser(birthday, verbose):
  result = 0
  category = ["Love luck", "Interparsonal luck", "Work and Study luck", "Money luck", "Health and Beauty luck", "Lucky item"]
  date = datetime.datetime.now().strftime("%Y/%-m/%-d/")
  sign = next(filter(lambda key: int(birthday.strftime("%m%-d")) <= SIGN[key][0], SIGN.keys()), next(iter(SIGN)))

  print(f"VOGUE HOROSCOPE: https://www.vogue.co.jp/horoscope（{SIGN[sign][1]}座の運勢）")

  for i, category in enumerate(category):
    if i == 0:
      url = f"https://www.vogue.co.jp/horoscope/daily/{date}{sign}"
    else:
      url = f"https://www.vogue.co.jp/horoscope/daily/{date}{sign}/{i + 1}"
    
    try:
      if i == 5:
        soup = BeautifulSoup(requests.get(url).content, "html.parser")
        item = soup.select("p.horoscope__single__message__star__item")[0].get_text().strip()
        if verbose:
          print(f"{' ' * 2}{category}:")
          print(f"{' ' * 4}name: {item}")
      else:
        soup = BeautifulSoup(requests.get(url).content, "html.parser")
        score = int(soup.select("div.horoscope__single__message__star strong")[0].get_text())
        if verbose:
          advice = soup.select("div.horoscope__single__message__text p")[0].get_text().strip()
          print(f"{' ' * 2}{category}:")
          print(f"{' ' * 4}star: {'★ ' * score}{'☆ ' * (5 - score)} ({score * 20}points)")
          print(f"{' ' * 4}advice: {advice_arrange(advice, 12)}")
        result += (score - 1) * 5
    except Exception:
      print("Error: failed to get fortune-telling information")
      return 0

  print(f"Success: The average score for VOGUE HOROSCOPE is {result} points\n")

  return [(result, [item])]

# Nippon TV Sukkirisuのサイトから占い情報を取得する関数
# (サイトの更新が朝の6時とか7時なので、実行する時間帯によっては前日の情報が引っ張られてくる)
def ntv_sukkirisu_parser(month, verbose):
  result = 0
  rank_category = ["超スッキりす", "スッキりす", "まあまあスッキりす", "ガッカりす"]
  url = "https://www.ntv.co.jp/sukkiri/sukkirisu/"

  print(f"Nippon TV Sukkirisu https://ntv.co.jp/sukkiri/sukkirisu（{month}月生まれの運勢）")

  try:
    soup = BeautifulSoup(requests.get(url).content, "html.parser")
    rank_list = [int(tag.get_text()) for tag in soup.select("div.result-list span")]
    rank = rank_list.index(month) + 1
    lucky_color = soup.select("div.row2 div")[rank - 1].get_text()
    if verbose:
      advice = soup.select("div.row2 p")[rank - 1].get_text()
      print(f"{' ' * 2}General luck:")
      print(f"{' ' * 4}rank: {rank}位（{rank_category[(rank + 3) // 5]}）")
      print(f"{' ' * 4}advice: {advice}")
      print(f"{' ' * 2}Lucky color:\n{' ' * 4}name: {lucky_color}")
    result = abs(rank - 12) * 8 + 12
  except Exception:
    print("Error: failed to get fortune-telling information")
    return 0

  print(f"Success: The average score for Nippon TV Sukkirisu is {result} points\n")

  return [(result, [lucky_color])]

# Uranai Squareのサイトから占い情報を取得する関数
def uranai_square_parser(bt_num, verbose):
  result = 0
  url = "https://uranai.d-square.co.jp/bloodtype_today.html"

  print(f"URANAI Square: https://uranai.d-square.co.jp（{BLOOD_TYPE[bt_num]}型の運勢）")

  try:
    soup = BeautifulSoup(requests.get(url).content, "html.parser")
    bt_link = soup.select(f"ul.bloodtype li:nth-of-type({bt_num + 1}) a")[0].get("href")
    soup = BeautifulSoup(requests.get(f"https://uranai.d-square.co.jp/{bt_link}").content, "html.parser")
    rank = int(soup.select("div.mainbloodtype img")[0].get("src")[-5])
    lucky_color = soup.select("div.green li:first-of-type p")[0].get_text().strip()
    lucky_word = soup.select("div.green li:last-of-type p")[0].get_text().strip()
    if verbose:
      general_luck = soup.select("div.green p")[0].get_text().strip()
      love_luck = soup.select("div.pink p")[0].get_text().strip()
      work_luck = soup.select("div.blue p")[0].get_text().strip()
      print(f"{' ' * 2}General luck:\n{' ' * 4}rank: {rank}位\n{' ' * 4}advice: {advice_arrange(general_luck, 12)}")
      print(f"{' ' * 2}Love luck:\n{' ' * 4}advice: {advice_arrange(love_luck, 12)}")
      print(f"{' ' * 2}Work luck:\n{' ' * 4}advice: {advice_arrange(work_luck, 12)}")
      print(f"{' ' * 2}Lucky color:\n{' ' * 4}name: {lucky_color}")
      print(f"{' ' * 2}Lucky word:\n{' ' * 4}name: {lucky_word}")
    result += abs(rank - 4) * 30
  except Exception:
    print("Error: failed to get fortune-telling information")
    return 0

  result += 10
  print(f"Success: The average score for URANAI Square is {result} points\n")

  return [(result, [lucky_color, lucky_word])]

# LINE Fortuneのサイトから占い情報を取得する関数
def line_fortune_parser(birthday, verbose):
  result = 0
  category = ["General luck", "Love luck", "Money luck", "Work luck"]
  sign = next(filter(lambda key: int(birthday.strftime("%m%-d")) <= SIGN[key][0], SIGN.keys()), next(iter(SIGN)))
  url = f"https://fortune.line.me/contents/horoscope/{sign}"

  print(f"LINE Fortune: https://fortune.line.me（{SIGN[sign][1]}座の運勢）")
  
  try:
    soup = BeautifulSoup(requests.get(url).content, "html.parser")
    for i, subsoup in enumerate(soup.select("div.lucky-detail-item_row__vsPgV")):
      score = 0
      for s in subsoup.select("i.star_starFilled__dlfMS"):
        score += 1 if "8.5" in s.get("style") else 2
      if verbose:
        advice =  subsoup.select("p.lucky-detail-item_description__LQecB")[0].get_text()
        print(f"{' ' * 2}{category[i]}:")
        print(f"{' ' * 4}star: {'★ ' * score}{'☆ ' * (10 - score)} ({score * 10}points)")
        print(f"{' ' * 4}advice: {advice_arrange(advice, 12)}")
      result += score * 10
    lucky_item = soup.select("span.lucky-overview_lucky__value__u2h81")[0].get_text()
    lucky_color = soup.select("span.lucky-overview_lucky__value__u2h81")[1].get_text()
    if verbose:
      print(f"{' ' * 2}Lucky item:\n{' ' * 4}name: {lucky_item}")
      print(f"{' ' * 2}Lucky color:\n{' ' * 4}name: {lucky_color}")
  except Exception:
    print("Error: failed to get fortune-telling information")
    return 0

  result = int(result / 4)
  print(f"Success: The average score for LINE Fortune is {result} points\n")

  return [(result, [lucky_item, lucky_color])]

# ESTART Uranaiのサイトから占い情報を取得する関数
def estart_uranai_parser(month, verbose):
  result = 0
  mapping = {'◎': 3, '◯': 2, '△': 1}
  url = f"https://start.jword.jp/uranai/birth_month/{month}"

  print(f"ESTART Uranai https://start.jword.jp/uranai（{month}月生まれの運勢）")

  try:
    soup = BeautifulSoup(requests.get(url).content, "html.parser")
    general_star = len([tag for tag in soup.select("ul.score li img") if tag.get("src") == "/_img/uranai/star_on.gif"])
    result += (general_star - 1) * 45 + 10
    lucky_stuff = [tag.get_text().split("： ")[-1] for tag in soup.select("div.lucky_stuff p")]
    icons = [tag.get_text() for tag in soup.select("table.table_weather p")]
    tarots = [tag.get("alt") for tag in soup.select("div#uranai_tarot_card img")]
    scores = [(mapping[icon] - 1) * 45 + 10 for icon in icons]
    result += sum(scores)
    if verbose:
      advice = soup.select("p.mb10")[0].get_text()
      print(f"{' ' * 2}General luck:")
      print(f"{' ' * 4}star: {'★ ' * general_star}{'☆ ' * (3 - general_star)} ({(general_star - 1) * 45 + 10}points)")
      print(f"{' ' * 4}advice: {advice_arrange(advice, 12)}")
      print(f"{' ' * 2}Love luck:")
      print(f"{' ' * 4}icon: {icons[0]} ({scores[0]}points)\n{' ' * 4}tarot: {tarots[0]}")
      print(f"{' ' * 2}Money luck:")
      print(f"{' ' * 4}icon: {icons[1]} ({scores[1]}points)\n{' ' * 4}tarot: {tarots[1]}")
      print(f"{' ' * 2}Work luck:")
      print(f"{' ' * 4}icon: {icons[2]} ({scores[2]}points)\n{' ' * 4}tarot: {tarots[2]}")
      print(f"{' ' * 2}Lucky item:\n{' ' * 4}name: {lucky_stuff[0]}")
      print(f"{' ' * 2}Lucky color:\n{' ' * 4}name: {lucky_stuff[1]}")
      print(f"{' ' * 2}Lucky number:\n{' ' * 4}name: {lucky_stuff[2]}")
  except Exception:
    print("Error: failed to get fortune-telling information")
    return 0

  result = int(result / 4)
  print(f"Success: The average score for ESTART Uranai is {result} points\n")

  return [(result, [lucky_stuff[0], lucky_stuff[1], f"数字の{lucky_stuff[2]}"])]

def advice_arrange(advice, space):
  return f"\n{' ' * space}".join(filter(lambda s: len(s) != 0, advice.split("。")))