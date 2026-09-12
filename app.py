import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# --- Platform Configuration ---
st.set_page_config(page_title="Curato | AI Matchmaking Platform", layout="wide")

# --- Initialize Default Multi-Category Catalog ---
if "catalog" not in st.session_state:
    st.session_state.catalog = pd.DataFrame([
        {"id": 1, "name": "Bose QuietComfort 45", "category": "Electronics", "merchant": "SoundTech Ltd", "vibe": "Productive Focus Minimalist", "price": 279, "impressions": 142, "clicks": 18, "boosted": False, "flagged": False},
        {"id": 2, "name": "Interstellar (4K Stream)", "category": "Media / Movie", "merchant": "CinemaStream", "vibe": "Sci-Fi Cosmic Late Night", "price": 15, "impressions": 210, "clicks": 34, "boosted": False, "flagged": False},
        {"id": 3, "name": "Herschel Everyday Backpack", "category": "Apparel", "merchant": "UrbanSupply Co", "vibe": "Weekend Adventure Minimalist", "price": 65, "impressions": 88, "clicks": 7, "boosted": False, "flagged": False},
        {"id": 4, "name": "Atomic Habits (Hardcover)", "category": "Books", "merchant": "PageTurner Books", "vibe": "Productive Focus Growth", "price": 20, "impressions": 175, "clicks": 29, "boosted": False, "flagged": False},
        {"id": 5, "name": "Deep Work Ambient Synth Playlist", "category": "Music", "merchant": "AudioWave", "vibe": "Productive Focus Sci-Fi", "price": 8, "impressions": 130, "clicks": 21, "boosted": False, "flagged": False},
        {"id": 6, "name": "Minimalist Matte Desk Lamp", "category": "Home Decor", "merchant": "Lumina Spaces", "vibe": "Productive Focus Minimalist", "price": 45, "impressions": 94, "clicks": 11, "boosted": False, "flagged": False},
        {"id": 7, "name": "Oversized Organic Cotton Hoodie", "category": "Apparel", "merchant": "CozyWear Studio", "vibe": "Cozy Evening Minimalist", "price": 55, "impressions": 115, "clicks": 16, "boosted": False, "flagged": False},
        {"id": 8, "name": "Cyberpunk Neon Desk Strip", "category": "Electronics", "merchant": "GlowGrid", "vibe": "Sci-Fi Cyberpunk Late Night", "price": 30, "impressions": 62, "clicks": 9, "boosted": False, "flagged": False}
    ])

if "user_likes" not in st.session_state:
    st.session_state.user_likes = []

# --- Navigation Sidebar ---
st.sidebar.title("Curato Platform Engine")
role = st.sidebar.radio("Navigate Platform View:", ["Consumer Discovery Feed", "Merchant Analytics Hub", "Platform Governance & Trust"])
st.sidebar.markdown("---")
st.sidebar.caption("MPB Project • Cross-Domain AI Matchmaking Layer")

