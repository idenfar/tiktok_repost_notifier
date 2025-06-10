# TikTok Repost Notifier

This project checks one or more public TikTok profiles for new videos and sends you an email and/or SMS message when new posts appear. It runs automatically on GitHub Actions every 15 minutes.

## Features

- Monitor multiple TikTok usernames.
- Send notifications via Gmail SMTP and/or Twilio SMS.
- Keeps track of posts already reported so you are only notified once.
- Works entirely through GitHub Actions (no need to run anything locally).

## Quick Start

1. **Fork this repository** to your own GitHub account.
2. **Create `config.json`**
   - Copy `config_template.json` to `config.json` in the root of the repo.
   - Fill in the usernames you want to track and your email/Twilio credentials.
3. **Add secrets** in your GitHub repository settings:
   - `GMAIL_PASSWORD` – your email/app password.
   - `TWILIO_AUTH_TOKEN` – Twilio auth token (if using SMS).
4. **Enable GitHub Actions** in your fork. The workflow is already defined in `.github/workflows/tiktok_notifier.yml` and will run every 15 minutes.
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
    "password": "${{ secrets.GMAIL_PASSWORD }}",
    "to": "you@example.com"
  },
  "twilio": {
    "enabled": false,
    "account_sid": "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "auth_token": "${{ secrets.TWILIO_AUTH_TOKEN }}",
    "from_number": "+1234567890",
    "to_number": "+1234567890"
  }
}
```

- Set `enabled` to `true` for any notification method you want to use.
- The script reads the password and auth token values from the JSON, so you may reference GitHub Secrets using the `${{ secrets.NAME }}` syntax or place the plain values directly (not recommended).
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

