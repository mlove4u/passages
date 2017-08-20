# -*- coding: utf-8 -*-
import os
import re
import linecache
import unicodedata

BookList = {
    "创": "创世记",
    "出": "出埃及记",
    "利": "利未记",
    "民": "民数记",
    "申": "申命记",
    "书": "约书亚记",
    "士": "士师记",
    "得": "路得记",
    "撒上": "撒母耳记上",
    "撒下": "撒母耳记下",
    "王上": "列王纪上",
    "王下": "列王纪下",
    "代上": "历代志上",
    "代下": "历代志下",
    "拉": "以斯拉记",
    "尼": "尼希米记",
    "斯": "以斯帖记",
    "伯": "约伯记",
    "诗": "诗篇",
    "箴": "箴言",
    "传": "传道书",
    "歌": "雅歌",
    "赛": "以赛亚书",
    "耶": "耶利米书",
    "哀": "耶利米哀歌",
    "结": "以西结书",
    "但": "但以理书",
    "何": "何西阿书",
    "珥": "约珥书",
    "摩": "阿摩司书",
    "俄": "俄巴底亚书",
    "拿": "约拿书",
    "弥": "弥迦书",
    "鸿": "那鸿书",
    "哈": "哈巴谷书",
    "番": "西番雅书",
    "该": "哈该书",
    "亚": "撒迦利亚书",
    "玛": "玛拉基书",
    "太": "马太福音",
    "可": "马可福音",
    "路": "路加福音",
    "约": "约翰福音",
    "徒": "使徒行传",
    "罗": "罗马书",
    "林前": "哥林多前书",
    "林后": "哥林多后书",
    "加": "加拉太书",
    "弗": "以弗所书",
    "腓": "腓利比书",
    "西": "歌罗西书",
    "帖前": "帖撒罗尼迦前书",
    "帖后": "帖撒罗尼迦后书",
    "提前": "提摩太前书",
    "提后": "提摩太后书",
    "多": "提多书",
    "门": "腓利门书",
    "来": "希伯来书",
    "雅": "雅各书",
    "彼前": "彼得前书",
    "彼后": "彼得后书",
    "约一": "约翰一书",
    "约二": "约翰二书",
    "约三": "约翰三书",
    "犹": "犹大书",
    "启": "启示录"
}

################################################################
def hyphen(v):
    if v.find("-") == -1:
        # IDEA:
        return v.split(",")
    else:
        a, z = int(v.split("-")[0]), int(v.split("-")[1])
        return range(a, z + 1)
################################################################
def get_passages(input):

    input = unicodedata.normalize('NFKC', input).replace(" ", "")
    if not input:
        print("经文出处不能为空")
        return

    input = input.replace("\n", ";").split(";")
    output = []
    for s in input:
        if not s:
            continue
        if not re.sub(r'\D+$', '', s): # 去掉末尾所有非数字的字符
            output.append({"Origin": s, "BookName": "", "CV": "", "Error": ">>>>>格式错误：没有章节数字"})
            continue
        a = re.search(r'\d', s).start()  # 第一个数字出现的位置。此前是书卷，此后是章节
        BookName = s[:a]
        CV = s[a:]  # 章节
        output.append({"Origin": s, "BookName": BookName, "CV": CV,"contents": "", "Error": False})


    for i, p in enumerate(output):
        if p["Error"]:
            continue

        if p["BookName"] == "":
            if i == 0:
                p["Error"] = ">>>>>第一个经文不能没有书卷名"
                continue
            else:
                p["BookName"] = output[i - 1]["BookName"]
                if not p["BookName"]:
                    p["Error"] = ">>>>>前一个经文没有书卷名"
                    continue

        if re.sub(r'[\d,-:]', "", p["CV"]):
            p["Error"] = ">>>>>【章节】里不能含有【数字，逗号，连接符，冒号】以外的字符"
            continue

        for k, v in BookList.items():
            if p["BookName"] in [k, v]:
                p["BookName"] = v
                break
        else:
            p["Error"] = ">>>>>找不到该书卷，请检查书卷名字是否正确"
            continue

        p["contents"] = []
        bookPath = "bible/" + p["BookName"] + ".txt"

        if ":" in p["CV"]:  # 输出章和节
            colonN = p["CV"].count(":")  # colon Num 冒号个数
            # 输出同一章内的经文
            if colonN == 1:
                C, V = p["CV"].split(":")[0], p["CV"].split(":")[1]
                Chapter = linecache.getline(bookPath, int(C))
                linecache.clearcache()
                begin = len(C) + 2  # 每段的开头都以“第＊章”开头，跳过这几个字符
                VerseArr = V.split(",")
                for x in VerseArr:
                    for y in hyphen(x):
                        p_start = Chapter.find(str(y), begin)
                        p_end = Chapter.find(str(int(y) + 1), begin)
                        verse = Chapter[p_start:p_end]
                        p["contents"].append(verse)
            # 输出跨章的经文
            elif colonN == 2:
                if p["CV"].find(",") != -1:
                    p["Error"] = ">>>>>不同章的经文不能放在同一行"
                elif p["CV"].find("-") != -1:
                    VerseArr = p["CV"].split("-")
                    C1, V1 = VerseArr[0].split(":")[0], VerseArr[0].split(":")[1]  # 连接符前的章、节
                    begin1 = len(C1) + 2
                    C2, V2 = VerseArr[1].split(":")[0], VerseArr[1].split(":")[1]  # 连接符后的章、节
                    begin2 = len(C2) + 2
                    for x in range(int(C1), int(C2) + 1):
                        Chapter = linecache.getline(bookPath, x)
                        linecache.clearcache()
                        if x == int(C1):
                            p_start = Chapter.find(V1, begin1)
                            verse = Chapter[p_start:-1]
                            p["contents"].append("第" + C1 + "章" + verse + "\n")
                        elif x == int(C2):
                            p_end = Chapter.find(str(int(V2) + 1),begin2)
                            verse = Chapter[0:p_end]
                            p["contents"].append(verse)
                        else:
                            p["contents"].append(Chapter)
            # 其他错误
            else:
                p["Error"] = ">>>>>【跨章】出处格式错误"
                continue

        else:  # 没有冒号（输出整章）
            ChapterArr = p["CV"].split(",")
            for x in ChapterArr:
                for y in hyphen(x):
                    Chapter = linecache.getline(bookPath, int(y))
                    p["contents"].append(Chapter)
                    linecache.clearcache()

    return output


################################################################
if __name__ == "__main__":
    with open("bible_input.txt", "r", encoding="utf-8") as inputfile:
        source = inputfile.read()
    with open("bible_output.txt", "w", encoding="utf-8") as outputfile:
        result = get_passages(source)
        if result:
            for x in result:
                if x["Error"]:
                    outputfile.write(x["Origin"] + x["Error"])
                    print(x["Origin"] , x["Error"])
                else:
                    outputfile.write(x["Origin"] + "\n" + "".join(x["contents"]))
                outputfile.write("\n"+"\n")
    print("Completed")
