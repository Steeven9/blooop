# Debug/local config

# The bot alias, used for logging. Must match the NAMEBOT_TOKEN variable
bot_name = "local"
# The Twitter List ID
list_id = 1550597761648713728
# The Discord channel to send the messages to
channel_id = 935532391550820372
# The role to ping when a new tweet drops
role_id = 942805359494574111
# Whether to include retweets as well
enable_retweets = False

# An array of keywords to match for schedule tweets
schedule_keywords = ["schedule", "weekly"]
# Same as above but for guerrilla tweets
guerrilla_keywords = ["guerrilla", "guerilla", "gorilla"]

# Myth
talents = [
    "gawrgura", "moricalliope", "ninomaeinanis", "takanashikiara",
    "watsonameliaEN"
]
# Hope
talents += ["irys_en"]
# Council
talents += [
    "ceresfauna",
    "hakosbaelz",
    "nanashimumei_en",
    "ourokronii",
    # "tsukumosana",
]
# ID gen 1
talents += [
    "ayunda_risu",
    "airaniiofifteen",
    "moonahoshinova",
]
# ID gen 2
talents += [
    "anyamelfissa",
    "kureijiollie",
    "pavoliareine",
]
# ID gen 3
talents += [
    "kaelakovalskia",
    "kobokanaeru",
    "vestiazeta",
]
# TEMPUS HQ
talents += ["noirvesper_en", "axelsyrios", "magnidezmond", "regisaltare"]
# TEMPUS Vanguard
talents += ["gavisbettel", "machinaxflayon", "banzoinhakka", "josuijishinri"]

extra_pings = [{
    "talent": "ninomaeinanis",
    "channel": 225654873599901696,
    "role": None
}, {
    "talent": "gavisbettel",
    "channel": 225654873599901696,
    "role": None
}]
