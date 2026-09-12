import streamlit as st
import pandas as pd
import google.generativeai as genai
import json

# --- Platform Configuration ---
st.set_page_config(page_title="Curato | AI Matchmaking", layout="wide", initial_sidebar_state="expanded")

# --- Initialize Real AI ---
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-3.6-flash')

if "user_likes" not in st.session_state:
    st.session_state.user_likes = []

# --- Navigation Sidebar ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1162/1162804.png", width=60)
    st.title("Curato OS")
    st.markdown("---")
    role = st.radio("Access Portal:", ["📱 Consumer Feed", "📊 Merchant Hub"])
    st.markdown("---")
    st.caption("MPB Project Prototype • v5.0 (Dual-Discovery)")

# ==========================================
# VIEW 1: TRUE AI CONSUMER DISCOVERY
# ==========================================
if role == "📱 Consumer Feed":
    st.header("✨ Infinite AI Discovery Feed")
    st.write("Search for anything. Curato will find exactly what you need, and then suggest how to complete the vibe.")
    
    user_vibe = st.text_input(
        "🎯 What are you looking for today?", 
        placeholder="e.g., Hindi motivational workout songs..."
    )
    
    if st.button("Generate My Curato Feed", type="primary") and user_vibe:
        with st.spinner("🧠 AI is hunting across millions of Indian catalogs to match your vibe..."):
            
            # The AI is now instructed to return TWO distinct lists
            prompt = f"""
            You are Curato, an advanced e-commerce AI designed specifically for the Indian market. 
            The user searched for: "{user_vibe}".
            
            Your job is to provide TWO sets of recommendations in a single JSON response:
            1. "direct_matches": 4 highly specific items that EXACTLY match the user's primary request category (e.g., if they ask for songs, give 4 songs).
            2. "cross_domain_matches": 4 highly specific items from DIFFERENT categories (e.g., Apparel, Electronics, Web Series, Health/Fitness) that complement the same mood or activity.
            
            CRITICAL INSTRUCTIONS:
            - Ensure items feel authentically Indian, relatable, and culturally relevant.
            - Pricing MUST be in Indian Rupees (₹).
            - Format your response STRICTLY as a valid JSON object with the two keys mentioned above.
            - Do not include markdown formatting, backticks, or the word 'json'.
            
            Example format:
            {{
              "direct_matches": [
                {{"name": "Kar Har Maidaan Fateh", "category": "Music", "merchant": "Spotify India", "price": 0, "match_score": 99, "emoji": "🎵"}}
              ],
              "cross_domain_matches": [
                {{"name": "NoiseFit Active Smartwatch", "category": "Electronics", "merchant": "Amazon India", "price": 2499, "match_score": 95, "emoji": "⌚"}}
              ]
            }}
            """
            
            try:
                response = model.generate_content(prompt)
                
                cleaned_response = response.text.strip()
                if cleaned_response.startswith("```"):
                    cleaned_response = "\n".join(cleaned_response.split("\n")[1:-1])
                
                ai_data = json.loads(cleaned_response)
                
                st.success("Feed Generated!")
                
                # --- ROW 1: DIRECT MATCHES ---
                st.subheader("🎯 Direct Matches for your Search")
                cols_direct = st.columns(4)
                for idx, item in enumerate(ai_data.get("direct_matches", [])):
                    with cols_direct[idx]:
                        with st.container(border=True):
                            st.markdown(f"## {item.get('emoji', '✨')}")
                            st.markdown(f"**{item['name']}**")
                            st.caption(f"Category: {item['category']} | 🏬 {item['merchant']}")
                            st.markdown(f"**₹{item['price']}**")
                            st.success(f"🎯 AI Match: {item['match_score']}%")
                            
                            if st.button(f"❤️ Match", key=f"dir_btn_{idx}", use_container_width=True):
                                st.session_state.user_likes.append(item)
                                st.toast("Item added to your Taste Vector!", icon="📈")

                st.markdown("---")
                
                # --- ROW 2: CROSS-DOMAIN DISCOVERY ---
                st.subheader("✨ Complete the Vibe (Cross-Domain Suggestions)")
                st.write("Explore complementary items from other categories based on your search intent.")
                cols_cross = st.columns(4)
                for idx, item in enumerate(ai_data.get("cross_domain_matches", [])):
                    with cols_cross[idx]:
                        with st.container(border=True):
                            st.markdown(f"## {item.get('emoji', '✨')}")
                            st.markdown(f"**{item['name']}**")
                            st.caption(f"Category: {item['category']} | 🏬 {item['merchant']}")
                            st.markdown(f"**₹{item['price']}**")
                            st.info(f"💡 AI Vibe Match: {item['match_score']}%")
                            
                            if st.button(f"❤️ Match", key=f"cross_btn_{idx}", use_container_width=True):
                                st.session_state.user_likes.append(item)
                                st.toast("Item added to your Taste Vector!", icon="📈")
                                
            except Exception as e:
                st.error(f"Something went wrong while parsing the data: {str(e)}")
                st.info("Here is the raw text the AI tried to send back so we can debug it:")
                st.write(response.text if 'response' in locals() else "No response from AI.")

    if len(st.session_state.user_likes) > 0:
        st.markdown("---")
        st.subheader("Your Evolving Taste Vector")
        for like in st.session_state.user_likes:
            st.write(f"• **{like['name']}** ({like['category']})")

# ==========================================
# VIEW 2: MERCHANT ANALYTICS HUB
# ==========================================
elif role == "📊 Merchant Hub":
    st.header("📈 Merchant Partner Dashboard")
    st.write("Simulating inbound traffic for registered merchants based on user interactions.")
    
    match_count = len(st.session_state.user_likes)
    simulated_impressions = (match_count * 1420) + 5400
    take_rate_revenue = match_count * 125.50
    
    kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
    kpi_col1.metric("Platform Impressions", f"{simulated_impressions:,}", "+24% AI boost")
    kpi_col2.metric("Total Match Clicks", f"{match_count}", "Live")
    kpi_col3.metric("Your Commission Paid", f"₹{take_rate_revenue:,.2f}")
