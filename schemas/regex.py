REGEX = {
    "mobile_phone": r"^(090|080|070)-\d{4}-\d{4}$",
    # "home_phone": r"^0([0-9]-[0-9]{4}|[0-9]{2}-[0-9]{3}|[0-9]{3}-[0-9]{2}|[0-9]{4}-[0-9])-[0-9]{4}$",
    "home_phone": r"^(((\d{2}-\d{4})|(\d{3}-\d{3,4})|(\d{4}-\d{2})|(\d{5}-\d{1}))-\d{4})|(\d{4}-\d{3}-\d{3})$",
    "emergency_contact": r"^0([0-9]-[0-9]{4}|[0-9]{2}-[0-9]{3}|[0-9]{3}-[0-9]{2}|[0-9]{4}-[0-9])-[0-9]{4}$|^(090|080|070)-\d{4}-\d{4}$",
    "postal_code": r"^\d{3}\-\d{4}$",
    "ymd": r"^\d{4}\/\d{2}\/\d{2}$",
    "ym": r"^\d{4}\/\d{2}$",
    "email": r"^([a-zA-Z0-9])+([a-zA-Z0-9\._-])*@([a-zA-Z0-9_-])+([a-zA-Z0-9\._-]+)+$",
}
