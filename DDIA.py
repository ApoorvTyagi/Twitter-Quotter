import tweepy
import openai
import time
import schedule
from datetime import datetime
import json
import random
import os
from dotenv import load_dotenv

import os

TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


# load_dotenv()

# TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
# TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
# TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
# TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI
openai.api_key = OPENAI_API_KEY

DDIA_TOPICS = {
    # Simple concepts (2-3 tweets)
    "simple": [
        "Hash indexes and SSTables",
        "Column-oriented storage",
        "Write-ahead logging (WAL)",
        "Bloom filters in databases",
        "Request routing in distributed systems",
    ],
    
    # Medium concepts (4-5 tweets)
    "medium": [
        "Reliability in distributed systems",
        "Scalability and performance metrics",
        "B-trees vs LSM-trees trade-offs",
        "Leader-based replication",
        "Partitioning strategies",
        "Replication lag and consistency",
        "Read committed isolation",
        "Snapshot isolation and repeatable read",
        "Message brokers and event logs",
        "Kafka and log-based message brokers",
        "Stream processing concepts",
        "Batch processing fundamentals",
        "MapReduce and distributed filesystems",
    ],
    
    # Complex concepts (6-8 tweets)
    "complex": [
        "Multi-leader replication conflicts",
        "Leaderless replication and quorums",
        "Transactions and ACID properties",
        "Weak isolation levels",
        "Write skew and phantoms",
        "Serializability",
        "Two-phase locking",
        "Serializable snapshot isolation",
        "Two-phase commit protocol",
        "Distributed consensus algorithms",
        "Raft consensus algorithm",
        "Linearizability guarantees",
        "CAP theorem explained",
        "Lambda vs Kappa architecture",
        "Stream joins and windowing",
        "Fault tolerance in stream processing",
    ]
}

