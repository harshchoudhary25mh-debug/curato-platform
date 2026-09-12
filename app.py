import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# --- Platform Configuration ---
st.set_page_config(page_title="Curato | AI Matchmaking", layout="wide", initial_sidebar_state="expanded")

# --- Initialize Default Multi-Category Catalog WITH IMAGES ---
if "catalog" not in st.session_state:
    st.session_state.catalog = pd.DataFrame([
        {"id": 1, "name": "Bose QuietComfort 45", "category": "Electronics", "merchant": "SoundTech Ltd", "vibe": "Productive Focus Minimalist", "price": 279, "impressions": 142, "clicks": 18, "boosted": False, "flagged": False, "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&q=80"},
        {"id": 2, "name": "Interstellar (4K Stream)", "category": "Media / Movie", "merchant": "CinemaStream", "vibe": "Sci-Fi Cosmic Late Night", "price": 15, "impressions": 210, "clicks": 34, "boosted": False, "flagged": False, "image": "https://images.unsplash.com/photo-1462331940025-496dfbfc7564?w=400&q=80"},
        {"id": 3, "name": "Herschel Everyday Backpack", "category": "Apparel", "merchant": "UrbanSupply Co", "vibe": "Weekend Adventure Minimalist", "price": 65, "impressions": 88, "clicks": 7, "boosted": False, "flagged": False, "image": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400&q=80"},
        {"id": 4, "name": "Atomic Habits (Hardcover)", "category": "Books", "merchant": "PageTurner Books", "vibe": "Productive Focus Growth", "price": 20, "impressions": 175, "clicks": 29, "boosted": False, "flagged": False, "image": "https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=400&q=80"},
        {"id": 5, "name": "Deep Work Synth Playlist", "category": "Music", "merchant": "AudioWave", "vibe": "Productive Focus Sci-Fi", "price": 8, "impressions": 130, "clicks": 21, "boosted": False, "flagged": False, "image": "https://images.unsplash.com/photo-1511379938547-c1f69419868d?w=400&q=80"},
        {"id": 6, "name": "Minimalist Matte Desk Lamp", "category": "Home Decor", "merchant": "Lumina Spaces", "vibe": "Productive Focus Minimalist", "price": 45, "impressions": 94, "clicks": 11, "boosted": False, "flagged": False, "image": "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=400&q=80"},
        {"id": 7, "name": "Organic Cotton Hoodie", "category": "Apparel", "merchant": "CozyWear Studio", "vibe": "Cozy Evening Minimalist", "price": 55, "impressions": 115, "clicks": 16, "boosted": False, "flagged": False, "image": "https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=400&q=80"},
        {"id": 8, "name": "Neon Cyberpunk Desk Strip", "category": "Electronics", "merchant": "GlowGrid", "vibe": "Sci-Fi Cyberpunk Late Night", "price": 30, "impressions": 62, "clicks": 9, "boosted": False, "flagged": False, "image": "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=400&q=80"}
    ])

if "user_likes" not in st.session_state:
    st.session_state.user_likes = []

# --- Navigation Sidebar ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1162/1162804.png", width=60)
    st.title("Curato OS")
    st.markdown("---")
    role = st.radio("Access Portal:", ["📱 Consumer Feed", "📊 Merchant Hub", "🛡️ Trust & Safety"])
    st.markdown("---")
    st.caption("MPB Project Prototype • v2.0")

# ==========================================
# VIEW 1: CONSUMER DISCOVERY FEED
# ==========================================
if role == "📱 Consumer Feed":
    st.header("✨ Your Unified Discovery Feed")
    
    # Cold-Start Intake
    vibe_selection = st.selectbox(
        "🎯 Step 1: What is your current mood?",
        ["Productive Focus", "Sci-Fi Late Night", "Weekend Adventure", "Cozy Evening", "Minimalist"]
    )
    st.markdown("---")
    
    valid_products = st.session_state.catalog[~st.session_state.catalog["flagged"]].copy()
    vectorizer = TfidfVectorizer()
    
    # --- ROW 1: VIBE-BASED RECOMMENDATIONS ---
    st.subheader(f"🔮 AI Curations for '{vibe_selection}'")
    
    # Calculate Vibe Match
    corpus_vibe = valid_products["vibe"].tolist() + [vibe_selection]
    tfidf_matrix_vibe = vectorizer.fit_transform(corpus_vibe)
    sim_scores_vibe = cosine_similarity(tfidf_matrix_vibe[-1], tfidf_matrix_vibe[:-1])[0]
    
    valid_products["vibe_score"] = (sim_scores_vibe * 100).round(1)
    # Apply Boost if merchant paid
    valid_products["display_score"] = valid_products.apply(
        lambda row: row["vibe_score"] + 10 if row["boosted"] else row["vibe_score"], axis=1
    )
    
    ranked_vibe_feed = valid_products.sort_values(by="display_score", ascending=False).head(4)
    
    cols1 = st.columns(4)
    for idx, (_, row) in enumerate(ranked_vibe_feed.iterrows()):
        with cols1[idx]:
            with st.container(border=True):
                st.image(row["image"], use_container_width=True)
                st.markdown(f"**{row['name']}**")
                st.caption(f"🏬 {row['merchant']}")
                
                if row["boosted"]:
                    st.info(f"✨ AI Match: {row['display_score']:.1f}% (Sponsored)")
                else:
                    st.success(f"🎯 AI Match: {row['display_score']:.1f}%")
                
                if st.button(f"❤️ Match", key=f"vibe_{row['id']}", use_container_width=True):
                    st.session_state.user_likes.append(row.to_dict())
                    st.session_state.catalog.loc[st.session_state.catalog["id"] == row["id"], "clicks"] += 1
                    st.rerun()

    # --- ROW 2: ITEM-BASED RECOMMENDATIONS (Appears only after clicking match) ---
    if len(st.session_state.user_likes) > 0:
        st.markdown("---")
        last_liked_item = st.session_state.user_likes[-1]
        
        st.subheader(f"🔗 Because you matched with **{last_liked_item['name']}**...")
        
        # Calculate Item-to-Item Match
        corpus_item = valid_products["vibe"].tolist() + [last_liked_item["vibe"]]
        tfidf_matrix_item = vectorizer.fit_transform(corpus_item)
        sim_scores_item = cosine_similarity(tfidf_matrix_item[-1], tfidf_matrix_item[:-1])[0]
        
        valid_products["item_score"] = (sim_scores_item * 100).round(1)
        
        # Filter out the item they just liked so it doesn't recommend itself
        item_feed = valid_products[valid_products["id"] != last_liked_item["id"]]
        ranked_item_feed = item_feed.sort_values(by="item_score", ascending=False).head(4)
        
        cols2 = st.columns(4)
        for idx, (_, row) in enumerate(ranked_item_feed.iterrows()):
            with cols2[idx]:
                with st.container(border=True):
                    st.image(row["image"], use_container_width=True)
                    st.markdown(f"**{row['name']}**")
                    st.caption(f"Category: {row['category']}")
                    st.warning(f"🤖 Item Similarity: {row['item_score']}%")
                    
                    if st.button(f"❤️ Match", key=f"item_{row['id']}", use_container_width=True):
                        st.session_state.user_likes.append(row.to_dict())
                        st.session_state.catalog.loc[st.session_state.catalog["id"] == row["id"], "clicks"] += 1
                        st.rerun()

# ==========================================
# VIEW 2: MERCHANT ANALYTICS HUB
# ==========================================
elif role == "📊 Merchant Hub":
    st.header("📈 Merchant Partner Dashboard")
    st.write("Real-time algorithmic exposure and customer acquisition metrics.")
    
    total_impressions = st.session_state.catalog["impressions"].sum()
    total_clicks = st.session_state.catalog["clicks"].sum()
    avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
    take_rate_revenue = (st.session_state.catalog["clicks"] * st.session_state.catalog["price"] * 0.25).sum() * 0.05
    
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    kpi_col1.metric("Platform Impressions", f"{total_impressions:,}", "+12% this week")
    kpi_col2.metric("Total Match Clicks", f"{total_clicks:,}", "Active")
    kpi_col3.metric("Platform CTR", f"{avg_ctr:.2f}%", "+0.4% from AI")
    kpi_col4.metric("Your Commission Paid", f"${take_rate_revenue:.2f}", "ROI positive")
    
    st.markdown("---")
    st.subheader("Manage Inventory & AI Boost")
    
    for idx, row in st.session_state.catalog.iterrows():
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([1, 3, 2, 2])
            c1.image(row["image"], width=60)
            c2.write(f"**{row['name']}**")
            c3.write(f"Category: {row['category']}")
            is_boosted = c4.toggle("⚡ AI Visibility Boost ($5/mo)", value=row["boosted"], key=f"boost_{row['id']}")
            st.session_state.catalog.at[idx, "boosted"] = is_boosted

# ==========================================
# VIEW 3: PLATFORM GOVERNANCE
# ==========================================
elif role == "🛡️ Trust & Safety":
    st.header("⚖️ Platform Governance Console")
    st.warning("Admin access only. Manage ecosystem integrity.")
    
    for idx, row in st.session_state.catalog.iterrows():
        g1, g2, g3 = st.columns([4, 3, 2])
        g1.write(f"**{row['name']}** — Merchant: *{row['merchant']}*")
        g2.write(f"Status: {'🔴 Suspended' if row['flagged'] else '🟢 Verified Active'}")
        toggle_flag = g3.button("Reinstate Listing" if row["flagged"] else "Flag as Counterfeit", key=f"gov_{row['id']}")
        if toggle_flag:
            st.session_state.catalog.at[idx, "flagged"] = not row["flagged"]
            st.rerun()
