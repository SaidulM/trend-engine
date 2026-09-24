"""Category definitions — প্রতি ক্যাটাগরির নিজস্ব সোর্স, কীওয়ার্ড ও ফিল্টার।"""

GEO = "US"
HL = "en-US"
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
        "extra_rss": [
            "https://www.theverge.com/rss/index.xml",
            "https://techcrunch.com/feed/",
            "https://www.engadget.com/rss.xml",
            "https://arstechnica.com/feed/",
            "https://feeds.arstechnica.com/arstechnica/gadgets",
        ],
    },

    "Health": {
        "label": "Health / Fitness / Medicine / Nutrition",
        "must_any": [
            "health", "healthy", "disease", "symptom", "doctor", "hospital", "patient", "medicine",
            "medical", "drug", "vaccine", "virus", "flu", "covid", "cancer", "diabetes", "heart",
            "blood pressure", "cholesterol", "mental health", "anxiety", "depression", "sleep",
            "diet", "nutrition", "vitamin", "protein", "weight loss", "obesity", "fitness", "workout",
            "exercise", "yoga", "gut", "immune", "fda", "cdc", "who", "therapy", "supplement",
            "ozempic", "wellness", "pregnancy", "skin", "allergy", "cold", "pain",
        ],
        "never": ["stock", "crypto", "football", "movie"],
        "seeds": ["weight loss tips", "healthy diet", "mental health", "ozempic side effects",
                  "best workout", "vitamin deficiency", "sleep better"],
        "subreddits": ["Health", "Fitness", "nutrition", "loseit", "science", "medicine",
                       "AskDocs", "mentalhealth"],
        "news_queries": ["health study finds", "new treatment approved", "nutrition research",
                         "fitness trend", "FDA approval"],
        "gnews_topic": "HEALTH",
        "yt_queries": ["health tips 2026", "weight loss transformation", "doctor explains",
                       "home workout", "healthy meal prep"],
        "quora_queries": ["how to lose weight", "is it healthy to", "what causes",
                          "best exercise for"],
        "extra_rss": [
            "https://www.medicalnewstoday.com/rss",
            "https://www.health.harvard.edu/blog/feed",
            "https://tools.cdc.gov/api/v2/resources/media/404952.rss",
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
        "seeds": ["breaking news today", "us politics", "world news", "election update"],
        "subreddits": ["news", "worldnews", "politics", "UpliftingNews", "geopolitics"],
        "news_queries": ["breaking news", "world news today", "US politics"],
        "gnews_topic": "WORLD",
        "yt_queries": ["breaking news today", "world news update", "news analysis"],
        "quora_queries": ["why is happening in", "what will happen if"],
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
        "never": ["stock market", "nfl"],
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
        "extra_rss": [
            "https://aboutislam.net/feed/",
            "https://www.islamicity.org/feed/",
            "https://muslimmatters.org/feed/",
        ],
    },

    "Image_Emoji": {
        "label": "Images / Emoji / Memes / Visual Trends",
        "must_any": [
            "emoji", "emote", "meme", "memes", "viral", "wallpaper", "aesthetic", "photo",
            "picture", "image", "gif", "sticker", "avatar", "pfp", "profile picture", "filter",
            "ai image", "midjourney", "dall-e", "stable diffusion", "photoshop", "canva",
            "thumbnail", "poster", "design", "illustration", "art", "trend", "reaction",
            "emoji meaning", "unicode", "icon", "logo", "template", "edit", "photography",
        ],
        "never": ["stock market", "surgery"],
        "seeds": ["emoji meaning", "viral meme", "AI image generator", "aesthetic wallpaper",
                  "new emoji 2026", "meme template"],
        "subreddits": ["memes", "dankmemes", "pics", "wallpapers", "aiArt", "Design",
                       "midjourney", "photoshop"],
        "news_queries": ["new emoji", "viral meme", "AI image generator", "unicode emoji update"],
        "gnews_topic": None,
        "yt_queries": ["viral memes 2026", "AI image generator tutorial", "emoji meanings explained",
                       "photo editing tricks"],
        "quora_queries": ["what does this emoji mean", "best AI image generator",
                          "where to find free images"],
        "extra_rss": [
            "https://knowyourmeme.com/newsfeed.rss",
            "https://blog.emojipedia.org/feed/",
        ],
    },

    "Business": {
        "label": "Business / Startup / Money / Market",
        "must_any": [
            "business", "startup", "founder", "entrepreneur", "funding", "raise", "vc",
            "venture capital", "ipo", "acquisition", "merger", "revenue", "profit", "earnings",
            "stock", "stocks", "market", "nasdaq", "s&p", "dow", "shares", "investor", "investing",
            "crypto", "bitcoin", "ethereum", "economy", "inflation", "recession", "fed",
            "interest rate", "jobs report", "layoff", "hiring", "ecommerce", "amazon", "walmart",
            "tariff", "trade", "salary", "passive income", "side hustle", "marketing", "brand",
            "dropshipping", "saas", "bank", "loan", "tax", "ceo", "billion", "million",
        ],
        "never": ["recipe", "workout"],
        "seeds": ["stock market today", "how to start a business", "passive income ideas",
                  "startup funding", "crypto price", "side hustle 2026"],
        "subreddits": ["business", "Entrepreneur", "stocks", "investing", "smallbusiness",
                       "wallstreetbets", "startups", "economy"],
        "news_queries": ["stock market", "startup funding round", "company earnings",
                         "layoffs announced", "economy inflation"],
        "gnews_topic": "BUSINESS",
        "yt_queries": ["make money online 2026", "stock market analysis", "start a business",
                       "side hustle ideas", "business case study"],
        "quora_queries": ["how to start a business", "best way to invest", "is it profitable to",
                          "how much money can you make"],
        "extra_rss": [
            "https://feeds.a.dj.com/rss/RSSMarketsMain.xml",
            "https://www.cnbc.com/id/10001147/device/rss/rss.html",
            "https://feeds.bloomberg.com/markets/news.rss",
            "https://techcrunch.com/category/startups/feed/",
        ],
    },
}

PLATFORMS = ["Google Trends", "YouTube", "Reddit", "Quora", "Bing Search", "Google News"]
