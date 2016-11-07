# http://inamidst.com/saxo/
# Created by Sean B. Palmer

import re, sys, time, os
import saxo

#from importlib.machinery import SourceFileLoader
#r = SourceFileLoader("r", "/home/docker/ircbot/saxo/ircpic/commands/r").load_module()

sys.path.append('/home/docker/ircbot/saxo/reddit')
from reddit2 import r2

regex_link = re.compile(r"\b[кКkK][0oOоОAaАа][тТTt1][эЭ3зЗiI1иИN]")

@saxo.event("PRIVMSG")
def cats(irc):
    if irc.sender == '#sotona' and irc.nick == 'Lavos' and regex_link.search(irc.text):
        #print(dir(irc))
        #print(dir(saxo))
        #print(saxo.env, dir(saxo.env))
        os.environ["SAXO_NICK"] = irc.nick
        o = r2('cats', saxo)
        #print(o)
        irc.say("%s: %s | СЛАВА РОБАТАМ СЛАВА СОТОНЕ" % (irc.nick, o))
    if 'т прнс?' in irc.text and irc.sender == '#sotona':
        os.environ["SAXO_NICK"] = irc.nick
        irc.say("%s: я прнс %s" % (irc.nick, r2('cats', saxo)))
