# core.py
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd



TOKEN_RE = re.compile(r"[A-Za-z']+")

CHAT_RE = re.compile(r"^\d{1,2}/\d{1,2}/\d{2}, .*? – (?P<user>.*?): (?P<msg>.*)$")

# WhatsApp-style: 12/04/24, 09:17 – Alice: Hey
LINE_RE = re.compile(
    r"""^
        \d{1,2}/\d{1,2}/\d{2,4},\s        # 09/04/2022,
        \d{1,2}:\d{2}\s-\s                # 13:37 -
        (?P<user>[^:]+):\s                # Mr_X:
        (?P<msg>.*)$                      # message
    """, re.VERBOSE)

def read_plain_chat(path: Path) -> pd.DataFrame:
    rows = []
    with path.open(encoding="utf-8", errors="ignore") as f:
        for idx, line in enumerate(f, 1):
            m = LINE_RE.match(line.strip())
            if m:                                    # keep only real messages
                rows.append({"entry_index": idx,
                             "user": m["user"].strip(),
                             "text": m["msg"]})
    return pd.DataFrame(rows)


def load_lexicons(lexicon_path: str | Path) -> Dict[str, set]:
    lexicon_path = Path(lexicon_path)
    data = json.loads(lexicon_path.read_text(encoding="utf-8"))
    dims = data["dimensions"]
    return {k: set(map(str.lower, v)) for k, v in dims.items()}

def tokenize(text: str) -> List[str]:
    return [t.lower() for t in TOKEN_RE.findall(text)]

def score_tokens(tokens: List[str], lexicons: Dict[str, set]) -> Dict[str, float]:
    if not tokens:
        return {dim: 0.0 for dim in lexicons}
    token_set = tokens  # keep multiplicity (counts), not unique
    n = len(token_set)
    out = {}
    for dim, words in lexicons.items():
        hits = sum(1 for tok in token_set if tok in words)
        out[dim] = hits / n
    return out


def process_chat(path_to_txt: str | Path, lexicon_path: str | Path = "lexicons.json") -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Returns:
      message_df: one row per message with six dimension rates
      summary_df: one row with mean rates across messages
    """
    lexicons = load_lexicons(lexicon_path)
    df = read_plain_chat(path_to_txt)

    scores = []
    for text in df["text"].astype(str):
        tokens = tokenize(text)
        scores.append(score_tokens(tokens, lexicons))

    score_df = pd.DataFrame(scores)
    message_df = pd.concat([df, score_df], axis=1)

    summary = score_df.mean(numeric_only=True).to_frame("mean_rate").T
    summary.insert(0, "n_messages", len(message_df))
    return message_df, summary