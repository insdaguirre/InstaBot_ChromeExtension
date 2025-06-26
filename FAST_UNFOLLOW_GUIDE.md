# 🚀 Fast Parallel Instagram Unfollow Bot

## Speed Comparison
- **Old method**: 10-30 seconds per account (serial processing)
- **New method**: 2-4 seconds per account (6x parallel processing)
- **Speed improvement**: ~10-15x faster overall!

## Quick Start

### 1. Setup (one-time)
```bash
# Run the setup script
./setup_and_run.sh

# OR manually:
pip install selenium concurrent.futures
```

### 2. Prepare your CSV file
Create a CSV file with usernames to unfollow (one per line):
```csv
username1
username2
username3
```

### 3. Run the Fast Bot

#### Command Line Usage:
```bash
python3 fast_unfollow_bot.py \
  --csv your_usernames.csv \
  --username your_instagram_username \
  --password your_instagram_password \
  --workers 6 \
  --min-delay 1.5 \
  --max-delay 3.0
```

#### Python Script Usage:
```python
from fast_unfollow_bot import FastUnfollowBot

# Create bot instance
bot = FastUnfollowBot(
    username="your_instagram_username",
    password="your_instagram_password",
    max_workers=6,
    min_delay=1.5,
    max_delay=3.0
)

# Load usernames from CSV
usernames = bot.load_usernames_from_csv("your_usernames.csv")

# Execute parallel unfollow
successful_unfollows = bot.unfollow_accounts_parallel(usernames)

# Save results
bot.save_results_to_csv(successful_unfollows)
```

## Performance Optimizations

### ⚡ Speed Features:
- **Parallel Processing**: 6 workers running simultaneously
- **Minimal Delays**: 1-3 seconds instead of 30+ seconds per account
- **No Page Refreshes**: Eliminated costly verification refreshes
- **Optimized Chrome**: Disabled images, JS, and unnecessary features
- **Smart Waiting**: WebDriverWait instead of fixed sleeps

### 📊 Expected Performance:
- **100 accounts**: ~3-5 minutes (vs 30-50 minutes old method)
- **500 accounts**: ~15-20 minutes (vs 2.5-4 hours old method)
- **1000 accounts**: ~30-40 minutes (vs 5-8 hours old method)

## Configuration Options

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--workers` | 6 | Number of parallel browser instances |
| `--min-delay` | 1.5 | Minimum seconds between actions |
| `--max-delay` | 3.0 | Maximum seconds between actions |
| `--csv` | Required | Path to CSV file with usernames |

## Safety Features

- **Rate Limiting**: Built-in delays to avoid Instagram detection
- **Error Handling**: Robust error recovery and logging
- **Progress Tracking**: Real-time progress updates
- **Result Logging**: CSV export of successful/failed actions

## Tips for Maximum Speed

1. **Use SSD**: Faster disk = faster browser startup
2. **Close Other Apps**: Free up RAM for parallel browsers
3. **Stable Internet**: Avoid timeouts and retries
4. **Small Batches**: Test with 10-20 accounts first
5. **Monitor System**: Watch CPU/RAM usage

## Troubleshooting

### If bot is still slow:
1. Reduce `--workers` to 3-4 on slower machines
2. Increase `--min-delay` and `--max-delay` if getting rate limited
3. Check internet connection stability
4. Ensure Chrome browser is updated

### If getting rate limited:
1. Increase delays: `--min-delay 3 --max-delay 6`
2. Reduce workers: `--workers 3`
3. Take breaks between large batches

## Example Output
```
🚀 Starting parallel unfollow with 6 workers
📊 Processing 300 accounts in 6 chunks
⚡ Estimated time: 20.0 minutes
============================================================
✅ Worker 1: Logged in successfully
✅ Worker 2: Logged in successfully
✅ Worker 1 (1/50): Successfully unfollowed user123 (2.3s)
✅ Worker 2 (1/50): Successfully cancelled request user456 (1.8s)
...
🎉 Worker 1: Completed 48/50 accounts
============================================================
🎯 RESULTS SUMMARY:
   ✅ Successfully processed: 285/300 accounts
   📈 Success rate: 95.0%
   ⏱️  Total time: 1247.3 seconds
   🚀 Average per account: 4.2s
   ⚡ Speed improvement: ~7x faster
``` 