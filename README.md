# TikTok Repost Notifier

This project checks one or more public TikTok profiles for new videos and sends you an email and/or SMS message when new posts appear. It runs automatically on GitHub Actions every 15 minutes.

## Features

- Monitor multiple TikTok usernames.
- Send notifications via Gmail SMTP and/or Twilio SMS.
- Keeps track of posts already reported so you are only notified once.
- Works entirely through GitHub Actions (no need to run anything locally).

## Quick Start

1. **Fork this repository** to your GitHub account. Forking creates a copy of the
   project under your username (look for it at `https://github.com/<your-user>/tiktok_repost_notifier`).
2. **Edit `config.json`**
   - A default `config.json` lives in the root of the repo—the top-level folder
     containing this README. Update it with the TikTok usernames you want to
     track and your notification details.
   - The password and auth token fields may contain placeholders such as
     `${GMAIL_PASSWORD}`. These will be replaced by environment variables from
     GitHub Secrets when the workflow runs.
3. **Add secrets** in your GitHub repository settings:
   - Open your fork, then go to **Settings → Secrets and variables → Actions**.
   - Create secrets named `GMAIL_PASSWORD` and `TWILIO_AUTH_TOKEN` with your
     credentials.
4. **Enable GitHub Actions** in your fork. Visit the **Actions** tab and, if
   prompted, click **Enable** to allow workflows to run. The included workflow
   `.github/workflows/tiktok_notifier.yml` runs every 15 minutes by default.
5. **Check the Actions tab** to see logs and confirm notifications are being sent.

## Configuration File

`config.json` controls which users are monitored and how notifications are sent. Example:

```json
{
  "usernames": ["example_user", "another_user"],
  "email": {
    "enabled": true,
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "address": "you@example.com",
    "password": "${GMAIL_PASSWORD}",
    "to": "you@example.com"
  },
  "twilio": {
    "enabled": false,
    "account_sid": "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "auth_token": "${TWILIO_AUTH_TOKEN}",
    "from_number": "+1234567890",
    "to_number": "+1234567890"
  }
}
```

- Set `enabled` to `true` for any notification method you want to use.
- Any values in the form `${VAR_NAME}` will be expanded from environment variables, so the GitHub Action can supply your secret credentials securely.
- `usernames` accepts one or many TikTok usernames.

## How It Works

1. The GitHub Action installs Python dependencies and runs `tiktok_notifier.py`.
2. The script scrapes each TikTok profile for video links.
3. Any new links since the last run are stored in the `data/` directory and committed back to the repository.
4. If new posts are found, a single email/SMS notification is sent summarizing all of them.
5. If a profile is private or cannot be fetched, the action fails and you can view the error in the Actions logs.

## Customization

- **Change the schedule:** Edit the `cron` line in `.github/workflows/tiktok_notifier.yml` to run more or less frequently.
- **Add or remove usernames:** Update the `usernames` list in `config.json`.
- **Switch notification methods:** Toggle the `enabled` flags or adjust credentials in `config.json`.

## Updating Seen Data

The script keeps JSON files under the `data/` directory (one per username) containing the links it has already reported. These files are automatically committed by the GitHub Action after each run. If you want to reset the history, simply delete the corresponding file(s) and commit the deletion.

## Troubleshooting

- **No notifications?** Check the Actions logs for errors. Make sure your credentials are correct and that the profile is public.
- **Need to change credentials?** Update them in `config.json` and, if using secrets, in your repository settings.
- **Disable SMS or email:** Set the appropriate `enabled` field to `false` in `config.json`.

## Manual Testing Locally

You can run the script locally with Python 3:

```bash
pip install requests beautifulsoup4 twilio
python tiktok_notifier.py
```

Make sure `config.json` exists in the project root when testing locally.

