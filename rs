#!/usr/bin/env python3

from __future__ import print_function

import os, time, datetime, re, sys
import itertools
import praw
import saxo

import pprint

def warning(*objs):
    print("WARNING: ", *objs, file=sys.stderr)

subreddit_r = re.compile('[a-zA-Z0-9]+')

@saxo.command()
def rs(arg):
    if not saxo.env("base"):
        return "Sorry, this command requires an IRC instance"
    if not arg:
        return "Specify subreddit name"
    else:
        sname = arg.lower()
    path = os.path.join(saxo.env("base"), "database.sqlite3")
    with saxo.database(path) as db:
        c = db.connection.cursor()

        tname = "reddit_%s" % sname
        if not tname in db:
            return "No such subreddit"

        top = c.execute("select count(*),req_by from %s where req_by != '' group by req_by order by 1 desc;" % tname).fetchmany(5)
        return sname + ': ' + ', '.join([ "{0}:{1}".format(x[1], x[0]) for x in top ])

