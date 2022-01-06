class GiveawayMessage:
    def __init__(self):
        self.platform = None
        self.title = None
        self.description = None
        self.price = None
        self.image = None
        self.link = None


def parse_template(template: str, msg: GiveawayMessage) -> str:
    with open(template, "r", encoding="utf-8") as f:
        content = f.read()
    return content \
        .replace("{BOLDON}", "<b>") \
        .replace("{BOLDOFF}", "</b>") \
        .replace("{SOURCE}", str(msg.platform)) \
        .replace("{TITLE}", str(msg.title)) \
        .replace("{DESCRIPTION}", str(msg.description)) \
        .replace("{PRICE}", str(msg.price)) \
        .replace("{LINK}", "<a href='" + str(msg.link) + "'> " + str(msg.link) + "</a>" if msg.link is not None else "") \
        .replace("{IMAGE}", "<img src='" + str(msg.image) + "'>" if msg.image is not None else "")
