"""Shared validation helpers for user-provided text."""
import re

try:
    from better_profanity import profanity
except ModuleNotFoundError:
    profanity = None


CENSOR_MARKER = "\x00"
BANNED_WORDS = [
    "badword",
    "curse",
    "damn",
    "fuck",
    "idiot",
    "jerk",
    "nastyword",
    "sh_t",
    "stupid",
    "trashword",
    "wtf",
]


def _build_censor_words(words: list[str]) -> list[str]:
    """Return base words and basic plural variations."""
    censor_words = set()

    for word in words:
        plural_word = f"{word}s"
        censor_words.add(word)
        censor_words.add(plural_word)
        censor_words.add(word.upper())
        censor_words.add(plural_word.upper())

    return list(censor_words)


_CENSOR_WORDS = _build_censor_words(BANNED_WORDS)
if profanity is not None:
    profanity.load_censor_words()
    profanity.add_censor_words(_CENSOR_WORDS)
_CENSOR_MARKER_BLOCK = CENSOR_MARKER * 4
_CENSOR_WORDS_PATTERN = re.compile(
    r"(?<![A-Za-z0-9_])(" + "|".join(re.escape(word) for word in _CENSOR_WORDS) + r")(?![A-Za-z0-9_])",
    re.IGNORECASE,
)


def validate_and_censor_text(text: str) -> str:
    """Return text with inappropriate words censored."""
    if not text:
        return text

    if profanity is None:
        return _CENSOR_WORDS_PATTERN.sub(lambda match: "*" * len(match.group(0)), text)

    original_text = f"{text} "
    censored_text = profanity.censor(original_text, censor_char=CENSOR_MARKER)
    return _restore_censor_lengths(original_text, censored_text)[:-1]


def validate_and_censor_note(text: str) -> str:
    """Return note text with inappropriate words censored."""
    return validate_and_censor_text(text)


def contains_inappropriate_words(text: str) -> bool:
    """Return True if text contains inappropriate words."""
    if not text:
        return False

    if profanity is None:
        return _CENSOR_WORDS_PATTERN.search(text) is not None

    return validate_and_censor_text(text) != text


def _restore_censor_lengths(original_text: str, censored_text: str) -> str:
    """Expand fixed censor markers to match original word lengths."""
    result = []
    original_index = 0
    censored_index = 0

    while censored_index < len(censored_text):
        if censored_text.startswith(_CENSOR_MARKER_BLOCK, censored_index):
            span_end = _find_censored_span_end(
                original_text,
                original_index,
                censored_text,
                censored_index + len(_CENSOR_MARKER_BLOCK),
            )
            result.append("*" * (span_end - original_index))
            original_index = span_end
            censored_index += len(_CENSOR_MARKER_BLOCK)
            continue

        result.append(censored_text[censored_index])
        original_index += 1
        censored_index += 1

    return "".join(result)


def _find_censored_span_end(
    original_text: str,
    original_index: int,
    censored_text: str,
    next_censored_index: int,
) -> int:
    """Return the original index where a censored span ends."""
    if next_censored_index >= len(censored_text):
        return len(original_text)

    next_visible_char = censored_text[next_censored_index]
    span_end = original_text.find(next_visible_char, original_index)

    if span_end == -1:
        return len(original_text)

    return span_end
