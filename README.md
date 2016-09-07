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

    $ ./classwerk.py -h
    usage: classwerk.py [-h] -u USERNAME [-p PASSWORD]
                        {collect-results,create-repos,create-teams,push-files,tag-submissions}
                        ...

    Github Administration tools

    positional arguments:
      {collect-results,create-repos,create-teams,delete-repos,download-submissions,push-files,tag-submissions}
                            sub-command help
        collect-results     returns result of Travis for repos
        create-repos        manage student groups
        create-teams        manage student groups
        delete-repos        delete repos and teams
        download-submissions
                            returns result of Travis for repos
        push-files          push code to student repos
        tag-submissions     tag all student repos

    optional arguments:
      -h, --help            show this help message and exit
      -u USERNAME, --username USERNAME
                            Github username
      -p PASSWORD, --password PASSWORD
                            Github password
      -c CONFIG, --config CONFIG
                            path to class config file (default: class.yml)

A normal flow would look something like this:

    $ ./classwerk.py -u <your github username> create-teams
    $ ./classwerk.py -u <your github username> create-repos

    # To update the release code, push changes to the source repository
    # and then run the following
    $ ./classwerk.py -u <your github username> push-files

    # To collect submissions at a deadline, you can simply tag the submissions
    # using the following and collect submissions for autograding at a later point in time with the following
    $ ./classwerk.py -u <your github username> tag-submissions -t "tag" -m "Long description for tag"
    $ ./classwerk.py -u <your github username> download-submissions -t "tag" -o <output dir for submissions>

    # If you enabled Travis, you can automatically collect Travis logs once the builds have completed with the following
    $ ./classwerk.py -u <your github username> collect-results -t "tag" -o <output dir for Travis logs>

Note that all the commands can be run repeatedly without destructive side effects, but isn't recommended. In addition, the `-c` flag can be used to select different configuration files, allowing mangement of multiple classrooms.