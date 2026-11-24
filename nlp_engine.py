"""
JanMat Platform — NLP & Sentiment Scoring Engine
Provides lightweight, offline-resilient natural language processing,
lexicon-enhanced sentiment scoring, keyword extraction, and issue clustering.
"""

import re
from typing import Dict, List, Tuple
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer

# Specialized domain sentiment lexicons tailored for Indian political,
# welfare scheme, and grassroots campaign vernacular / Hinglish terms.
POSITIVE_LEXICON = {
    "smooth", "direct", "transparent", "benefited", "happy", "helped", "credit", "credited",
    "received", "relieved", "improved", "clean", "cashless", "seamless", "dignity",
    "saved", "efficient", "convenient", "secure", "delivered", "sanctioned", "connected",
    "reduced", "good", "great", "excellent", "fast", "speed", "progress", "advance",
    "accha", "bahut", "shandaar", "suvidha", "vishwas", "labh", "vikas", "dhanyawad"
}

NEGATIVE_LEXICON = {
    "blocked", "delayed", "rejection", "refused", "queues", "shortage", "corruption",
    "bribe", "bribery", "potholes", "damaged", "waterlogging", "blackout", "protest",
    "frustration", "rumors", "leak", "mismatch", "down", "downtime", "broken", "absent",
    "heavy", "difficult", "stopped", "complaint", "neglected", "bad", "poor", "worse",
    "pareshan", "samasya", "kharab", "gussa", "dhokha", "bhrashtachar", "ghotala"
}

INTENSIFIERS = {
    "very": 1.4, "deep": 1.4, "acute": 1.5, "severely": 1.6, "completely": 1.3,
    "bahut": 1.5, "bilkul": 1.4, "urgent": 1.5, "critical": 1.6
}

DIMINISHERS = {
    "slightly": 0.6, "little": 0.7, "thoda": 0.7, "somewhat": 0.8
}

NEGATIONS = {
    "not", "no", "never", "without", "nahi", "na", "mat"
}

def analyze_sentiment(text: str) -> Tuple[float, str]:
    """
    Computes normalized sentiment score between -1.00 and +1.00
    along with label ('Positive', 'Neutral', 'Negative').
    Resilient, deterministic, and works without external cloud API.
    """
    if not text or not text.strip():
        return 0.0, "Neutral"

    words = re.findall(r'\b[a-zA-Z\u0900-\u097F]+\b', text.lower())
    if not words:
        return 0.0, "Neutral"

    score = 0.0
    multiplier = 1.0
    negate = False

    for i, w in enumerate(words):
        if w in NEGATIONS:
            negate = True
            continue

        weight = 0.0
        if w in POSITIVE_LEXICON:
            weight = 1.0
        elif w in NEGATIVE_LEXICON:
            weight = -1.0

        if weight != 0.0:
            current_multiplier = multiplier
            # Check previous word for intensifiers
            if i > 0 and words[i-1] in INTENSIFIERS:
                current_multiplier *= INTENSIFIERS[words[i-1]]
            elif i > 0 and words[i-1] in DIMINISHERS:
                current_multiplier *= DIMINISHERS[words[i-1]]

            effective_score = weight * current_multiplier
            if negate:
                effective_score *= -0.75
                negate = False

            score += effective_score

    # Normalize between -1.0 and 1.0
    num_significant = max(1, len([w for w in words if w in POSITIVE_LEXICON or w in NEGATIVE_LEXICON]))
    normalized = max(-1.0, min(1.0, score / (num_significant * 1.2)))
    normalized = round(normalized, 2)

    if normalized >= 0.15:
        label = "Positive"
    elif normalized <= -0.15:
        label = "Negative"
    else:
        label = "Neutral"

    return normalized, label

def extract_top_keywords(corpus: List[str], top_n: int = 15) -> List[Tuple[str, float]]:
    """
    Extracts top keywords using TF-IDF across feedback text corpus.
    """
    if not corpus:
        return []

    # Clean corpus
    clean_corpus = [c for c in corpus if isinstance(c, str) and len(c.strip()) > 5]
    if not clean_corpus:
        return []

    stop_words_custom = {
        'the', 'and', 'to', 'of', 'in', 'is', 'for', 'on', 'with', 'at', 'by',
        'from', 'up', 'about', 'into', 'over', 'after', 'our', 'this', 'that',
        'these', 'those', 'are', 'was', 'were', 'been', 'being', 'have', 'has',
        'had', 'having', 'do', 'does', 'did', 'doing', 'an', 'the', 'under',
        'per', 'all', 'very', 'due', 'house', 'village', 'need', 'received'
    }

    try:
        vectorizer = TfidfVectorizer(
            stop_words=list(stop_words_custom),
            ngram_range=(1, 2),
            max_features=top_n * 2,
            min_df=2
        )
        tfidf_matrix = vectorizer.fit_transform(clean_corpus)
        feature_names = vectorizer.get_feature_names_out()
        sums = tfidf_matrix.sum(axis=0)

        data = []
        for col, term in enumerate(feature_names):
            data.append((term.title(), float(sums[0, col])))

        data.sort(key=lambda x: x[1], reverse=True)
        return data[:top_n]
    except Exception:
        # Fallback to simple term frequency
        words = []
        for text in clean_corpus:
            tokens = re.findall(r'\b[A-Za-z]{4,}\b', text.lower())
            words.extend([t for t in tokens if t not in stop_words_custom])
        counts = Counter(words).most_common(top_n)
        return [(k.title(), float(v)) for k, v in counts]
