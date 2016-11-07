#!/usr/bin/env python3

from __future__ import print_function

import os, time, datetime, re, sys
import itertools
import praw
#import saxo
#from reddit2 import r2

import pprint

subreddit_r = re.compile('[a-zA-Z0-9]+')
subreddit_r = re.compile('cats?_?(gifs)?')

def drop_empty(db, tname):
    c = db.connection.cursor()
    urls = c.execute("select url from %s" % tname).fetchone()
    if urls == None:
        c.execute("drop table %s" % tname)
        db.commit()

def r2(arg, saxo):
    if not arg:
        return "Fetch links from reddit"
    if not saxo.env("base"):
        return "Sorry, this command requires an IRC instance"
    args = arg.split(' ')
    n = 1
    if len(args) >= 1:
        sname = args[0].lower()
    if len(args) >= 2:
        n = int(args[1])
    if n > 8:
        return "Sorry, link count should be less than 9"
    if n < 1:
        return "wat?"
    if not subreddit_r.match(sname):
        return "Sorry, subreddit name must match " + subreddit_r.pattern

    req_nick = saxo.env("nick").encode('utf-8', 'surrogateescape').decode('utf-8')
    if req_nick == "Lavos" and cats_r.match(sname, flags=re.I):
        return "The struggle is real. Welcome back."

    path = os.path.join(saxo.env("base"), "database.sqlite3")
    with saxo.database(path) as db:
        c = db.connection.cursor()
        if not "reddit_stat" in db:
            db['reddit_stat'].create(("name", "text unique"), ("value", str))

        tname = "reddit_%s" % sname
        if not tname in db:
            db[tname].create(('url', 'text unique'), ('req_by', str), ('title', 'text default null'))

        posts = c.execute("select url, title from %s where req_by = ''" % tname).fetchmany(n)
        if posts == None or posts == []:
            rtime = c.execute("select value from reddit_stat where name = ?", [tname]).fetchone()
            if rtime != None and rtime[0] == str(datetime.date.today()):
                return "No more %s for today" % sname
            try:
                reddit = praw.Reddit(user_agent='irc_pic_bot')
                s = reddit.get_subreddit(sname).get_hot(limit=32)
                for x in s:
                    if 'imgur.com' in x.url or \
                       'gfycat.com' in x.url or \
                       x.url.endswith(('.jpg', '.jpeg', '.gif', '.png', '.gifv', '.webm')):
                        c.execute("replace into %s values(?, '', ?)" % tname, [x.url, x.title])
                db.commit()
            except:
                drop_empty(db, tname)
                return "Something went wrong while fetching posts. Sorry."
            c.execute("replace into reddit_stat values (?, ?)", [tname, str(datetime.date.today())])
            db.commit()
            posts = c.execute("select url, title from %s where req_by = ''" % tname).fetchmany(n)

        if posts == None or posts == []:
            drop_empty(db, tname)
            return "No more posts. Maybe I can't get any pictures. Maybe you specified bad subreddit. Or maybe reddit is down."

        urls = [ p[0] for p in posts ]
        req_nicks = [req_nick] * len(urls)
        vals = list(zip(urls, req_nicks))
        #warning(vals, len(vals))
        c.executemany("replace into %s (url, req_by) values (?, ?)" % tname, vals)
        db.commit()

        rurls = ''
        for u in urls:
            if 'imgur.com' in u and u.endswith('.gif'):
                u += 'v'
            rurls += ' ' + u
        if n == 1 and posts[0][1] is not None:
            rurls += ' ' + posts[0][1]
        return rurls