class AISystemDesignBot:
    def __init__(self):
        """Initialize the bot with Twitter and OpenAI clients"""
        print("🔧 Initializing bot...")
        
        # Validate credentials
        if not all([TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, 
                   TWITTER_ACCESS_TOKEN_SECRET]):
            raise ValueError("Missing Twitter API credentials in .env file")
        
        if not OPENAI_API_KEY:
            raise ValueError("Missing OpenAI API key in .env file")
        
        # Initialize Twitter client
        try:
            self.twitter_client = tweepy.Client(
                consumer_key=TWITTER_API_KEY,
                consumer_secret=TWITTER_API_SECRET,
                access_token=TWITTER_ACCESS_TOKEN,
                access_token_secret=TWITTER_ACCESS_TOKEN_SECRET
            )
            
            me = self.twitter_client.get_me()
            print(f"✅ Authenticated as: @{me.data.username}")
            
        except Exception as e:
            print(f"❌ Authentication failed: {e}")
            raise
        
        self.posted_topics = self.load_posted_topics()
        print(f"📊 Previously posted topics: {len(self.posted_topics)}")
        
    def load_posted_topics(self):
        """Load previously posted topics from file"""
        try:
            with open('posted_topics.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def save_posted_topics(self):
        """Save posted topics to file"""
        with open('posted_topics.json', 'w') as f:
            json.dump(self.posted_topics, f, indent=2)
    
    def get_topic_complexity(self, topic):
        """Determine complexity level of topic"""
        for complexity, topics in DDIA_TOPICS.items():
            if topic in topics:
                return complexity
        return "medium"  # default
    
    def generate_comprehensive_thread(self, topic, complexity):
        """Generate a comprehensive thread optimized for system design interviews"""
        
        # Set thread length based on complexity
        thread_lengths = {
            "simple": "3-4",
            "medium": "5-6", 
            "complex": "7-9"
        }
        target_length = thread_lengths.get(complexity, "5-6")
        
        # Check if this is a repeated topic to add novelty
        cycle_number = self.posted_topics.count(topic) + 1
        novelty_instruction = ""
        if cycle_number > 1:
            novelty_instruction = f"\nNOTE: This is cycle {cycle_number} for this topic. Bring FRESH perspective: different examples, alternative angles, or deeper technical details than typical explanations."
        
        prompt = f"""You are a system design interview coach and expert on "Designing Data-Intensive Applications" by Martin Klempmann.

Create a comprehensive Twitter thread about: "{topic}"{novelty_instruction}

This thread is for engineers preparing for system design interviews at FAANG companies. Make it interview-focused and GO DEEP into concepts and trade-offs.

THREAD STRUCTURE ({target_length} tweets):

Tweet 1 (Hook):
- Start with a relatable problem or real production scenario
- Why this concept matters in actual distributed systems
- Use an emoji to grab attention
- NO hashtags here

Tweet 2-3 (Core Concept - GO DEEP):
- Explain the fundamental mechanism
- Don't just describe WHAT it is, explain HOW it actually works under the hood
- Use technical precision while remaining clear
- NO hashtags

Tweet 4-6 (Technical Deep Dive - THIS IS CRITICAL):
- Implementation details and internal mechanisms
- Include concrete examples with numbers/metrics
- Show the actual algorithms or data structures involved
- Memory/CPU/Network implications
- NO hashtags

Tweet 7+ (Trade-offs Analysis - INTERVIEW GOLD):
- DETAILED trade-offs (CAP theorem implications, consistency vs availability, etc.)
- When to use vs when NOT to use (be specific about scenarios)
- Real production examples: "Netflix does X because Y, but Uber does Z because W"
- Performance characteristics (Big O, throughput, latency numbers)
- Failure modes and edge cases
- Common mistakes that cause production incidents
- NO hashtags

Final Tweet:
- Powerful key takeaway or interview insight
- ONLY in this tweet add: #SystemDesign and no other hashtags

CRITICAL REQUIREMENTS:
- Each tweet MUST be less than or equal to 280 characters
- Go DEEP on technical details and trade-offs (this is not for beginners)
- Include specific metrics, algorithms, or quantifiable trade-offs
- Focus heavily on WHY certain decisions are made
- Explain the COST of trade-offs (what you lose when you choose X)
- Use real company examples with specifics
- Make every tweet dense with information
- Use emojis strategically (1-2 per tweet max)
- ONLY add #SystemDesign to the final tweet, NO hashtags in other tweets

Return ONLY valid JSON array of tweet strings:
["tweet1", "tweet2", "tweet3", ...]"""

        try:
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert system design interviewer and educator. You explain concepts with perfect clarity, always focusing on trade-offs and real-world applicability. You write engaging, Twitter-friendly content that engineers love."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content.strip()
            
            # Remove markdown code blocks if present
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            elif content.startswith("```"):
                content = content.replace("```", "").strip()
            
            # Parse JSON
            tweets = json.loads(content)
            
            # Validate each tweet length
            validated_tweets = []
            for i, tweet in enumerate(tweets):
                if len(tweet) > 280:
                    print(f"⚠️ Tweet {i+1} too long ({len(tweet)} chars), trimming...")
                    tweet = tweet[:277] + "..."
                validated_tweets.append(tweet)
            
            return validated_tweets
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
            print(f"Raw response: {content[:200]}...")
            return None
        except Exception as e:
            print(f"❌ Error generating thread: {str(e)}")
            return None
    
    def validate_thread_quality(self, tweets, topic):
        """Use AI to validate if thread is comprehensive enough"""
        
        thread_text = "\n\n".join([f"Tweet {i+1}: {t}" for i, t in enumerate(tweets)])
        
        validation_prompt = f"""You are reviewing a Twitter thread about "{topic}" for system design interview preparation.

Thread content:
{thread_text}

Rate this thread on a STRICT scale:

1. Technical Depth (does it go beyond surface level?)
2. Trade-offs Analysis (are trade-offs explained in detail?)
3. Real-world applicability (concrete examples with specifics?)
4. Interview-readiness (would this help in a FAANG interview?)

Respond in JSON format:
{{
    "score": 1-10,
    "is_good": true/false,
    "missing": ["what could be deeper"],
    "feedback": "2-3 sentences of actionable feedback"
}}

Score >= 6 means post it.
Score < 6 means regenerate."""

        try:
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a strict technical content reviewer who values depth and precision over simplicity."},
                    {"role": "user", "content": validation_prompt}
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            result = response.choices[0].message.content.strip()
            if result.startswith("```json"):
                result = result.replace("```json", "").replace("```", "").strip()
            
            validation = json.loads(result)
            return validation
            
        except Exception as e:
            print(f"⚠️ Validation error: {e}")
            # If validation fails, assume it's good enough
            return {"score": 8, "is_good": True, "feedback": "Validation skipped"}
    
    def post_thread(self, tweets):
        """Post a Twitter thread with rate limit handling"""
        try:
            previous_tweet_id = None
            posted_ids = []
            
            # Determine delay based on environment
            delay_seconds = 60 if os.getenv("GITHUB_ACTIONS") else 5
            
            for i, tweet_text in enumerate(tweets):
                # Add thread numbering to first tweet
                if i == 0:
                    tweet_text = f"🧵 Thread: {tweet_text}"
                
                try:
                    if previous_tweet_id:
                        response = self.twitter_client.create_tweet(
                            text=tweet_text,
                            in_reply_to_tweet_id=previous_tweet_id
                        )
                    else:
                        response = self.twitter_client.create_tweet(text=tweet_text)
                    
                    previous_tweet_id = response.data['id']
                    posted_ids.append(previous_tweet_id)
                    print(f"✅ Thread tweet {i+1}/{len(tweets)} posted!")
                    
                    # Delay between tweets to avoid rate limits
                    if i < len(tweets) - 1:
                        env_name = "GitHub Actions" if os.getenv("GITHUB_ACTIONS") else "Local"
                        print(f"⏳ Waiting {delay_seconds} seconds before next tweet ({env_name} mode)...")
                        time.sleep(delay_seconds)
                
                except tweepy.TooManyRequests as e:
                    print(f"⚠️ Rate limit hit on tweet {i+1}. Waiting 90 seconds...")
                    time.sleep(90)
                    # Retry once
                    try:
                        if previous_tweet_id:
                            response = self.twitter_client.create_tweet(
                                text=tweet_text,
                                in_reply_to_tweet_id=previous_tweet_id
                            )
                        else:
                            response = self.twitter_client.create_tweet(text=tweet_text)
                        
                        previous_tweet_id = response.data['id']
                        posted_ids.append(previous_tweet_id)
                        print(f"✅ Thread tweet {i+1}/{len(tweets)} posted (after retry)!")
                        
                        if i < len(tweets) - 1:
                            print(f"⏳ Waiting {delay_seconds} seconds before next tweet...")
                            time.sleep(delay_seconds)
                    except Exception as retry_error:
                        print(f"❌ Failed to post tweet {i+1} even after retry: {retry_error}")
                        raise
            
            return posted_ids
            
        except Exception as e:
            print(f"❌ Error posting thread: {str(e)}")
            return None
    
    def create_and_post(self):
        """Main method to generate and post content"""
        try:
            # Get all topics
            all_topics = []
            for complexity, topics in DDIA_TOPICS.items():
                all_topics.extend(topics)
            
            # Check if all topics used - clear and restart with novelty
            if len(self.posted_topics) >= len(all_topics):
                print("\n" + "=" * 70)
                print("🔄 ALL TOPICS COVERED! Starting fresh cycle with NEW perspectives")
                print("=" * 70)
                # Clear the posted topics file to allow re-posting with novelty
                self.posted_topics = []
                self.save_posted_topics()
                print("✅ Posted topics cleared. Next threads will bring fresh angles!\n")
            
            # Select random unused topic
            available_topics = [t for t in all_topics if t not in self.posted_topics]
            topic = random.choice(available_topics)
            complexity = self.get_topic_complexity(topic)
            
            # Check cycle number for this specific topic
            cycle_info = ""
            if topic in self.posted_topics:
                cycle_num = self.posted_topics.count(topic) + 1
                cycle_info = f" (Cycle {cycle_num} - Fresh perspective!)"
            
            print(f"\n📚 Selected topic: {topic}{cycle_info}")
            print(f"📊 Complexity: {complexity.upper()}")
            print(f"⏳ Generating comprehensive thread with AI...")
            
            # Generate thread
            tweets = self.generate_comprehensive_thread(topic, complexity)
            
            if not tweets:
                print("❌ Failed to generate thread")
                return False
            
            print(f"\n📝 Generated thread ({len(tweets)} tweets):")
            print("=" * 70)
            for i, tweet in enumerate(tweets):
                # Show hashtag indicator
                has_hashtag = "#SystemDesign" in tweet
                hashtag_indicator = " [#️⃣ HAS HASHTAG]" if has_hashtag else ""
                print(f"\n[Tweet {i+1}/{len(tweets)}] ({len(tweet)} chars){hashtag_indicator}")
                print(tweet)
                print("-" * 70)
            
            # Validate quality
            print("\n🔍 Validating thread quality...")
            validation = self.validate_thread_quality(tweets, topic)
            print(f"📈 Quality Score: {validation['score']}/10")
            print(f"💬 Feedback: {validation.get('feedback', 'N/A')}")
            
            if not validation.get('is_good', True):
                print("⚠️ Thread quality below threshold. Regenerating...")
                return False
            
            # Post thread
            print(f"\n🚀 Posting thread to Twitter...")
            posted_ids = self.post_thread(tweets)
            
            if posted_ids:
                self.posted_topics.append(topic)
                self.save_posted_topics()
                
                print(f"\n✨ Success!")
                print(f"🔗 Thread URL: https://twitter.com/user/status/{posted_ids[0]}")
                print(f"📊 Progress: {len(self.posted_topics)}/{len(all_topics)} topics covered")
                print(f"🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("=" * 70)
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def start_scheduled_posting(self, interval_hours=12):
        """Start automatic posting at regular intervals"""
        print("=" * 70)
        print("🤖 AI-Powered DDIA System Design Bot Started!")
        print("=" * 70)
        print(f"📅 Posting every {interval_hours} hours")
        print(f"📚 Total topics: {sum(len(topics) for topics in DDIA_TOPICS.values())}")
        print(f"🎯 Format: Comprehensive threads (2-8 tweets)")
        print(f"🧠 AI Model: GPT-4o-mini with validation")
        print(f"💼 Focus: System design interview preparation")
        print("=" * 70)
        
        # Post immediately on start
        self.create_and_post()
        
        # Schedule regular posts
        schedule.every(interval_hours).hours.do(self.create_and_post)
        
        # Keep running
        print("\n⏰ Bot is running. Press Ctrl+C to stop.\n")
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)
        except KeyboardInterrupt:
            print("\n\n👋 Bot stopped by user")

def main():
    """Main entry point"""
    try:
        bot = AISystemDesignBot()
        
        if os.getenv("GITHUB_ACTIONS"):
            bot.create_and_post()
        else:
            # Running locally
            bot.start_scheduled_posting(interval_hours=12)
        
    except Exception as e:
        print(f"❌ Failed to start bot: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()