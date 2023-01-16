# Docs

## Methodology

Much of Percheron is based on [DjangoCon Europe/US 2022 sprints](https://glasnt.com/blog/django-contributors-notebook/) work, the results of which is a Jupyter notebook that speaks to the method of data collection, and further discussions. 

Percheron is a stand-alone CLI designed to produce 80% of what's required to produce a list of contributors to a release of Django, specifically for the use of the Django Fellows who create the release notes for a version of Django. 

For the purposes of Percheron, a contribution is _any meaningful contribution to a release of Django_. This is not limited just to the code that ends up in the release, but also includes, and not limited to, discussions, debugging, triage, testing, security, and translations related to the code.

### Data Sources

Django works from a combination of [Trac issue tracking](https://code.djangoproject.com/), [GitHub Pull Requests](https://github.com/django/django/pulls), proxy commits for [security fixes](https://docs.djangoproject.com/en/dev/releases/security/), and [Transifex translations](https://github.com/django/django-docs-translations). 

The main trunk of data used is from the `django/django` git repo. 

The contents of a release of Django is the range of commits between when the release branch was branched from main, up until the HEAD of that branch.  (Read more from [Carlton Gibson](https://noumenal.es/posts/what-is-django-4/zj2/)).

Commits in this range will have commit messages that generally follow the [Django committing guidelines](https://docs.djangoproject.com/en/dev/internals/contributing/committing-code/), with messages containing references to Trac tickets.

Tickets link to pull requests where the commits were merged into the release. All activity and comments for the tickets and pull requests are included in the dataset. 

Additionally, security commits are made on behalf of the reporters of security issues, and while they may be authored by a Django Fellow, include acknowledgement of the reporter/s of the security issue. 

Additionally, while documentation changes are already included in the above process, the translation of these docs are performed in [Transifex](https://www.transifex.com/django/), then outputs of which are committed in [django/django-docs-translations](https://github.com/django/django-docs-translations). 

### Data Structure

The following is the relational mapping, some fields removed for clarity.

* `git_commits`: 
    * `commit_sha`: primary key
    * `author`: git author
    * `author_email`: git email
* `git_trac_links`: 
    * `commit_sha`: link to `git_commit`
    * `trac_ticket_id`: link to `trac_ticket`
* `trac_tickets`:
    * `ticket_id`: primary key
    * `reporter`: GitHub or Django Project username
* `trac_pr_links`:
    * `ticket_id`: link to `trac_tickets`
    * `pull_request`: link to `pull_request`
* `pull_requests`:
    * `id`: primary key
    * `user`: GitHub username
* `pr_comments`:
    * `pull_request`: link to `pull_request`
    * `user`: GitHub username
* `translators`:
    * `name`: Transifex account name
* `thanks`:
    * `name`: free-text name
* `github_userdata`: 
    * `username`: primary key
    * `name`: GitHub account name


## Outputs

`cache/`: 
  * Copies of the git repos cloned, and API calls made (using `https://pypi.org/project/requests-cache/`)

`data/`: 
  * JSON files of the different data sources.

`reports/` 

 * `percheron_list.txt` - A flat list of contributors.
 * `percheron_report.{txt,csv}` - A {ascii table, csv} report of all contributors, per contribution type. 
 * `percheron_data.db` - an SQLite database of all the data above, for use with tools like [Datasette](https://datasette.io/)


## Known limitations

* Translation authors are only publicly visible in the header information of the translation `.po` files ([example](https://github.com/django/django-docs-translations/commit/ce809e91c8d8ade2de7982aa0014e9d1e77c1aa9)). New information in these headers are only added for the calendar year, which may not map to a Django release. 
* Trac uses GitHub logins, but also supports Django Project logins. There's no public API to map non-GitHub logins to names, and often only the names, not usernames, are rendered in the page output. 
* Mapping git commit author names to the names associated to GitHub users may not always be 100% complete. 