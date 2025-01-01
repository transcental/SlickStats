# Slick Stats

Slick Stats is a Slack bot that will automatically update your Slack status to show what you're up to on a variety of platforms. To use it, just visit the app home, authorise and add your credentials!

## Features

- PFP Switching for some services
- Status setting for some services
- PFP Switching for Slack huddles
- Supports (in order of priority):
  - Steam
  - Jellyfin
  - Last.fm
 
Services coming soon:
- Nintendo Switch
- ListenBrainz

### Huddle Status
![Huddle example](https://cloud-9rhwby35x-hack-club-bot.vercel.app/0image.png)
### Last.fm Status
![Last.fm example](https://cloud-9rhwby35x-hack-club-bot.vercel.app/1image.png)
### Steam Status
![Steam example](https://cloud-9rhwby35x-hack-club-bot.vercel.app/2image.png)
### Jellyfin Status
![Jellyfin example](https://cloud-9rhwby35x-hack-club-bot.vercel.app/3image.png)

## Setup

Make a Slack app with the following manifest (make sure to switch out the URL to yours)

```
{
    "display_information": {
        "name": "Slick Stats",
        "description": "Update your status to show what you're doing across other services!",
        "background_color": "#5c235c",
        "long_description": "Slick Stats automatically updates your status to show what you're doing on other services throughout a variety of APIs.\r\n\r\nCurrently supported:\r\n- Last.fm - `{song} - {artist}`\r\n- Steam - `Playing {game} via Steam`\r\n\r\nComing soon:\r\n- Nintendo Switch\r\n\r\nGot a request? Submit an issue at https://github.com/transcental/SlickStats!"
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

After cloning the repo:

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python3.12 -m pip install -r requirements.txt
python3.12 app.py
```

You will also need the following in a `.env` file:

```
SLACK_CLIENT_ID=""
SLACK_CLIENT_SECRET=""
SLACK_SIGNING_SECRET=""
SLACK_LOG_CHANNEL=""

MONGO_URI=""
```
