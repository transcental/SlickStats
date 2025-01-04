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

### Setup

Create a Slack app from the [dashboard](https://api.slack.com/apps) with the following manifest (make sure to switch out the URL to yours)

```json
{
    "display_information": {
        "name": "Slick Stats",
        "description": "Update your status to show what you're doing across other services!",
        "background_color": "#5c235c",
        "long_description": "Slick Stats automatically updates your status to show what you're doing on other services throughout a variety of APIs.\r\n\r\nCurrently supported:\r\nLast.fm, Steam, Jellyfin, Slack Huddles\r\n\r\nComing soon:\r\nNintendo Switch, ListenBrainz\r\n\r\nGot a request? Submit an issue at https://github.com/transcental/SlickStats!"
    },
    "features": {
        "app_home": {
            "home_tab_enabled": true,
            "messages_tab_enabled": false,
            "messages_tab_read_only_enabled": false
        },
        "bot_user": {
            "display_name": "Slick Stats",
            "always_online": true
        }
    },
    "oauth_config": {
        "redirect_urls": [
            "URL/slack/oauth_redirect"
        ],
        "scopes": {
            "user": [
                "users.profile:read",
                "users.profile:write",
                "users:read"
            ],
            "bot": [
                "chat:write",
                "chat:write.customize",
                "commands",
                "im:history",
                "team:read",
                "users.profile:read",
                "users:read",
                "emoji:read"
            ]
        }
    },
    "settings": {
        "event_subscriptions": {
            "bot_events": [
                "app_home_opened",
                "message.im",
                "user_huddle_changed"
            ]
        },
        "interactivity": {
            "is_enabled": true
        },
        "org_deploy_enabled": false,
        "socket_mode_enabled": true,
        "token_rotation_enabled": false
    }
}
```

After cloning the repo, you will need to add a `.env` file with the following variables. You can get copy `.env.example` and fill in the values.

- Required
  - `SLACK_APP_TOKEN` - The app token for your Slack app for connecting via Socket mode
  - `SLACK_CLIENT_SECRET` - The client secret for your Slack app
  - `SLACK_SIGNING_SECRET` - The signing secret for your Slack app
  - `SLACK_LOG_CHANNEL` - The ID of the channel to log all status changes to
  - `MONGO_URI` - The URI to your MongoDB database (e.g. `mongodb://admin:password@localhost:27017/?retryWrites=true&w=majority&appName=SlickStats`)
- Optional
  - `ENV` - Should be set to `development` or `production`. Defaults to `development`
  - `PORT` - The port to run the Starlette server on. Defaults to `3000`

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python3.12 -m pip install -r requirements.txt
python3.12 app.py
```

To install the app, visit your `https://YOUR-URL.TLD/slack/install` and add the app to your workspace.


## License
All code in this repository is licensed under the GNU Affero General Public License v3.0, unless otherwise specified. See the [LICENSE](LICENSE.md) file for more information.
