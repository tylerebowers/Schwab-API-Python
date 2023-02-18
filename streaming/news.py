from streaming import utilities


def headline(keys, fields, command="SUBS"):
    return utilities.request(command, "NEWS_HEADLINE", keys, fields)


def headlineList(keys, fields, command="SUBS"):
    return utilities.request(command, "NEWS_HEADLINELIST", keys, fields)


def headlineStory(keys, fields, command="SUBS"):
    return utilities.request(command, "NEWS_STORY", keys, fields)
