import re
import string


# =========================
# BASIC CLEANING
# =========================
def clean_text(text: str) -> str:
    """
    Main text cleaning function for embeddings.
    """

    if not text:
        return ""

    # 1. Lowercase
    text = text.lower()

    # 2. Remove extra whitespace
    text = re.sub(r"\s+", " ", text)

    # 3. Remove special characters (keep useful symbols like . , : -)
    text = re.sub(r"[^\w\s\.\,\:\-\(\)]", "", text)

    # 4. Strip spaces
    text = text.strip()

    return text


# =========================
# REMOVE PUNCTUATION (STRICT)
# =========================
def remove_punctuation(text: str) -> str:
    """
    Removes all punctuation completely.
    """
    return text.translate(str.maketrans("", "", string.punctuation))


# =========================
# NORMALIZE WHITESPACE
# =========================
def normalize_whitespace(text: str) -> str:
    """
    Fix multiple spaces, tabs, newlines.
    """
    return re.sub(r"\s+", " ", text).strip()


# =========================
# REMOVE NUMBERS (OPTIONAL USE CASE)
# =========================
def remove_numbers(text: str) -> str:
    """
    Removes all digits.
    """
    return re.sub(r"\d+", "", text)


# =========================
# STRONG CLEAN (FOR EMBEDDINGS)
# =========================
def strong_clean(text: str) -> str:
    """
    Heavy cleaning for better embeddings (use carefully).
    """

    text = text.lower()
    text = re.sub(r"http\S+|www\S+", "", text)   # remove URLs
    text = re.sub(r"\d+", "", text)              # remove numbers
    text = re.sub(r"[^\w\s]", " ", text)         # remove punctuation
    text = re.sub(r"\s+", " ", text)             # normalize spaces
    text = text.strip()

    return text