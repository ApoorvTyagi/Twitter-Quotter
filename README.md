# Twitter-Quotter
Version 3.0

# System Design X profile

An AI-powered X profile that automatically posts comprehensive threads about system design concepts.

Perfect for engineers preparing for **system design interviews**! 🚀

## ✨ Features

- 🧵 **Smart Threading**: Creates 3-9 tweet threads based on topic complexity
- 🎲 **Random Scheduling**: Posts once daily between 7-11 PM IST at random times
- 🧠 **AI-Powered**: Uses GPT-4o-mini to generate fresh, engaging content
- 📊 **Quality Validation**: AI validates thread quality before posting
- 🔄 **Auto-Cycling**: Tracks posted topics and brings fresh perspectives on repeats
- 🎯 **Interview-Focused**: Emphasizes trade-offs, real-world examples, and practical insights

## 📖 What Gets Posted

Threads cover **70+ system design topics** including:

### Part I: Foundations
- Reliability, Scalability, Maintainability
- Data models (Relational, Document, Graph)
- Storage engines (B-trees, LSM-trees)
- OLTP vs OLAP systems

### Part II: Distributed Data
- Replication (Leader-based, Multi-leader, Leaderless)
- Partitioning strategies
- Transactions and isolation levels
- Distributed consensus (Raft, Paxos)

### Part III: Derived Data
- Batch processing (MapReduce)
- Stream processing (Kafka, Flink)
- Lambda vs Kappa architecture
- Consistency and consensus

## 🎯 Thread Structure

Each thread follows this interview-optimized format:

1. **Hook** (Tweet 1): Real-world problem or scenario
2. **Core Concept** (Tweets 2-3): Deep explanation of how it works
3. **Technical Details** (Tweets 4-6): Implementation, algorithms, trade-offs
4. **Interview Gold** (Tweets 7+): 
   - Detailed trade-off analysis
   - When to use vs not use
   - Real company examples (Netflix, Uber, Amazon)
   - Common mistakes and pitfalls
   - Only hashtag: `#SystemDesign` in final tweet

## 🚀 Setup Guide

### Prerequisites

- Python 3.11+
- X Developer Account with API access
- OpenAI API key
- GitHub account

### 1. Clone the Repository

```bash
git clone https://github.com/ApoorvTyagi/Twitter-Quotter
cd Twitter-Quotter
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Get API Credentials

#### Twitter API (X API)
1. Go to [X Developer Portal](https://developer.twitter.com/en/portal/dashboard)
2. Create a project and app
3. Set permissions to **"Read and Write"**
4. Generate:
   - API Key & Secret
   - Access Token & Secret
5. Important: Regenerate Access Token after setting permissions!

#### OpenAI API
1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create a new API key
3. Copy and save it securely

### 4. Configure GitHub Secrets

Go to your repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add these 5 secrets:

| Secret Name | Description |
|------------|-------------|
| `TWITTER_API_KEY` | Your X API Key |
| `TWITTER_API_SECRET` | Your X API Secret |
| `TWITTER_ACCESS_TOKEN` | Your X Access Token |
| `TWITTER_ACCESS_TOKEN_SECRET` | Your X Access Token Secret |
| `OPENAI_API_KEY` | Your OpenAI API Key |

### 5. Enable Workflow Permissions

1. Go to **Settings** → **Actions** → **General**
2. Under "Workflow permissions":
   - ☑️ Select **"Read and write permissions"**
   - ☑️ Check **"Allow GitHub Actions to create and approve pull requests"**
3. Click **Save**

### 6. Deploy

```bash
git add .
git commit -m "🚀 Deploy DDIA"
git push origin main
```

That's it! The code will automatically post between 7-11 PM IST daily. 🎉

## 🧪 Testing

### Test Locally

Create a `.env` file:

```env
TWITTER_API_KEY=your_key_here
TWITTER_API_SECRET=your_secret_here
TWITTER_ACCESS_TOKEN=your_token_here
TWITTER_ACCESS_TOKEN_SECRET=your_token_secret_here
OPENAI_API_KEY=your_openai_key_here
```

Run the code:

```bash
python DDIA.py
```

### Test on GitHub Actions

1. Go to **Actions** tab in your repo
2. Click **"DDIA - Random Time Daily"**
3. Click **"Run workflow"** → **"Run workflow"**
4. Watch it execute in real-time!

## 📊 Monitoring

### View Workflow Runs

- **Actions tab**: See all executions, success/failures
- **Click any run**: View detailed logs including:
  - Random post time calculated
  - Generated tweet content
  - Posting progress
  - Success confirmation

### Workflow Summary

Each run shows:
```
📊 Workflow Summary
- Scheduled Time: 7:00 PM IST
- Actual Post Time: 9:23 PM IST
- Status: Success
- Topics Posted: 15/70
```

### Check X

Simply visit your X profile to see the posted threads!

## ⚙️ Configuration

### Change Posting Time Window

Edit `.github/workflows/ddia-bot-random.yml`:

```yaml
# Current: 7-11 PM IST (4-hour window)
RANDOM_DELAY=$((RANDOM % 14400))

