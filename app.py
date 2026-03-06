# app.py
import io
import tempfile
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from core import process_chat

BASE_DIR = Path(__file__).parent
LEX_PATH = BASE_DIR / "lexicons.json"
DIM_LABELS = {
    "emo":      "Emotion",
    "coord":    "Coordination",
    "abstract": "Abstract",
    "dim4":     "Agency",
    "dim5":     "Future",
    "dim6":     "Self-Focus",
}

st.set_page_config(page_title="Chat Lexicon Analyzer", layout="centered")

st.title("Chat Lexicon Analyzer")
st.write("Upload a plain-text chat file and get six lexicon metrics + downloads.")

uploaded = st.file_uploader("Upload .txt", type=["txt"])

if uploaded:
        with tempfile.TemporaryDirectory() as td:
            tmp_path = Path(td) / "chat.txt"
            tmp_path.write_bytes(uploaded.getvalue())

            # ---- parse & build dataframe ---------------------------------
            msg_df, _ = process_chat(tmp_path, lexicon_path=LEX_PATH)

            if "user" not in msg_df.columns:
                st.error("Couldn’t detect speakers – is this a standard WhatsApp export?")
                st.stop()

            users   = sorted(msg_df["user"].unique())
            speaker = st.selectbox("Choose speaker", users)

            filtered = msg_df[msg_df["user"] == speaker]
            dims = [c for c in filtered.columns if c not in ("entry_index", "user", "text")]

            summary_df = filtered[dims].mean().to_frame("mean_rate").T
            summary_df = summary_df.rename(columns=DIM_LABELS) 
            dims = [DIM_LABELS[d] for d in dims]     # update the list
            
            st.subheader("Summary (mean rates)")
            st.dataframe(summary_df)


            #radar plot
            values = summary_df.loc["mean_rate", dims].values.astype(float)

            angles = np.linspace(0, 2*np.pi, len(dims), endpoint=False)
            values_closed = np.r_[values, values[0]]
            angles_closed = np.r_[angles, angles[0]]

            fig = plt.figure()
            ax = plt.subplot(111, polar=True)
            ax.plot(angles_closed, values_closed)
            ax.fill(angles_closed, values_closed, alpha=0.15)
            labels = [DIM_LABELS.get(d, d) for d in dims]
            ax.set_thetagrids(angles * 180/np.pi, labels)
            ax.set_title("Lexicon profile (mean rate)")
            st.pyplot(fig)

            # Downloads
            st.subheader("Downloads")
            st.download_button(
                "Download message-level CSV",
                data=msg_df.to_csv(index=False).encode("utf-8"),
                file_name="message_level_scores.csv",
                mime="text/csv",
            )
            st.download_button(
                "Download summary CSV",
                data=summary_df.to_csv(index=False).encode("utf-8"),
                file_name="summary_scores.csv",
                mime="text/csv",
            )