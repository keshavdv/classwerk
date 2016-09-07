# classwerk

The classwerk project is a set of scripts to help facilitate using Github as an assignment management platform.


## Class Configuration
The first step is to create a configuration file for a class. Each academic term should ideally have it's own configuration file. The format is as follows:

    $ cat class.yml
    ---
    organization: cornell-cs4411
    prefix: fa15
    source: 'git@github.com:cornell-cs4411/project-release'
    source-branch: 'master'
    teams:
      <unique team name>:
        - <Github username>
        - <Github username>

The main configuration options are detailed below

* organization: The Github organization under which the repos will live
* prefix: A prefix to use for all team names and repos (using the current term is suggested, e.g. fa15, sp16)
* source: The source repo that contains starter code for the assignments
* source-branch: A specific branch to track in the source repository (e.g fa15, sp16)
* enable_travis: Enables TravisCI for created repos
* private: If true, uses private repositories for students
* travis_host: Either https://magnum.travis-ci.com for private repos or https://travis-ci.org for public repos
* readme: Text that should be placed in the README file for each team repo. It may contain both a `{travis_badge}` and `{travis_url}` token that will automatically be replaced during repository creation.

## Class Setup

Once the configuration file is created, we may begin creating Github resources. The `classwerk.py` script is used to manage everything.

    $ classwerk -h
    usage: classwerk [-h]
                 {delete-repos,download-submissions,init-repos,push-files,tag-submissions}
                 ...

    Github Administration tools

    positional arguments:
      {delete-repos,download-submissions,init-repos,push-files,tag-submissions}
                            [-h, --help] for subcommand help
        delete-repos        delete repos and teams
        download-submissions
                            download releases from student repos
        init-repos          create and initialize repositories
        push-files          push code to student repos
        tag-submissions     tag all student repos

    optional arguments:
      -h, --help            show this help message and exit

A normal flow would look something like this:

    $ classwerk init-repos

    # To update the release code, push changes to the source repository
    # and then run the following
    $ classwerk push-files

    # To collect submissions at a deadline, you can simply tag the submissions
    # using the following and collect submissions for autograding at a later point in time with the following
    $ classwerk tag-submissions -t "tag" -m "Long description for tag"
    $ classwerk download-submissions -t "tag" -o <output dir for submissions>

Note that all the commands can be run repeatedly without destructive side effects, but isn't recommended. In addition, the `-c` flag can be used to select different configuration files, allowing mangement of multiple classrooms.