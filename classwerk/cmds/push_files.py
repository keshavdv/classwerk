#!/usr/bin/env python
import git
from git import Repo

from classwerk.utils import *

def add_subparser(parser, subparser):
    parser = subparser.add_parser("push-files", help='push code to student repos', parents=[parser])
    parser.set_defaults(command=update_files)

def update_files(args, handle, **kwargs):
    c = get_config(args.config)
    org = handle.organization(c['organization'])

    teams = filter_teams(c['teams'], args.filter)
    teams_with_failure = []

    for i, team in enumerate(teams, 1):
        members = c['teams'][team]

        if 'prefix' in c:
            name = "%s-%s" % (c['prefix'], team)
        else:
            name = team

        repo_path = "git@%s:%s/%s.git" % (get_github_url(args.file, args.profile), c['organization'], name)
        repo_short = "%s/%s" % (c['organization'], name)

        print "-> %s (%s/%s)" % (name, i, len(teams))

        # Check if github repo for team exists
        with TemporaryDirectory() as temp_dir:
            repo = Repo.clone_from(repo_path, temp_dir)
            print "  \-> Cloned student repo from %s" % repo_path

            upstream = repo.create_remote('upstream', c['source'])
            upstream.fetch()

            print "  \-> Fetched latest upstream"
            repo.git.checkout('upstream/%s' % c['source-branch'], track=True, b='upstream')
            repo.heads.upstream.checkout()

            repo.heads.master.checkout()
            try:
                repo.git.merge('upstream')
                print "  \-> %s" % Colors.success("Merged latest upstream")
            except git.exc.GitCommandError as e:
                repo.git.merge(abort=True)
                repo.git.checkout('upstream/%s' % c['source-branch'], track=True, b='merge-this')
                repo.remotes.origin.push('merge-this')
                teams_with_failure.append(name)

                print "  \-> %s" % Colors.error("Failed to merge latest upstream (conflicts). Pushed to merge-this branch")


            repo.remotes.origin.push(all=True)
            print "  \-> Pushed all branches"

    if len(teams_with_failure) > 0:
        print "-> The following repositories had merge conflicts. Please notify these students and ask them to merge the 'merge-this' branch into master"
        for team in teams_with_failure:
            print "  -> %s" % team

