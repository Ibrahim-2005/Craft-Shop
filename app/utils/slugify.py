import re


def slugify(value):
    value = re.sub(r"[^\w\s-]", "", value.lower()).strip()
    return re.sub(r"[-\s]+", "-", value)
