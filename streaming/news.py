from streaming import utilities


def headline(keys, fields):
    return utilities.SUBS("NEWS_HEADLINE", keys, fields)


def headlineList(keys, fields):
    return utilities.SUBS("NEWS_HEADLINELIST", keys, fields)


def headlineStory(keys, fields):
    return utilities.SUBS("NEWS_STORY", keys, fields)
