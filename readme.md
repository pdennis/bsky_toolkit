# Bluesky Toolkit

A collection of utility scripts for managing your Bluesky social network. These tools help automate common social networking tasks while respecting rate limits.

## Scripts

### 1. Non-Mutual Unfollower (`unfollow.py`)
Identifies and unfollows accounts that don't follow you back.

Features:
- Lists all non-mutual follows
- Safely unfollows with rate limiting
- Shows progress during operation
- Uses 3.5 second delays between actions to respect rate limits

### 2. Friend Follower (`follow.py`)
Helps you connect with friends-of-friends by following the followers of a specified account.

Features:
- Takes a friend's handle as input
- Skips accounts you already follow
- Shows progress during operation
- Uses 6 second delays between actions to respect rate limits

## Prerequisites

```bash
pip install atproto
```

## Usage

1. Clone this repository:
```bash
git clone https://github.com/yourusername/bsky-toolkit
cd bsky-toolkit
```

2. Edit either script to add your Bluesky credentials:
```python
manager = BlueskyFollowerManager("your.email@example.com", "your-password")
```

3. Run the scripts:

For unfollowing non-mutual follows:
```bash
python unfollow.py
```

For following friends' followers:
```bash
python follow.py
# You'll be prompted to enter a friend's handle
```

## Important Notes

- These scripts use conservative rate limiting to avoid overwhelming the Bluesky API
- The unfollower script can take several hours to complete if you have many non-mutual follows
- It's recommended to run these scripts during times when you won't need to use your account
- Consider backing up your follow list before using the unfollow script

## Rate Limits

- Unfollow script: 3.5 second delay between operations
- Follow script: 6 second delay between operations

These limits can be adjusted by modifying the `time.sleep()` values in the scripts.

