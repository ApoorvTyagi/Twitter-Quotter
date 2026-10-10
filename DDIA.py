
import json
import os
import random
import time
from datetime import datetime

import openai
import schedule
import tweepy
from dotenv import load_dotenv

load_dotenv()

TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

MODEL_NAME = "gpt-5.6-luna"

openai.api_key = OPENAI_API_KEY

DDIA_TOPICS = {
    "simple": [
        "Hash indexes and SSTables",
        "Column-oriented storage",
        "Write-ahead logging (WAL)",
        "Bloom filters in databases",
        "Request routing in distributed systems",
        "Database pages and page layouts",
        "Slotted pages and variable-length records",
        "Heap files and record storage",
        "Buffer pools and page caching",
        "Checksums and data corruption detection",
        "Binary search trees and B-trees",
    ],
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
        "B+ tree page splits and rebalancing",
        "B+ trees vs B-trees in database indexes",
        "LSM-tree architecture and write path",
        "Memtables and immutable SSTables",
        "Compaction strategies in LSM-trees",
        "Size-tiered vs leveled compaction",
        "Bloom filters in LSM-tree storage engines",
        "Buffer pool eviction policies",
        "Database caching and locality",
        "Write-ahead logging and crash recovery",
        "Log-structured storage engines",
        "Primary indexes vs secondary indexes",
        "Covering indexes and index-only scans",
        "Database iterators and query execution",
        "External sorting in database systems",
        "Hash joins vs sort-merge joins",
    ],
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
        "MVCC implementation and version chains",
        "Lock managers and deadlock detection",
        "Optimistic vs pessimistic concurrency control",
        "Transaction logging and recovery algorithms",
        "ARIES-style database recovery",
        "Checkpointing and crash recovery",
        "Cost-based query optimization",
        "Query execution pipelines",
        "Volcano iterator model",
        "Hash index internals and collision handling",
        "Extendible hashing and dynamic hash tables",
        "LSM-tree compaction amplification",
        "Write amplification vs read amplification",
        "Storage engine performance trade-offs",
        "Database replication internals",
        "Quorum-based replication",
        "Distributed transactions and failure recovery",
        "Consistent hashing and partition placement",
    ],
}


