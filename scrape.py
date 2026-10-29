"""삼육대학교 산학협력단 '업무별 연락처' 표를 읽어 staff.js 로 저장한다.

전화번호는 게임에 필요 없으므로 저장하지 않는다 (이름·팀·직위·담당업무만).
사용법: python3 scrape.py
"""
import html
import json
import re
import urllib.request

URL = "https://www.syu.ac.kr/industry-academic-research/industry-academic-consortium/"


def text(fragment):
    return html.unescape(re.sub(r"<[^>]+>", "", fragment)).strip()


def scrape():
    page = urllib.request.urlopen(URL, timeout=15).read().decode("utf-8")
    staff = {}
    # <h3 class="md_s_tit ...">팀이름</h3> 바로 뒤(스크롤 div 안)의 <table> 하나씩
    pattern = r'<h3 class="md_s_tit[^"]*">([^<]*)</h3>\s*(?:<div[^>]*>\s*)?<table[^>]*>(.*?)</table>'
    for team, table in re.findall(pattern, page, re.S):
        team = text(team)
        for row in re.findall(r"<tr>(.*?)</tr>", table, re.S):
            cells = [text(c) for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row, re.S)]
            if len(cells) < 3 or cells[1] == "이름":
                continue
            title, name, duty = cells[0], cells[1], cells[2]
            if name in staff:  # 겸직: 처음 나온 팀을 소속으로 두고 업무만 덧붙인다
                staff[name]["duties"].append(duty)
                continue
            staff[name] = {"name": name, "team": team, "title": "" if title in "–-" else title, "duties": [duty]}
    return list(staff.values())


if __name__ == "__main__":
    people = scrape()
    with open("staff.js", "w", encoding="utf-8") as f:
        f.write("// scrape.py 가 생성함 — 출처: " + URL + "\n")
        f.write("window.STAFF = " + json.dumps(people, ensure_ascii=False, indent=2) + ";\n")
    print(f"{len(people)}명 저장 → staff.js")
