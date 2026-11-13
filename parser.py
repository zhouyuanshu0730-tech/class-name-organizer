
import re
from class_config import CLASS_KEYWORDS, DEFAULT_CLASS_NUMBER


GENDER_WORDS = {
    "男", "女", "男性", "女性", "男生", "女生"
}

FIELD_PATTERNS = {
    "手机号": r"(?<!\d)1[3-9]\d{9}(?!\d)",
    "出生日期": r"(?:19|20)\d{2}[年./-]\d{1,2}[月./-]\d{1,2}日?",
    "政治面貌": r"中共党员|中共预备党员|共产党员|共青团员|群众|民主党派",
}

JOB_WORDS = [
    "班长", "副班长", "团支书", "学习委员",
    "生活委员", "组织委员", "宣传委员",
    "纪律委员", "心理委员", "文体委员"
]


def clean_line(line):
    line = str(line).strip()
    if not line:
        return ""

    line = re.sub(
        r"^\s*(?:\d+\s*[.、．)）]\s*|[（(]\d+[）)]\s*)",
        "",
        line
    )
    return line.strip()


def find_class(text):
    keywords = sorted(CLASS_KEYWORDS, key=len, reverse=True)
    keyword_pattern = "|".join(re.escape(k) for k in keywords)

    pattern = (
        rf"(?P<year>20\d{{2}}|\d{{2}})\s*"
        rf"(?P<major>{keyword_pattern})\s*"
        rf"(?P<number>\d+|[一二三四五六七八九十]+)?\s*班?"
    )

    match = re.search(pattern, text)

    if not match:
        return "", text

    number_map = {
        "一": "1", "二": "2", "三": "3", "四": "4",
        "五": "5", "六": "6", "七": "7", "八": "8",
        "九": "9", "十": "10"
    }

    year = match.group("year")
    major = match.group("major")
    number = match.group("number") or DEFAULT_CLASS_NUMBER
    number = number_map.get(number, number)

    class_name = f"{year}{major}{number}班"

    remaining = text[:match.start()] + " " + text[match.end():]
    return class_name, remaining


def split_fields(text):
    return [
        item.strip()
        for item in re.split(r"[\s,，;；|｜、\t]+", text)
        if item.strip()
    ]


def parse_line(line):
    line = clean_line(line)
    if not line:
        return None

    class_name, remaining = find_class(line)

    result = {"班级": class_name}

    # 手机号
    for match in re.findall(FIELD_PATTERNS["手机号"], remaining):
        result["手机号"] = match
        remaining = remaining.replace(match, " ", 1)

    # 出生日期
    for match in re.findall(FIELD_PATTERNS["出生日期"], remaining):
        result["出生日期"] = match
        remaining = remaining.replace(match, " ", 1)

    # 政治面貌
    for match in re.findall(FIELD_PATTERNS["政治面貌"], remaining):
        result["政治面貌"] = match
        remaining = remaining.replace(match, " ", 1)

    parts = split_fields(remaining)
    name_parts = []
    other_parts = []

    for part in parts:
        if part in GENDER_WORDS:
            result["性别"] = "男" if "男" in part else "女"
        elif part in JOB_WORDS:
            result["职务"] = part
        elif re.fullmatch(r"\d{1,2}岁", part):
            result["年龄"] = part
        else:
            name_parts.append(part)

    # 姓名优先保留，其他文字不丢弃
    if name_parts:
        result["姓名"] = name_parts[0]
        if len(name_parts) > 1:
            other_parts.extend(name_parts[1:])
    else:
        result["姓名"] = ""

    if other_parts:
        result["其他信息"] = "；".join(other_parts)

    return result


def parse_text(text):
    results = []

    for line in text.splitlines():
        result = parse_line(line)
        if result:
            results.append(result)

    # 动态列：根据实际出现的字段生成
    columns = ["班级", "姓名"]

    for row in results:
        for key in row:
            if key not in columns:
                columns.append(key)

    return [
        {column: row.get(column, "") for column in columns}
        for row in results
    ]
