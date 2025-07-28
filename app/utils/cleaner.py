import re
import html
import json
import unicodedata
from bs4 import BeautifulSoup
from typing import List, Union

from langchain_text_splitters import RecursiveCharacterTextSplitter


def extract_content_from_json(data: str) -> str:
    """
    If raw input is a JSON blob, extract the 'content' field only.
    """
    try:
        parsed = json.loads(data)
        if isinstance(parsed, dict) and "content" in parsed:
            return parsed["content"]
        elif isinstance(parsed, list):
            # If list of pages: [{'url': ..., 'content': ...}, ...]
            return " ".join(page.get("content", "") for page in parsed if isinstance(page, dict))
    except json.JSONDecodeError:
        pass
    return data  


def clean_html(raw_html: str) -> str:
    """
    Remove HTML tags, decode HTML entities, normalize unicode, strip symbols.
    """
    soup = BeautifulSoup(raw_html, "html.parser")

    # Remove unwanted elements
    for tag in soup(["script", "style", "noscript", "iframe"]):
        tag.decompose()

    text = soup.get_text(separator=" ", strip=True)
    text = html.unescape(text)
    text = normalize_unicode(text)
    text = remove_noise(text)

    return text.strip()


def normalize_unicode(text: str) -> str:
    """
    Convert accented/unicode text to closest ASCII version.
    """
    text = unicodedata.normalize("NFKD", text)
    return text.encode("ascii", "ignore").decode("utf-8", "ignore")


def remove_noise(text: str) -> str:
    """
    Clean up noisy punctuation, symbols, and extra tokens like 'url:'.
    """
    # Remove emojis and pictographs
    emoji_pattern = re.compile("[" 
        u"\U0001F600-\U0001F64F"
        u"\U0001F300-\U0001F5FF"
        u"\U0001F680-\U0001F6FF"
        u"\U0001F1E0-\U0001F1FF"
        u"\u2600-\u26FF"
        u"\u2700-\u27BF"
        "]+", flags=re.UNICODE)
    text = emoji_pattern.sub(" ", text)

    text = re.sub(r"\bhttps?:\/\/\S+\b", " ", text)
    text = re.sub(r'"?url"?:\s*"?https?:.*?"?(,)?', " ", text, flags=re.IGNORECASE)

    text = re.sub(r"[^\w\s.,!?;:'\"()/-]", " ", text)
    text = re.sub(r"([.,!?;:]){2,}", r"\1", text)
    text = re.sub(r"[-]{2,}", "-", text)

    text = re.sub(r"\s+([.,!?;:])", r"\1", text)
    text = re.sub(r"([.,!?;:])([^\s])", r"\1 \2", text)

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def split_into_chunks(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
    """
    Split long cleaned text into overlapping chunks.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", "!", "?", " ", ""],
    )
    return splitter.split_text(text)


def clean_and_chunk(raw_input: Union[str, dict, list], chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
    """
    Clean raw HTML or JSON string and return cleaned text chunks.
    Supports HTML pages or {"url": ..., "content": ...} JSONs.
    """
    content_only = extract_content_from_json(raw_input)
    cleaned = clean_html(content_only)
    chunks = split_into_chunks(cleaned, chunk_size, chunk_overlap)
    return chunks
