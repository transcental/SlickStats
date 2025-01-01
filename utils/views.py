def generate_home_view(
    lastfm_username: str | None,
    lastfm_api_key: str | None,
    steam_id: str | None,
    steam_api_key: str | None,
    jellyfin_url: str | None,
    jellyfin_api_key: str | None,
    jellyfin_username: str | None,
    default_pfp: str | None,
    music_pfp: str | None,
    film_pfp: str | None,
    huddle_pfp: str | None,
    gaming_pfp: str | None,
    user_exists: bool,
    enabled: bool
) -> dict:
    if not user_exists:
        return {
            "type": "home",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "Welcome to Slick Stats",
                        "emoji": True,
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "plain_text",
                        "text": "Hi there! I'll be updating your status when you use one of the various services I support. To get started, please click the button below to authorise me to update your status!",
                        "emoji": True,
                    },
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": ":slack: Authorise",
                                "emoji": True,
                            },
                            "style": "primary",
                            "url": "https://slickstats.transcental.dev/slack/install",
                            "action_id": "authorise-btn",
                        }
                    ],
                },
            ],
        }
    return {
        "type": "home",
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "SlickStats Settings",
                    "emoji": True,
                },
            },
            {
			"type": "section",
    			"text": {
    				"type": "mrkdwn",
    				"text": "SlickStats is currently enabled and your status is being updated! :neodog_happy:" if enabled else "SlickStats is currently disabled. Your status will not be updated. :neodog_sob:"
    			},
    			"accessory": {
    				"type": "button",
    				"text": {
    					"type": "plain_text",
    					"text": "Disable" if enabled else "Enable",
    					"emoji": True
    				},
    				"value": "toggle_enabled",
    				"action_id": "toggle_enabled",
    				"style": "danger" if enabled else "primary"
    			}
            },
            {"type": "divider"},
            {
                "type": "input",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "lastfm_username",
                    "initial_value": lastfm_username if lastfm_username else "",
                },
                "label": {
                    "type": "plain_text",
                    "text": "Last.fm Username",
                    "emoji": False,
                },
            },
            {
                "type": "context",
                "elements": [{"type": "mrkdwn", "text": "_Your account username!_"}],
            },
            {
                "type": "input",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "lastfm_api_key",
                    "initial_value": lastfm_api_key if lastfm_api_key else "",
                },
                "label": {
                    "type": "plain_text",
                    "text": "Last.fm API Key",
                    "emoji": False,
                },
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "_Get this from <https://www.last.fm/api/account/create|here>_",
                    }
                ],
            },
            {"type": "divider"},
            {
                "type": "input",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "steam_id",
                    "initial_value": steam_id if steam_id else "",
                },
                "label": {"type": "plain_text", "text": "Steam ID", "emoji": False},
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "_Put your profile URL into <https://steamdb.info/calculator/|SteamDB> and copy the SteamID field_",
                    }
                ],
            },
            {
                "type": "input",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "steam_api_key",
                    "initial_value": steam_api_key if steam_api_key else "",
                },
                "label": {
                    "type": "plain_text",
                    "text": "Steam API Key",
                    "emoji": False,
                },
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "_Get this from <https://steamcommunity.com/dev/apikey|here>. You need 2FA on your account_",
                    }
                ],
            },
            {"type": "divider"},
            {
                "type": "input",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "jellyfin_url",
                    "initial_value": jellyfin_url if jellyfin_url else "",
                },
                "label": {"type": "plain_text", "text": "Jellyfin URL", "emoji": False},
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "_The URL of your Jellyfin instance_",
                    }
                ],
            },
            {
                "type": "input",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "jellyfin_api_key",
                    "initial_value": jellyfin_api_key if jellyfin_api_key else "",
                },
                "label": {
                    "type": "plain_text",
                    "text": "Jellyfin API Key",
                    "emoji": False,
                },
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "_Get this from `/web/#/dashboard/keys` on your Jellyfin server_",
                    }
                ],
            },
            {
                "type": "input",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "jellyfin_username",
                    "initial_value": jellyfin_username if jellyfin_username else "",
                },
                "label": {
                    "type": "plain_text",
                    "text": "Jellyfin Username",
                    "emoji": False,
                },
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "_Your Jellyfin account username for your server_",
                    }
                ],
            },
            {"type": "divider"},
            {
                "type": "input",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "default_pfp",
                    "initial_value": default_pfp if default_pfp else "",
                },
                "label": {
                    "type": "plain_text",
                    "text": "Default PFP",
                    "emoji": False,
                },
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "_Set this to your normal PFP_",
                    }
                ],
            },
            {
                "type": "input",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "music_pfp",
                    "initial_value": music_pfp if music_pfp else "",
                },
                "label": {
                    "type": "plain_text",
                    "text": "Musical PFP",
                    "emoji": False,
                },
            },
            {
                "type": "input",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "film_pfp",
                    "initial_value": film_pfp if film_pfp else "",
                },
                "label": {
                    "type": "plain_text",
                    "text": "Film PFP",
                    "emoji": False,
                },
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "_Set this to an image URL if you want your PFP to change when watching a film or TV show_",
                    }
                ],
            },
            {
                "type": "input",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "huddle_pfp",
                    "initial_value": huddle_pfp if huddle_pfp else "",
                },
                "label": {
                    "type": "plain_text",
                    "text": "Huddle PFP",
                    "emoji": False,
                },
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "_Set this to an image URL if you want your PFP to change when you're in a Slack huddle_",
                    }
                ],
            },
            {
                "type": "input",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "gaming_pfp",
                    "initial_value": gaming_pfp if gaming_pfp else "",
                },
                "label": {
                    "type": "plain_text",
                    "text": "Gaming PFP",
                    "emoji": False,
                },
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "_Set this to an image URL if you want your PFP to change when playing a game_",
                    }
                ],
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Submit", "emoji": True},
                        "value": "submit_settings",
                        "style": "primary",
                        "action_id": "submit_settings",
                    }
                ],
            },
            {"type": "divider"},
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "_Not working? Try re-authorising the app._",
                    }
                ],
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": ":slack: Re-authorise",
                            "emoji": True,
                        },
                        "style": "danger",
                        "url": "https://slickstats.transcental.dev/slack/install",
                        "action_id": "authorise-btn",
                    }
                ],
            },
        ],
    }
