def format_ja_numeric(num, unit):
    if not num:
        return ""
    else:
        return "{:,.0f}".format(int(num)) + unit
