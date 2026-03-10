import re
import nltk

# Download sentence tokenizer on first run
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)

HEADER_PATTERN = re.compile(
    r'(CLAUSE\s+\d+|SCHEDULE\s+[A-Z]|^\d+\.\s+[A-Z][A-Z]+|^[A-Z][A-Z\s]{4,}$)',
    re.MULTILINE
)


def segment_by_headers(text: str) -> list[dict]:
    """
    Stage 1 — regex header detection.
    Splits contract into sections wherever a header is found.
    """
    matches = list(HEADER_PATTERN.finditer(text))

    if len(matches) < 2:
        return []

    segments = []
    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        segment_text = text[start:end].strip()

        if segment_text:
            segments.append({
                "id": i,
                "label": match.group().strip(),
                "text": segment_text,
                "char_start": start,
                "char_end": end
            })

    return segments


def segment_by_sentences(text: str, max_tokens: int = 200) -> list[dict]:
    """
    Stage 2 — nltk fallback for headerless contracts.
    Groups sentences into chunks of roughly max_tokens each.
    """
    sentences = nltk.sent_tokenize(text)

    segments = []
    current_chunk = []
    current_token_count = 0
    chunk_id = 0

    for sentence in sentences:
        token_count = len(sentence.split())

        if current_token_count + token_count > max_tokens and current_chunk:
            chunk_text = " ".join(current_chunk)
            segments.append({
                "id": chunk_id,
                "label": f"Section {chunk_id + 1}",
                "text": chunk_text,
                "char_start": text.find(current_chunk[0]),
                "char_end": text.find(current_chunk[0]) + len(chunk_text)
            })
            chunk_id += 1
            current_chunk = [sentence]
            current_token_count = token_count
        else:
            current_chunk.append(sentence)
            current_token_count += token_count

    if current_chunk:
        chunk_text = " ".join(current_chunk)
        segments.append({
            "id": chunk_id,
            "label": f"Section {chunk_id + 1}",
            "text": chunk_text,
            "char_start": text.find(current_chunk[0]),
            "char_end": text.find(current_chunk[0]) + len(chunk_text)
        })

    return segments


def segment_contract(text: str) -> list[dict]:
    """
    Main function — tries header detection first, falls back to sentence chunking.
    """
    segments = segment_by_headers(text)

    if not segments:
        segments = segment_by_sentences(text)

    return segments