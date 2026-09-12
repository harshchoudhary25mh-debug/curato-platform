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
    st.caption("MPB Project Prototype • v4.0 (Localized India)")

# ==========================================
# VIEW 1: TRUE AI CONSUMER DISCOVERY
# ==========================================
if role == "📱 Consumer Feed":
    st.header("✨ Infinite AI Discovery Feed")
    st.write("Type literally any vibe. Curato spans Music, Web Series, Apparel, Movies, Comics, and Lifestyle.")
    
    # Updated placeholder to feel authentically Indian
    user_vibe = st.text_input(
        "🎯 Describe your exact mood or vibe right now:", 
        placeholder="e.g., Monsoon evening craving some North Indian sweets, looking for a relatable web series and cozy apparel..."
    )
    
    if st.button("Generate My Curato Feed", type="primary") and user_vibe:
        with st.spinner("🧠 AI is hunting across millions of Indian catalogs to match your vibe..."):
            
            # THE CORE DIFFERENCE: Prompt Engineering for Localization
            prompt = f"""
            You are Curato, an advanced e-commerce AI designed specifically for the Indian market. 
            The user's vibe is: "{user_vibe}".
            Recommend exactly 4 highly specific items across a diverse mix of categories (choose from: Web Series, Movies, Indie Music Playlists, Clothing/Apparel, Comics/Graphic Novels, Home Decor, Electronics) that perfectly match this vibe.
            
            CRITICAL INSTRUCTIONS:
            - Ensure the products, media, and brands feel authentically Indian, relatable, and culturally relevant (e.g., local indie brands, popular Indian streaming shows, relatable ethnic or modern fusion wear).
            - Pricing MUST be in Indian Rupees (₹) and represent realistic Indian market pricing.
            - Format your response STRICTLY as a valid JSON array of objects. Do not include any markdown formatting, backticks, or the word 'json'.
            
            Example format:
            [
              {{"name": "Panchayat Season 3", "category": "Web Series", "merchant": "Amazon Prime Video", "price": 299, "match_score": 98, "emoji": "📺"}},
              {{"name": "Oversized Block-Print Cotton Kurta", "category": "Apparel", "merchant": "Myntra", "price": 899, "match_score": 95, "emoji": "👕"}}
            ]
            """
            
            try:
                response = model.generate_content(prompt)
                
                cleaned_response = response.text.strip()
                if cleaned_response.startswith("```"):
                    cleaned_response = "\n".join(cleaned_response.split("\n")[1:-1])
                
                ai_recommendations = json.loads(cleaned_response)
                
                st.success("Feed Generated!")
                cols = st.columns(4)
                
                for idx, item in enumerate(ai_recommendations):
                    with cols[idx]:
                        with st.container(border=True):
                            st.markdown(f"## {item.get('emoji', '✨')}")
                            st.markdown(f"**{item['name']}**")
                            st.caption(f"Category: {item['category']} | 🏬 {item['merchant']}")
                            st.markdown(f"**₹{item['price']}**") # Changed to Rupees
                            st.success(f"🎯 AI Match: {item['match_score']}%")
                            
                            if st.button(f"❤️ Match", key=f"ai_btn_{idx}", use_container_width=True):
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
    st.write("Since Curato now generates infinite items, this dashboard simulates the inbound traffic for registered merchants.")
    
    # Updated simulation metrics for the Indian market scale
    match_count = len(st.session_state.user_likes)
    simulated_impressions = (match_count * 1420) + 5400
    take_rate_revenue = match_count * 125.50 # Simulated Rupee revenue per match
    
    kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
    kpi_col1.metric("Platform Impressions", f"{simulated_impressions:,}", "+24% AI boost")
    kpi_col2.metric("Total Match Clicks", f"{match_count}", "Live")
    kpi_col3.metric("Your Commission Paid", f"₹{take_rate_revenue:,.2f}") # Changed to Rupees