# ==========================================
# VIEW 1: CONSUMER DISCOVERY FEED
# ==========================================
if role == "Consumer Discovery Feed":
    st.title("Curato: Unified Lifestyle Discovery")
    st.markdown("Your multi-category AI feed spanning Tech, Fashion, Media, and Home Decor.")
    
    # Cold-Start Style / Vibe Intake
    st.subheader("Step 1: Calibrate Your Taste Profile")
    vibe_selection = st.selectbox(
        "Choose your current lifestyle vibe:",
        ["Productive Focus", "Sci-Fi Late Night", "Weekend Adventure", "Cozy Evening", "Minimalist"]
    )
    
    # Recommendation Algorithm (TF-IDF + Cosine Similarity)
    valid_products = st.session_state.catalog[~st.session_state.catalog["flagged"]].copy()
    
    # Build search context combining chosen vibe and past liked items
    liked_context = " ".join([item["vibe"] for item in st.session_state.user_likes])
    query_context = f"{vibe_selection} {liked_context}".strip()
    
    vectorizer = TfidfVectorizer()
    corpus = valid_products["vibe"].tolist() + [query_context]
    tfidf_matrix = vectorizer.fit_transform(corpus)
    
    # Match query context with product tags
    sim_scores = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])[0]
    valid_products["ai_match_score"] = (sim_scores * 100).round(1)
    
    # Apply merchant boost weight (+10% score if boosted)
    valid_products["display_score"] = valid_products.apply(
        lambda row: row["ai_match_score"] + 10 if row["boosted"] else row["ai_match_score"], axis=1
    )
    ranked_feed = valid_products.sort_values(by="display_score", ascending=False)
    
    st.subheader(f"Step 2: Curated Matches for '{vibe_selection}'")
    cols = st.columns(3)
    for idx, (_, row) in enumerate(ranked_feed.iterrows()):
        with cols[idx % 3]:
            with st.container(border=True):
                st.markdown(f"**{row['name']}**")
                st.caption(f"Category: {row['category']} • Merchant: {row['merchant']}")
                st.write(f"Price: **${row['price']}**")
                st.info(f"AI Match: **{row['display_score']:.1f}%**" + (" *(Sponsored Boost)*" if row["boosted"] else ""))
                
                if st.button(f"Save / Match Item", key=f"btn_{row['id']}"):
                    st.session_state.user_likes.append(row.to_dict())
                    # Record click to merchant metrics
                    st.session_state.catalog.loc[st.session_state.catalog["id"] == row["id"], "clicks"] += 1
                    st.success(f"Matched! Taste Vector updated.")
                    st.rerun()

    if st.session_state.user_likes:
        st.markdown("---")
        st.write("### Your Active Taste Profile Signals")
        liked_names = [f"• {item['name']} ({item['category']})" for item in st.session_state.user_likes]
        st.markdown("\n".join(liked_names))

# ==========================================
# VIEW 2: MERCHANT ANALYTICS HUB
# ==========================================
elif role == "Merchant Analytics Hub":
    st.title("Curato Merchant Dashboard")
    st.markdown("Monitor cross-domain exposure, customer acquisition, and monetization performance.")
    
    total_impressions = st.session_state.catalog["impressions"].sum()
    total_clicks = st.session_state.catalog["clicks"].sum()
    avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
    simulated_gmv = (st.session_state.catalog["clicks"] * st.session_state.catalog["price"] * 0.25).sum()
    take_rate_revenue = simulated_gmv * 0.05
    
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    kpi_col1.metric("Total Catalog Impressions", f"{total_impressions:,}")
    kpi_col2.metric("Total Match Clicks", f"{total_clicks:,}")
    kpi_col3.metric("Platform CTR", f"{avg_ctr:.2f}%")
    kpi_col4.metric("Platform Commission (5%)", f"${take_rate_revenue:.2f}")
    
    st.markdown("---")
    st.subheader("Manage Inventory & AI Boost Placements")
    
    for idx, row in st.session_state.catalog.iterrows():
        c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
        c1.write(f"**{row['name']}** ({row['category']})")
        c2.write(f"Merchant: {row['merchant']}")
        c3.write(f"Clicks: {row['clicks']}")
        is_boosted = c4.checkbox("Boost with AI ($5/mo)", value=row["boosted"], key=f"boost_{row['id']}")
        st.session_state.catalog.at[idx, "boosted"] = is_boosted

# ==========================================
# VIEW 3: PLATFORM GOVERNANCE & TRUST
# ==========================================
elif role == "Platform Governance & Trust":
    st.title("Platform Trust & Governance Panel")
    st.markdown("Manage ecosystem integrity, counterfeit detection, and merchant verification.")
    
    st.subheader("Active Listing Moderation")
    for idx, row in st.session_state.catalog.iterrows():
        g1, g2, g3 = st.columns([4, 3, 2])
        g1.write(f"**{row['name']}** — Merchant: *{row['merchant']}*")
        g2.write(f"Status: {'Flagged / Suspended' if row['flagged'] else 'Verified Active'}")
        toggle_flag = g3.button(
            "Reinstate" if row["flagged"] else "Flag Listing",
            key=f"gov_{row['id']}"
        )
        if toggle_flag:
            st.session_state.catalog.at[idx, "flagged"] = not row["flagged"]
            st.rerun()
