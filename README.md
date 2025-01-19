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

Create a Slack app from the [dashboard](https://api.slack.com/apps) with the following manifest (make sure to switch out the URL to yours)

```json
{
    "display_information": {
        "name": "Slick Stats Dev",
        "description": "Development version of @Slick Stats",
        "background_color": "#2b592a",
        "long_description": "Woah, hey I'm the dev version of @Slick Stats. I really don't think you should mess around with me, it could break your @Slick Stats experience which you really don't want do you?"
    },
    "features": {
        "app_home": {
            "home_tab_enabled": true,
            "messages_tab_enabled": true,
            "messages_tab_read_only_enabled": false
        },
        "bot_user": {
            "display_name": "Slick Stats Dev",
            "always_online": true
        }
    },
    "oauth_config": {
        "redirect_urls": [
            "https://URL/slack/oauth_redirect"
        ],
        "scopes": {
            "user": [
                "users.profile:read",
                "users.profile:write",
                "users:read"
            ],
            "bot": [
                "chat:write",
                "chat:write.public",
                "commands",
                "emoji:read",
                "im:history",
                "team:read",
                "users.profile:read",
                "users:read",
                "chat:write.customize"
            ]
        }
    },
    "settings": {
        "event_subscriptions": {
            "request_url": "URL/slack/events",
            "bot_events": [
                "app_home_opened",
                "message.im",
                "user_huddle_changed"
            ]
        },
        "interactivity": {
            "is_enabled": true,
            "request_url": "URL/slack/events",
            "message_menu_options_url": "URL/slack/events"
        },
        "org_deploy_enabled": false,
        "socket_mode_enabled": false,
        "token_rotation_enabled": false
    }
}
```

After cloning the repo, you will need to add a `.env` file with the following variables. You can get copy `.env.example` and fill in the values.

- Required
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
