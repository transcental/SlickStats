# Slick Stats

Slick Stats is a Slack app that automatically updates your Slack status and profile picture to show what you're up to on a variety of platforms. To use it, just visit the app home [here](https://hackclub.slack.com/app_redirect?channel="U0754EVVCD9"), authorise and add your credentials!

## Features

- PFP Switching for some services
- Status setting for some services
- Supports (in order of priority):
  - Slack Huddles
  - Steam
  - Jellyfin
  - Last.fm
- Logging of all status changes to a centralised channel
 
Services coming soon:
- ListenBrainz
- Nintendo Switch

## Contributing
Contributions are welcome! If you're working on a feature, please open an issue first and say you're working on it. If you're having trouble, you can [message me on Slack](https://hackclub.slack.com/app_redirect?channel="U054VC2KM9P") or open an issue.

Make sure to install the pre-commit hooks by running `pre-commit install` after cloning the repo and installing the dependencies.

### Setup

**The person installing this for the first time must be a workspace admin/owner**

Create a Slack app from the [dashboard](https://api.slack.com/apps) with the manifest from the [manifest.json](manifest.json) file. Change out the request URL to your server's URL (e.g. `https://your-url.tld/slack/events`).


After cloning the repo, you will need to add the environment variables. Use the `.env.example` file as a template and create a `.env` file in the root of the project. The following environment variables are required:

- Required
  - `SLACK_CLIENT_ID` - The client ID for your Slack app
  - `SLACK_CLIENT_SECRET` - The client secret for your Slack app
  - `SLACK_TOKEN` - The bot token for your Slack app (xoxb)
  - `SLACK_TEAM_ID` - The team ID for your Slack workspace (find this using `/sdt whoami`)
  - `SLACK_SIGNING_SECRET` - The signing secret for your Slack app
  - `SLACK_LOG_CHANNEL` - The ID of the channel to log all status changes to
  - `MONGO_URI` - The URI to your MongoDB database (e.g. `mongodb://admin:password@localhost:27017/?retryWrites=true&w=majority&appName=SlickStats`)
  - `DOMAIN` - The domain of your server (e.g. `https://your-url.tld`). Do not include a trailing slash.
- Optional
  - `ENV` - Should be set to `development` or `production`. Defaults to `development`
  - `PORT` - The port to run the Starlette server on. Defaults to `3000`
  - `SLACK_HEARTBEAT_CHANNEL` - Extra channel to send debug messages to. Only use if you need it or are dev-ing

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python3.12 -m pip install -r requirements.txt
python3.12 app.py
```

To install the app for the first time, visit your `https://YOUR-URL.TLD/slack/install?team_id=TEAM_ID` and add the app to your workspace.

Need help? Send me a message on the Hack Club Slack, open an issue here, shoot me an email at amber (at) transcental (dot) dev or get in contact with me anywhere else you can find me!

## License
All code in this repository is licensed under the GNU Affero General Public License v3.0, unless otherwise specified. See the [LICENSE](LICENSE.md) file for more information.