class AISystemDesignBot:
    def __init__(self):
        """Initialize the Twitter and OpenAI clients."""
        print("Initializing bot...")

        twitter_credentials = [
            TWITTER_API_KEY,
            TWITTER_API_SECRET,
            TWITTER_ACCESS_TOKEN,
            TWITTER_ACCESS_TOKEN_SECRET,
        ]

        if not all(twitter_credentials):
            raise ValueError(
                "Missing Twitter API credentials in .env file"
            )

        if not OPENAI_API_KEY:
            raise ValueError("Missing OpenAI API key in .env file")

        self.twitter_client = tweepy.Client(
            consumer_key=TWITTER_API_KEY,
            consumer_secret=TWITTER_API_SECRET,
            access_token=TWITTER_ACCESS_TOKEN,
            access_token_secret=TWITTER_ACCESS_TOKEN_SECRET,
        )

        # GitHub Actions may encounter Cloudflare 403 errors on get_me().
        if not os.getenv("GITHUB_ACTIONS"):
            try:
                me = self.twitter_client.get_me()

                if me.data:
                    print(f"Authenticated as: @{me.data.username}")
                else:
                    print("Warning: Twitter returned no user data.")

            except tweepy.errors.TweepyException as exc:
                print(f"Twitter authentication check failed: {exc}")
                raise
        else:
            print(
                "GitHub Actions detected. "
                "Skipping get_me() to avoid intermittent Cloudflare 403."
            )

        self.posted_topics = self.load_posted_topics()
        print(f"Previously posted topics: {len(self.posted_topics)}")

    def load_posted_topics(self):
        """Load previously posted topics from JSON."""
        try:
            with open("posted_topics.json", "r", encoding="utf-8") as file:
                topics = json.load(file)

            if not isinstance(topics, list):
                print("Warning: posted_topics.json is not a list.")
                return []

            return topics

        except FileNotFoundError:
            return []

        except json.JSONDecodeError as exc:
            print(f"Warning: Invalid posted_topics.json: {exc}")
            return []

    def save_posted_topics(self):
        """Persist successfully posted topics."""
        with open("posted_topics.json", "w", encoding="utf-8") as file:
            json.dump(self.posted_topics, file, indent=2)

    def get_topic_complexity(self, topic):
        """Return the configured complexity of a topic."""
        for complexity, topics in DDIA_TOPICS.items():
            if topic in topics:
                return complexity

        return "medium"

    def split_long_tweet(self, tweet_text, max_length=280):
        """Split text into tweets without exceeding the character limit."""
        words = tweet_text.split()
        result = []
        current = ""

        for word in words:
            while len(word) > max_length:
                if current:
                    result.append(current)
                    current = ""

                result.append(word[:max_length])
                word = word[max_length:]

            candidate = f"{current} {word}".strip()

            if len(candidate) <= max_length:
                current = candidate
            else:
                if current:
                    result.append(current)

                current = word

        if current:
            result.append(current)

        return result

    def _extract_json_content(self, response, context_label):
        """Extract generated text and remove optional Markdown fences."""
        if not response.choices:
            print(f"No response choices returned during {context_label}.")
            return None

        choice = response.choices[0]
        content = (choice.message.content or "").strip()

        if not content:
            print(f"Empty model response during {context_label}.")
            print(f"Finish reason: {choice.finish_reason}")

            if response.usage:
                print(f"Token usage: {response.usage}")

            return None

        if content.startswith("```"):
            lines = content.splitlines()

            if lines and lines[0].startswith("```"):
                lines = lines[1:]

            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]

            content = "\n".join(lines).strip()

        return content

    def generate_comprehensive_thread(self, topic, complexity):
        """Generate an interview-focused thread about the selected topic."""
        thread_lengths = {
            "simple": "3-5",
            "medium": "6-10",
            "complex": "11-15",
        }

        target_length = thread_lengths.get(complexity, "5-7")
        cycle_number = self.posted_topics.count(topic) + 1

        novelty_instruction = ""

        if cycle_number > 1:
            novelty_instruction = (
                f"\nThis is cycle {cycle_number} for this topic. "
                "Use a fresh perspective, different examples, or deeper "
                "technical details than previous explanations."
            )

        prompt = f"""
You are an experienced system design interview coach and database engineer
with deep knowledge of "Designing Data-Intensive Applications" by
Martin Kleppmann and "Database Internals" by Alex Petrov.

Create a comprehensive Twitter thread about: "{topic}"
{novelty_instruction}

The audience consists of engineers preparing for backend and system
design interviews. Prioritize technical depth, implementation details,
and practical trade-offs.

For database internals, explain relevant data structures, page layouts,
memory behavior, disk I/O, algorithms, concurrency, recovery, and
performance implications.

THREAD LENGTH: {target_length} tweets.

STRUCTURE:

1. Hook:
   Start with an interesting production problem or relatable scenario.
   Explain why the concept matters. An emoji is optional.
   No hashtags.

2. Core concept:
   Explain what happens under the hood, not just what the concept means.
   Maintain technical precision.

3. Technical deep dive:
   Include relevant algorithms, data structures, concrete examples,
   complexity analysis, and CPU, memory, disk, or network implications.

4. Trade-offs:
   Explain when to use the approach and when not to.
   Discuss failure modes, operational costs, edge cases, and common
   production mistakes.

5. Final tweet:
   End with a strong technical takeaway or interview insight.
   Include #SystemDesign in the final tweet only.

VOICE:
- Sound like an experienced engineer talking to another engineer.
- Use natural language, varied sentence structure, and creative hooks.
- Avoid generic AI-sounding filler and repetitive templates.
- Never use em dashes. Use commas, colons, parentheses, or hyphens.
- Do not invent company practices, incidents, or benchmark numbers.
- Use real company examples only when the details are accurate.
- Include specific numbers only when technically justified.
- Keep the content useful, original, and technically substantive.

REQUIREMENTS:
- Return only a valid JSON array of strings.
- Every tweet must be at most 280 characters.
- Do not include hashtags except #SystemDesign in the final tweet.
- Do not use em dashes anywhere.
- Do not add commentary outside the JSON array.

Example format:
["First tweet", "Second tweet", "Final takeaway #SystemDesign"]
"""

        try:
            response = openai.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert system design interviewer "
                            "and database engineer. Explain technical "
                            "concepts precisely and naturally. Prioritize "
                            "useful insights, implementation details, and "
                            "real-world trade-offs. Never use em dashes."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                max_completion_tokens=6000,
            )

            content = self._extract_json_content(
                response,
                context_label=f"thread generation ({topic})",
            )

            if content is None:
                return None

            try:
                tweets = json.loads(content)
            except json.JSONDecodeError as exc:
                print(f"JSON parsing error: {exc}")
                print(f"Raw response: {content[:500]}")
                return None

            if (
                not isinstance(tweets, list)
                or not tweets
                or not all(isinstance(tweet, str) for tweet in tweets)
            ):
                print("The model did not return a non-empty array of strings.")
                return None

            # Split oversized tweets and reserve room for the first-tweet prefix.
            prepared_tweets = []

            for index, tweet in enumerate(tweets):
                max_length = 272 if index == 0 else 280

                if len(tweet) > max_length:
                    print(
                        f"Tweet {index + 1} is too long "
                        f"({len(tweet)} characters). Splitting it."
                    )

                    prepared_tweets.extend(
                        self.split_long_tweet(tweet, max_length)
                    )
                else:
                    prepared_tweets.append(tweet)

            # Keep the hashtag on the actual final tweet after splitting.
            if not prepared_tweets[-1].strip():
                print("The generated final tweet is empty.")
                return None

            return prepared_tweets

        except Exception as exc:
            print(f"Error generating thread: {exc}")
            return None

    def post_thread(self, tweets):
        """Post a thread with rate-limit handling and retry attempts."""
        posted_ids = []
        previous_tweet_id = None

        delay_seconds = 60 if os.getenv("GITHUB_ACTIONS") else 5

        print("\nPosting thread")
        print(f"Tweets: {len(tweets)}")
        print(f"Delay between tweets: {delay_seconds} seconds")

        for index, original_text in enumerate(tweets):
            tweet_text = original_text

            if index == 0:
                tweet_text = f"Thread: {tweet_text}"

            try:
                if previous_tweet_id:
                    response = self.twitter_client.create_tweet(
                        text=tweet_text,
                        in_reply_to_tweet_id=previous_tweet_id,
                    )
                else:
                    response = self.twitter_client.create_tweet(
                        text=tweet_text
                    )

                if not response.data or not response.data.get("id"):
                    raise RuntimeError(
                        f"Twitter returned no tweet ID for tweet {index + 1}."
                    )

                previous_tweet_id = response.data["id"]
                posted_ids.append(previous_tweet_id)

                print(
                    f"Tweet {index + 1}/{len(tweets)} posted. "
                    f"ID: {previous_tweet_id}"
                )

            except tweepy.errors.TooManyRequests as exc:
                print(f"Rate limit hit on tweet {index + 1}: {exc}")

                reset_time = None

                if getattr(exc, "response", None) is not None:
                    reset_time = exc.response.headers.get(
                        "x-rate-limit-reset"
                    )

                if reset_time:
                    wait_seconds = max(
                        1, int(reset_time) - int(time.time()) + 1
                    )
                else:
                    wait_seconds = 60

                print(f"Waiting {wait_seconds} seconds before retry.")
                time.sleep(wait_seconds)

                try:
                    if previous_tweet_id:
                        response = self.twitter_client.create_tweet(
                            text=tweet_text,
                            in_reply_to_tweet_id=previous_tweet_id,
                        )
                    else:
                        response = self.twitter_client.create_tweet(
                            text=tweet_text
                        )

                    if not response.data or not response.data.get("id"):
                        raise RuntimeError("Twitter returned no tweet ID.")

                    previous_tweet_id = response.data["id"]
                    posted_ids.append(previous_tweet_id)

                    print(
                        f"Tweet {index + 1}/{len(tweets)} posted after retry."
                    )

                except Exception as retry_error:
                    print(
                        f"Retry failed for tweet {index + 1}: {retry_error}"
                    )
                    print(
                        f"Successfully posted {len(posted_ids)} "
                        f"of {len(tweets)} tweets."
                    )

                    if posted_ids:
                        print(
                            "Thread URL: "
                            f"https://twitter.com/i/web/status/{posted_ids[0]}"
                        )

                    return posted_ids or None

            except Exception as exc:
                print(f"Failed to post tweet {index + 1}: {exc}")
                print(
                    f"Successfully posted {len(posted_ids)} "
                    f"of {len(tweets)} tweets."
                )

                if posted_ids:
                    print(
                        "Thread URL: "
                        f"https://twitter.com/i/web/status/{posted_ids[0]}"
                    )

                return posted_ids or None

            if index < len(tweets) - 1:
                print(f"Waiting {delay_seconds} seconds before next tweet.")
                time.sleep(delay_seconds)

        print(f"\nThread complete. Posted {len(posted_ids)} tweets.")

        return posted_ids or None

    def create_and_post(self):
        """Select a topic, generate a thread, and publish it."""
        try:
            all_topics = [
                topic
                for topics in DDIA_TOPICS.values()
                for topic in topics
            ]

            if len(self.posted_topics) >= len(all_topics):
                print("\nAll topics covered. Starting a new cycle.")

                self.posted_topics = []
                self.save_posted_topics()

            available_topics = [
                topic
                for topic in all_topics
                if topic not in self.posted_topics
            ]

            if not available_topics:
                print("No unused topics available.")
                return False

            topic = random.choice(available_topics)
            complexity = self.get_topic_complexity(topic)

            print(f"\nSelected topic: {topic}")
            print(f"Complexity: {complexity.upper()}")
            print("Generating thread...")

            tweets = self.generate_comprehensive_thread(
                topic,
                complexity,
            )

            if not tweets:
                print("Failed to generate thread.")
                return False

            print(f"\nGenerated thread ({len(tweets)} tweets)")
            print("=" * 70)

            for index, tweet in enumerate(tweets, start=1):
                print(f"\n[Tweet {index}/{len(tweets)}] ({len(tweet)} chars)")
                print(tweet)
                print("-" * 70)

            # Quality scoring and validation have been removed.
            print("\nPosting thread to Twitter...")

            posted_ids = self.post_thread(tweets)

            if not posted_ids:
                print("Failed to post thread.")
                return False

            # Record the topic only after the posting attempt returns IDs.
            # A partial thread is still recorded to avoid duplicate attempts.
            self.posted_topics.append(topic)
            self.save_posted_topics()

            print("\nSuccess!")
            print(
                "Thread URL: "
                f"https://twitter.com/i/web/status/{posted_ids[0]}"
            )
            print(
                f"Progress: {len(self.posted_topics)}/{len(all_topics)} "
                "topics covered"
            )
            print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 70)

            return True

        except Exception as exc:
            print(f"Unexpected error: {exc}")

            import traceback
            traceback.print_exc()

            return False

    def start_scheduled_posting(self, interval_hours=12):
        """Run the bot immediately and then at regular intervals."""
        total_topics = sum(
            len(topics) for topics in DDIA_TOPICS.values()
        )

        print("=" * 70)
        print("AI-Powered DDIA System Design Bot Started")
        print("=" * 70)
        print(f"Posting every {interval_hours} hours")
        print(f"Total topics: {total_topics}")
        print("Focus: System design and database internals")
        print(f"Model: {MODEL_NAME}")
        print("=" * 70)

        self.create_and_post()

        schedule.every(interval_hours).hours.do(self.create_and_post)

        print("\nBot is running. Press Ctrl+C to stop.")

        try:
            while True:
                schedule.run_pending()
                time.sleep(60)

        except KeyboardInterrupt:
            print("\nBot stopped by user.")


def main():
    """Start the bot in scheduled or GitHub Actions mode."""
    try:
        bot = AISystemDesignBot()

        if os.getenv("GITHUB_ACTIONS"):
            bot.create_and_post()
        else:
            bot.start_scheduled_posting(interval_hours=12)

    except Exception as exc:
        print(f"Failed to start bot: {exc}")

        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
