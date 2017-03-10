# slack-jira-sprint-updates
Bot which posts on slack recently finished tickets.

## Setup
To use bot you need to create following environment variables:
```
SLACK_CHANNEL=
JIRA_AUTHORIZATION=         # Basic _token_
GITHUB_TOKEN=
JIRA_PROJECT_NAME=
APPS=                       # for example [{"app_name": "wikia", "repo_name": "app"}, {"app_name": "mercury"}, {"app_name": "mobile-wiki"}]
SLACK_BOT_TOKEN=
SLACK_BOT_NAME=
```

## Running
All you need to do is go to `slack-jira-sprint-updates` dir and run:

`python updater.py`

## Integration with Slack
Go to channel you want to add the bot to and click: `Add a service integration` -> `Bots` -> `Add bot integration` and you'll get your `SLACK_BOT_TOKEN` needed to post a message.

## Schedule it!
To run task periodically, every fixed amount of time, use `cron` or create jenkins job.

For example using cron, to run script every week from Monday to Thursday at 4p.m.:

* run `crontab -e` on machine you want to run the script on.
* paste following line:

`0 16 * * 1-4 python ~/slack-jira-sprint-updates/updater.py`

