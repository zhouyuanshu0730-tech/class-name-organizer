
import re
from class_config import CLASS_KEYWORDS, DEFAULT_CLASS_NUMBER


def clean_line(line):
    """清理空行、序号和多余空格"""
    line = line.strip()

    if not line:
        return ""

    # 删除开头序号，例如：1.、2、3、4）
    line = re.sub(
        r"^\s*(?:\d+\s*[.、．)）]\s*|[（(]\d+[）)]\s*)",
        "",
        line
    )

    # 删除所有空格
    line = re.sub(r"\s+", "", line)

    return line


def parse_line(line):
    """识别单条名单"""
    line = clean_line(line)

    if not line:
        return None

    keywords = sorted(CLASS_KEYWORDS, key=len, reverse=True)
    keyword_pattern = "|".join(re.escape(k) for k in keywords)

    pattern = (
        rf"^(?P<year>20\d{{2}}|\d{{2}})"
        rf"(?P<major>{keyword_pattern})"
        rf"(?P<number>\d+)?"
        rf"班?"
        rf"(?P<name>.*)$"
    )

    match = re.match(pattern, line)

    if match:
        year = match.group("year")
        major = match.group("major")
        number = match.group("number")
        name = match.group("name")

        if not number:
            number = DEFAULT_CLASS_NUMBER

        class_name = f"{year}{major}{number}班"

    else:
        class_name = ""
        name = line

    return {
        "班级": class_name,
        "姓名": name
    }


def parse_text(text):
    """批量整理多行名单"""
    results = []

    for line in text.splitlines():
        result = parse_line(line)

        if result is not None:
            results.append(result)

    return results
