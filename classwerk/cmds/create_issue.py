#!/usr/bin/env python
import git
from git import Repo

from classwerk.utils import *

def add_subparser(parser, subparser):
    parser = subparser.add_parser("create-issue", help='create issue from file', parents=[parser])
    parser.add_argument('-t', '--title', help='title of issue', required=True)
    parser.add_argument('-b', '--body', help='folder of files for issues', required=True)
    parser.set_defaults(command=create_issue)

def create_issue(args, handle, **kwargs):
    if not os.path.isdir(args.body):
        print Colors.error("Can't find input directory for issues!")
        sys.exit(1)
    
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
            print "  \-> %s" % Colors.success("Created issue")
            try:
                with open(os.path.join(args.body, name)) as f:
                    repo.create_issue(args.title, f.read())
            except Exception as e:
                print "  \-> Error (%s)" % e
            i += 1

