# Deploying to Heroku

This guide will help you deploy the Telegram Leech Bot to Heroku.

## Prerequisites

- A [Heroku account](https://signup.heroku.com/)
- [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) installed (optional, for manual deployment)
- Your Telegram Bot Token from [@BotFather](https://t.me/BotFather)

## Method 1: Deploy with Heroku Button (Easiest)

Click the button below to deploy directly to Heroku:

[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

This will:
1. Create a new Heroku app
2. Install all required dependencies (Python, aria2, ffmpeg)
3. Prompt you to enter your bot token and other configuration
4. Deploy and start the bot automatically

**Configuration:**
- `BOT_TOKEN`: Your bot token from @BotFather (required)
- `AUTHORIZED_USERS`: Comma-separated user IDs (optional, leave empty to allow all users)

## Method 2: Manual Deployment via Heroku CLI

### 1. Clone the repository

```bash
git clone https://github.com/RecklessEvadingDriver/Leechrepo.git
cd Leechrepo
```

### 2. Login to Heroku

```bash
heroku login
```

### 3. Create a new Heroku app

```bash
heroku create your-leech-bot-name
```

Or use an existing app:

```bash
heroku git:remote -a your-existing-app-name
```

### 4. Add buildpacks

The app needs multiple buildpacks for Python, apt packages, and ffmpeg:

```bash
heroku buildpacks:add heroku-community/apt
heroku buildpacks:add heroku/python
heroku buildpacks:add https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git
```

### 5. Set environment variables

Set your bot token and other configuration:

```bash
heroku config:set BOT_TOKEN="your_bot_token_here"
heroku config:set AUTHORIZED_USERS="123456789,987654321"  # Optional
```

Optional configuration:

```bash
heroku config:set DOWNLOAD_DIR="./downloads"
heroku config:set MAX_DOWNLOAD_SIZE="2147483648"
heroku config:set ARIA2_HOST="localhost"
heroku config:set ARIA2_PORT="6800"
```

### 6. Deploy the app

```bash
git push heroku main
```

Or if you're on a different branch:

```bash
git push heroku copilot/add-telegram-leech-bot:main
```

### 7. Scale the web dyno

```bash
heroku ps:scale web=1
```

### 8. Check logs

```bash
heroku logs --tail
```

You should see:
```
✅ Bot is running! Press Ctrl+C to stop.
```

## Method 3: Deploy via GitHub Integration

1. Go to your Heroku dashboard
2. Create a new app or select an existing one
3. Go to the "Deploy" tab
4. Connect to your GitHub repository
5. Enable automatic deploys (optional)
6. Click "Deploy Branch"
7. Go to "Settings" tab
8. Click "Reveal Config Vars"
9. Add your `BOT_TOKEN` and other configuration

## Verifying Deployment

1. Check the logs:
   ```bash
   heroku logs --tail
   ```

2. Open Telegram and search for your bot
3. Send `/start` to test if it's working
4. Try downloading a file:
   ```
   /leech https://sample-videos.com/video321/mp4/720/big_buck_bunny_720p_1mb.mp4
   ```

## Troubleshooting

### Bot not responding

**Check logs:**
```bash
heroku logs --tail
```

**Restart the dyno:**
```bash
heroku restart
```

**Verify config vars:**
```bash
heroku config
```

Make sure `BOT_TOKEN` is set correctly.

### aria2 not found

The `Aptfile` should automatically install aria2. If it's not working:

1. Check buildpacks are in the correct order:
   ```bash
   heroku buildpacks
   ```
   
   Should show:
   ```
   1. heroku-community/apt
   2. heroku/python
   3. https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git
   ```

2. If needed, clear buildpacks and re-add:
   ```bash
   heroku buildpacks:clear
   heroku buildpacks:add heroku-community/apt
   heroku buildpacks:add heroku/python
   heroku buildpacks:add https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git
   ```

3. Redeploy:
   ```bash
   git commit --allow-empty -m "Rebuild with buildpacks"
   git push heroku main
   ```

### Download fails

Check the download directory:
```bash
heroku config:set DOWNLOAD_DIR="./downloads"
```

### Out of memory

Heroku free dynos have limited RAM (512MB). For large files:

1. Upgrade to a paid dyno with more memory
2. Set a lower `MAX_DOWNLOAD_SIZE`
3. Download smaller files

### Connection timeout

Heroku has a 30-second request timeout. For large downloads:
- The bot handles this by using async downloads
- Make sure aria2 is running (check logs)

## Free Tier Limitations

Heroku free dynos have some limitations:

- **Sleep after 30 minutes of inactivity**: The bot will stop after 30 minutes without requests
- **550 free dyno hours per month**: Approximately 23 days of uptime
- **512MB RAM**: Limited memory for large downloads
- **Ephemeral filesystem**: Downloaded files are deleted when dyno restarts

**Recommendations:**
- Use a paid dyno for 24/7 uptime
- Set `MAX_DOWNLOAD_SIZE` appropriately for your dyno tier
- Consider using external storage (S3, Google Drive) for persistent downloads

## Upgrading Your Dyno

For better performance and no sleep:

```bash
heroku ps:type hobby
```

Hobby dynos ($7/month):
- Never sleep
- 512MB RAM
- More consistent performance

## Environment Variables Reference

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `BOT_TOKEN` | Telegram bot token | - | Yes |
| `AUTHORIZED_USERS` | Comma-separated user IDs | All users | No |
| `DOWNLOAD_DIR` | Download directory | `./downloads` | No |
| `MAX_DOWNLOAD_SIZE` | Max file size in bytes | `2147483648` (2GB) | No |
| `ARIA2_HOST` | Aria2 RPC host | `localhost` | No |
| `ARIA2_PORT` | Aria2 RPC port | `6800` | No |

## Monitoring

View real-time logs:
```bash
heroku logs --tail
```

Check dyno status:
```bash
heroku ps
```

## Updating the Bot

When you push changes to your repository:

**If using GitHub integration:**
- Changes are deployed automatically if auto-deploy is enabled

**If using Heroku CLI:**
```bash
git pull origin main
git push heroku main
```

## Support

If you encounter issues:

1. Check the logs: `heroku logs --tail`
2. Verify configuration: `heroku config`
3. Restart the dyno: `heroku restart`
4. Check the [main README](README.md) for general troubleshooting
5. Open an issue on GitHub

## Additional Resources

- [Heroku Python Documentation](https://devcenter.heroku.com/articles/getting-started-with-python)
- [Heroku Buildpacks](https://devcenter.heroku.com/articles/buildpacks)
- [Heroku Config Vars](https://devcenter.heroku.com/articles/config-vars)
- [Heroku Logs](https://devcenter.heroku.com/articles/logging)
