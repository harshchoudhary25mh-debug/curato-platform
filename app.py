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
    st.caption("MPB Project Prototype • v6.0 (Multi-Tier Choice Architecture)")

# ==========================================
# VIEW 1: TRUE AI CONSUMER DISCOVERY
# ==========================================
if role == "📱 Consumer Feed":
    st.header("✨ Infinite AI Discovery Feed")
    st.write("Curato builds complete lifestyle bundles with options for every budget.")
    
    user_vibe = st.text_input(
        "🎯 What are you planning or looking for today?", 
        placeholder="e.g., Planning a surprise birthday party..."
    )
    
    if st.button("Curate My Options", type="primary") and user_vibe:
        with st.spinner("🧠 AI is architecting multi-tier options from Indian catalogs..."):
            
            # The AI is now instructed to bundle by Category and offer Price Tiers
            prompt = f"""
            You are Curato, an advanced e-commerce AI designed specifically for the Indian market. 
            The user's intent is: "{user_vibe}".
            
            Your job is to provide a comprehensive, multi-tiered recommendation bundle. Break down the user's request into exactly 3 logical Categories (e.g., if they are planning a birthday, categories could be Cakes/Food, Music/Entertainment, and Decor/Gifts).
            
            Within EACH category, you MUST provide exactly 2 distinct options targeting different budgets:
            1. A "Value / Free" option (low cost, everyday budget, or free streaming).
            2. A "Premium / Upgraded" option (luxury, specialized, or physical product purchase).
            
            CRITICAL INSTRUCTIONS:
            - Ensure items feel authentically Indian and relatable.
            - Pricing MUST be in Indian Rupees (₹). Use 0 for free digital items.
            - Format your response STRICTLY as a valid JSON array of objects. Do not include markdown formatting, backticks, or the word 'json'.
            
            Example format:
            [
              {{
                "category_name": "Celebration Cakes",
                "options": [
                  {{"name": "1kg Pineapple Cake", "merchant": "Bakingo", "price": 499, "tier": "Value Option", "emoji": "🧁"}},
                  {{"name": "Custom 2-Tier Truffle Cake", "merchant": "Theobroma", "price": 2499, "tier": "Premium Upgrade", "emoji": "🎂"}}
                ]
              }},
              {{
                "category_name": "Party Playlists & Music",
                "options": [
                  {{"name": "Bollywood Party Anthems", "merchant": "Spotify India", "price": 0, "tier": "Free Streaming", "emoji": "🎵"}},
                  {{"name": "Portable Party Speaker", "merchant": "Amazon (boAt)", "price": 3499, "tier": "Premium Upgrade", "emoji": "🔊"}}
                ]
              }}
            ]
            """
            
            try:
                response = model.generate_content(prompt)
                
                cleaned_response = response.text.strip()
                if cleaned_response.startswith("```"):
                    cleaned_response = "\n".join(cleaned_response.split("\n")[1:-1])
                
                ai_data = json.loads(cleaned_response)
                
                st.success("Your Curated Options are Ready!")
                
                # Render the Multi-Tier Choice Architecture
                for cluster in ai_data:
                    st.markdown(f"### ✨ {cluster['category_name']}")
                    cols = st.columns(2)
                    
                    for idx, item in enumerate(cluster.get('options', [])):
                        with cols[idx]:
                            with st.container(border=True):
                                # Visually separate the tiers with color tags
                                if "Premium" in item['tier'] or "Upgrade" in item['tier']:
                                    st.warning(f"💎 **{item['tier']}**")
                                else:
                                    st.success(f"🌱 **{item['tier']}**")
                                    
                                st.markdown(f"## {item.get('emoji', '✨')}")
                                st.markdown(f"**{item['name']}**")
                                st.caption(f"🏬 {item['merchant']}")
                                
                                if item['price'] == 0:
                                    st.markdown("**₹0 (Free / Ad-Supported)**")
                                else:
                                    st.markdown(f"**₹{item['price']}**")
                                
                                if st.button(f"❤️ Select {item['tier'].split()[0]}", key=f"btn_{cluster['category_name']}_{idx}", use_container_width=True):
                                    st.session_state.user_likes.append(item)
                                    st.toast(f"Added {item['name']} to your plan!", icon="✅")
                    st.markdown("---")
                                
            except Exception as e:
                st.error(f"Something went wrong while parsing the data: {str(e)}")
                st.info("Here is the raw text the AI tried to send back so we can debug it:")
                st.write(response.text if 'response' in locals() else "No response from AI.")

    if len(st.session_state.user_likes) > 0:
        st.subheader("🛒 Your Selected Bundle")
        for like in st.session_state.user_likes:
            st.write(f"• **{like['name']}** — ₹{like['price']} ({like['merchant']})")
        
        total_cost = sum(item['price'] for item in st.session_state.user_likes)
        st.info(f"**Total Estimated Cart Value: ₹{total_cost}**")

# ==========================================
# VIEW 2: MERCHANT ANALYTICS HUB
# ==========================================
elif role == "📊 Merchant Hub":
    st.header("📈 Merchant Partner Dashboard")
    st.write("Simulating inbound traffic and tiered conversion metrics.")
    
    match_count = len(st.session_state.user_likes)
    premium_matches = sum(1 for item in st.session_state.user_likes if "Premium" in item.get('tier', ''))
    
    simulated_impressions = (match_count * 1420) + 5400
    take_rate_revenue = sum(item['price'] * 0.05 for item in st.session_state.user_likes)
    
    kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
    kpi_col1.metric("Platform Impressions", f"{simulated_impressions:,}", "+24% AI boost")
    kpi_col2.metric("Premium Conversions", f"{premium_matches}", "High Value")
    kpi_col3.metric("Your Commission Paid (5%)", f"₹{take_rate_revenue:,.2f}")
