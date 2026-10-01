"""Category definitions — প্রতি ক্যাটাগরির নিজস্ব সোর্স, কীওয়ার্ড ও ফিল্টার।"""

GEO = "US"
HL = "en-US"

# US-এ ইংরেজি ও স্প্যানিশ — দুই ভাষাতেই ট্রেন্ড আনা হয়
LANGS = [
    {"code": "en", "hl": "en-US", "ceid": "US:en", "tag": ""},
    {"code": "es", "hl": "es-419", "ceid": "US:es", "tag": "[ES] "},
]
TOPICS_PER_PLATFORM = 5
MIN_SCORE = 25          # এর নিচে স্কোর হলে টপিক বাদ (ফালতু জিনিস ছেঁকে ফেলা)

# ---------------------------------------------------------------- categories
CATEGORIES = {

    "Tech": {
        "label": "Tech / AI / Gadgets / Product Launch",
        # অবশ্যই এর একটা শব্দ থাকতে হবে (না থাকলে টপিক বাদ)
        "must_any": [
            "ai", "artificial intelligence", "gpt", "llm", "chatgpt", "gemini", "claude", "copilot",
            "openai", "anthropic", "nvidia", "gpu", "chip", "semiconductor", "apple", "iphone", "ipad",
            "macbook", "samsung", "galaxy", "pixel", "android", "ios", "windows", "microsoft", "google",
            "meta", "tesla", "spacex", "startup app", "software", "app", "laptop", "smartphone", "phone",
            "review", "leak", "launch", "unveil", "release", "benchmark", "robot", "drone", "vr", "ar",
            "headset", "quantum", "cybersecurity", "hack", "data breach", "update", "firmware", "processor",
            "battery", "ev", "electric car", "cloud", "api", "developer", "coding", "open source", "linux",
        ],
        "never": ["recipe", "horoscope", "nfl", "nba score", "celebrity gossip"],
        "seeds": ["AI tools", "iPhone 17", "best laptop 2026", "new AI model",
                  "tech product launch", "smartphone review", "GPU benchmark"],
        "subreddits": ["technology", "gadgets", "artificial", "singularity", "hardware",
                       "Android", "apple", "LocalLLaMA", "programming"],
        "news_queries": ["AI announcement", "new gadget launch", "tech product review",
                         "technology leak", "software update release"],
        "gnews_topic": "TECHNOLOGY",
        "yt_queries": ["tech review 2026", "AI news this week", "new smartphone unboxing",
                       "best gadgets", "AI tools tutorial"],
        "quora_queries": ["best AI tool", "which smartphone should I buy", "is AI going to",
                          "best laptop for"],
        "es_queries": ['inteligencia artificial', 'nuevo celular', 'mejor laptop', 'tecnologia noticias'],
        "extra_rss": [
            "https://www.theverge.com/rss/index.xml",
            "https://techcrunch.com/feed/",
            "https://www.engadget.com/rss.xml",
            "https://arstechnica.com/feed/",
            "https://feeds.arstechnica.com/arstechnica/gadgets",
        ],
    },

    "News": {
        "label": "World & US News",
        "must_any": [
            "president", "election", "senate", "congress", "government", "policy", "law", "court",
            "supreme court", "war", "ukraine", "russia", "israel", "gaza", "china", "india", "eu",
            "protest", "strike", "shooting", "storm", "hurricane", "earthquake", "flood", "wildfire",
            "crisis", "attack", "killed", "arrested", "investigation", "sanctions", "treaty", "summit",
            "trump", "biden", "white house", "pentagon", "un", "nato", "immigration", "border",
            "breaking", "report", "announced", "state of emergency", "verdict", "indicted",
        ],
        "never": ["recipe", "unboxing", "asmr"],
        "seeds": ["us supreme court ruling", "immigration policy news", "congress bill vote",
                  "white house announcement", "ukraine russia war update",
                  "middle east conflict news", "us election 2026"],
        "subreddits": ["news", "worldnews", "politics", "UpliftingNews", "geopolitics"],
        "news_queries": ["breaking news", "world news today", "US politics"],
        "gnews_topic": "WORLD",
        "yt_queries": ["breaking news today", "world news update", "news analysis"],
        "quora_queries": ["why is happening in", "what will happen if"],
        "es_queries": ['noticias de ultima hora', 'noticias estados unidos', 'noticias del mundo'],
        "extra_rss": [
            "https://feeds.bbci.co.uk/news/world/rss.xml",
            "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
            "https://feeds.npr.org/1001/rss.xml",
            "https://moxie.foxnews.com/google-publisher/latest.xml",
        ],
    },

    "Islamic": {
        "label": "Islamic Content / Topics",
        "must_any": [
            "islam", "islamic", "muslim", "quran", "qur'an", "hadith", "sunnah", "prophet",
            "muhammad", "allah", "salah", "namaz", "prayer", "dua", "ramadan", "eid", "hajj",
            "umrah", "mecca", "makkah", "medina", "zakat", "halal", "haram", "hijab", "masjid",
            "mosque", "imam", "sharia", "fiqh", "tafsir", "sufi", "ummah", "fasting", "jummah",
            "ayah", "surah", "iftar", "shia", "sunni", "madrasa", "sheikh", "fatwa",
        ],
        "never": ["stock market", "nfl", "makhachev", "ufc", "mma", "octagon",
                  "fighter", "knockout", "boxing", "vs garry", "lightweight title"],
        "seeds": ["Quran tafsir", "how to pray salah", "Ramadan 2026", "Islamic history",
                  "dua for", "halal food", "hajj guide"],
        "subreddits": ["islam", "MuslimLounge", "Quran", "converts", "Muslim"],
        "news_queries": ["Muslim community", "Islamic scholar", "mosque", "Ramadan Eid",
                         "Quran study"],
        "gnews_topic": None,
        "yt_queries": ["Islamic lecture", "Quran recitation", "how to pray salah",
                       "Islamic reminder", "seerah prophet"],
        "quora_queries": ["what does Islam say about", "is it haram to", "how to pray",
                          "meaning of surah"],
        "es_queries": ['islam', 'musulmanes', 'coran', 'ramadan'],
        "extra_rss": [
            "https://aboutislam.net/feed/",
            "https://www.islamicity.org/feed/",
            "https://muslimmatters.org/feed/",
        ],
    },

}

PLATFORMS = ["Google Trends", "YouTube", "Reddit", "Quora", "Bing Search", "Google News"]
