import dotenv

import msg_parser

config = dotenv.dotenv_values("../.env.test")

msg = msg_parser.GiveawayMessage()
msg.title = "Hello World"
msg.description = "This is a wonderful game."
msg.price = 28.53
msg.link = "https://image-url.com/image123"
msg.platform = "PC, Steam"
# msg.source = "https://steampowered.com/title/578492"

parsed = msg_parser.parse_template(config["MSG_GIVEAWAY"], msg)

print(parsed)