# 8-10 PM IST (2-hour window)
- cron: '30 14 * * *'  # Start at 8 PM IST
RANDOM_DELAY=$((RANDOM % 7200))
```

### Change Thread Complexity

Edit `DDIA.py` - modify `thread_lengths` in `generate_comprehensive_thread()`:

```python
thread_lengths = {
    "simple": "3-4",    # Change to "2-3" for shorter
    "medium": "5-6",    # Change to "4-5" for shorter
    "complex": "7-9"    # Change to "6-8" for shorter
}
```

### Add More Topics

Edit `DDIA_TOPICS` dictionary in `DDIA.py`:

```python
"medium": [
    "Your new topic here",
    "Another topic",
    # ... existing topics
]
```

### Adjust Delay Between Tweets

In `post_thread()` method:

```python
# Current: 60 seconds in GitHub Actions
delay_seconds = 60 if os.getenv("GITHUB_ACTIONS") else 5

# Change to 30 seconds:
delay_seconds = 30 if os.getenv("GITHUB_ACTIONS") else 5
```

## 📁 Project Structure

```
Twitter-Quotter/
├── .github/
│   └── workflows/
│       └── ddia-bot-random.yml    # GitHub Actions workflow
├── DDIA.py                        # Main code
├── requirements.txt               # Python dependencies
├── posted_topics.json             # Auto-generated topic tracker
├── .gitignore                     # Git ignore rules
└── README.md                      # This file
```

## 🔧 How It Works

### Daily Execution Flow

```
7:00 PM IST → GitHub Actions triggers workflow
                ↓
              Calculate random delay (0-4 hours)
                ↓
              Wait for calculated time
                ↓
7:00-11:00 PM → Select random unused topic
                ↓
              Generate thread with GPT-4o-mini
                ↓
              Validate thread quality (must score 8+/10)
                ↓
              Post thread to X (60s delay between tweets)
                ↓
              Update posted_topics.json
                ↓
              Commit and push changes
                ↓
              Done! Wait until tomorrow 7 PM
```

### Topic Cycling

1. It tracks posted topics in `posted_topics.json`
2. Only selects from unused topics
3. When all 70+ topics are covered → clears file
4. Next cycle brings **fresh perspectives**:
   - Different angles
   - New examples
   - Deeper technical details
   - Alternative explanations

### Quality Control

Each thread is validated before posting:
- ✅ Technical depth check
- ✅ Trade-off analysis verification
- ✅ Real-world examples present
- ✅ Interview-readiness score
- ✅ Proper hashtag placement

Only threads scoring 8+/10 are posted!

## 💰 Cost Breakdown

### GitHub Actions
- **Free tier**: 2,000 minutes/month
- **Usage**: ~150-240 minutes/month
- **Cost**: **$0** (FREE) ✅

### OpenAI API
- **Per thread**: ~$0.015 (generation + validation)
- **Daily**: $0.015
- **Monthly**: ~$0.45
- **Cost**: **Less than 50 cents/month** ✅

### Total Monthly Cost: **~$0.45** 🎉

## 🐛 Troubleshooting

### Profile doesn't post

**Check:**
- ✅ All 5 secrets are added correctly
- ✅ No typos in secret names
- ✅ Workflow permissions enabled
- ✅ Check Actions tab for error logs

### 403 Forbidden Error

**Fix:**
1. Verify X app has "Read and Write" permissions
2. Regenerate Access Token & Secret **after** changing permissions
3. Update GitHub secrets with new tokens

### 429 Rate Limit Error

**Fix:**
- Increase delay in `post_thread()` method
- Default is 60 seconds, try 90 or 120

### posted_topics.json not updating

**Fix:**
- Enable "Read and write permissions" in Settings → Actions
- Check commit step in workflow logs

### Thread quality too low / keeps regenerating

**Fix:**
- Lower threshold from 8 to 7 in `validate_thread_quality()`
- Or improve the generation prompt

## 📈 Best Practices

1. **Monitor First Week**
   - Check logs daily
   - Verify tweet quality
   - Watch for errors

2. **Track Engagement**
   - Note which topics get more engagement
   - Adjust complexity/length if needed

3. **Security**
   - Never commit secrets to code
   - Keep API keys secure
   - Regenerate if exposed

4. **Content Quality**
   - Review generated threads occasionally
   - Refine prompts if needed
   - Maintain technical accuracy

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

MIT License - feel free to use and modify!

## 🙏 Acknowledgments

- **Martin Klempmann** for writing "Designing Data-Intensive Applications"

## 📞 Support

- **Issues**: Open an issue on GitHub
- **Questions**: Check the workflow logs first
- **Contributions**: PRs are welcome!

## 🌟 Star This Repo!

If this profile helps you with system design interview prep, give it a ⭐!

---

**Happy Learning! 🚀**

Built with ❤️ for engineers preparing for system design interviews.
