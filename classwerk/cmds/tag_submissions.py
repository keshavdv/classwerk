#!/usr/bin/env python
import git
from datetime import datetime
from git import Repo

import github3
from classwerk.utils import *

def add_subparser(parser, subparser):
    parser = subparser.add_parser("tag-submissions", help='tag all student repos', parents=[parser])
    parser.add_argument('-t', '--tag', help='name of tag', required=True)
    parser.add_argument('-m', '--message', help='message for tag', required=True)
    parser.set_defaults(command=add_tag)

def add_tag(args, handle, **kwargs):
    c = get_config(args.config)
    org = handle.organization(c['organization'])
    teams = filter_teams(c['teams'], args.filter)

    i = 1
    for repo in org.repositories():
        
        tag = False
        if 'prefix' in c:
            name = "%s-%s" % (c['prefix'], team)
            if repo.name.startswith(c['prefix']) and repo.name[len(c['prefix']):] in teams:
                tag = True
        else:
            name = repo.name
            if repo.name in teams:
                tag = True

        if tag:
            print "-> %s (%s/%s)" % (name, i, len(teams))
            try:
                repo.create_release(args.tag, "master", name=args.tag, body=args.message)
                print "  \-> %s" % Colors.success("Created release")
            except:
                print "  \-> %s" % Colors.warn("Release already exists")
            
            i += 1


