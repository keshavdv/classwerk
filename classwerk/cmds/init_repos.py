import tempfile

import github3
from git import Repo

from classwerk.utils import Colors
from classwerk.utils import get_config
from classwerk.utils import get_github_url
from classwerk.utils import filter_teams
from classwerk.utils import TemporaryDirectory

def add_subparser(parser, subparser):
    parser = subparser.add_parser("init-repos", help='create and initialize repositories', parents=[parser])
    parser.add_argument('--force', action='store_const', const=True, help='force push even if repo exists',
                            required=False, default=False)
    parser.set_defaults(command=init_repos)

def init_repos(args, handle, **kwargs):
  c = get_config(args.config)
  org = handle.organization(c['organization'])

  all_teams = org.teams()

  # Search for existing student team
  all_student_team = None
  for avail_team in all_teams:
      if avail_team.name == "Students":
          all_student_team = avail_team

  if not all_student_team:
    all_student_team = org.create_team("Students", permission='pull')

  teams = filter_teams(c['teams'], args.filter)

  # Create all the required teams
  for i, team in enumerate(teams, 1):
    members = [ member.lower() for member in c['teams'][team]]

    if 'prefix' in c:
        team_name = "%s-%s" % (c['prefix'], team)
    else:
        team_name = team

    print "-> %s (%s/%s)" % (team, i, len(teams))

    # Create teams on Github
    try:
        team = org.create_team(team_name, permission='push')
        print "  \-> %s" % Colors.success("Created team")

    except github3.exceptions.UnprocessableEntity:

        # Team probably exists, so find it
        print "  \-> %s" % Colors.warn("Team exists")
        for avail_team in org.teams():
            if avail_team.name == team_name:
                team = avail_team

    # Remove members no longer in a group
    existing_members = []
    for prev_member in team.members():
      existing_members.append(prev_member.login.lower())
      if prev_member.login.lower() not in members:
        print "  \-> %s" % Colors.success("Removed %s" % prev_member)
        team.remove_member(prev_member)

   # Invite team members that aren't already a part of the group

    for member in set(members) - set(existing_members):
        invitation = team.invite(member)
        if invitation:
            all_student_team.invite(member)
            print "  \-> %s" % Colors.success("Invited %s" % member)
        else:
            print "  \-> %s" % Colors.warn("User %s does not exist" % member)

    

    # Create all the repositories
    repo_path = "git@%s:%s/%s.git" % (get_github_url(args.file, args.profile), c['organization'], team_name)
    repo_short = "%s/%s" % (c['organization'], team_name)


    # Create repo and add team to collaborators
    try:
        org.create_repository(team_name, private=c['private'])
        print "  \-> %s" % Colors.success("Created repo")
    except github3.exceptions.UnprocessableEntity:
        # Already exists
        print "  \-> %s" % Colors.warn("Repo already exists")
    else:
      with TemporaryDirectory() as temp_dir:
          # Initializes repo and adds README
          repo = Repo.init(temp_dir)

          # Commit the changes to deviate masters history
          repo.index.commit("Initial commit.")
          origin = repo.create_remote('origin', repo_path)

          # Add upstream branch that tracks source repo
          upstream = repo.create_remote('upstream', c['source'])
          upstream.fetch()

          repo.git.checkout('upstream/%s' % c['source-branch'], track=True, b='upstream')
          repo.heads.upstream.checkout()

          repo.heads.master.checkout()
          repo.git.merge('upstream')

          # Push everything to origin
          print "  \-> Pushing starter code"
          for status in repo.remotes.origin.push(all=True, force=args.force):
              message = "Pushing [%s] resulted in: %s" % (status.local_ref.name, status.summary)

              if status.flags > 1024: # ERROR
                  print "    \-> %s" % Colors.error(message)
              else:
                  print "    \-> %s" % Colors.success(message)

      # Add team and course staff as collaborators
      for team in all_teams:
        if team.name in [team_name, 'TAs']:
          team.add_repository(repo_short)
          team.edit(team.name, permission='push')
          print "  \-> %s" % Colors.success("Added team [%s] as collaborators" % team.name)
