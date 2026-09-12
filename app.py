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
    st.caption("MPB Project Prototype • v8.0 (Hyper-Personalized)")

# ==========================================
# VIEW 1: TRUE AI CONSUMER DISCOVERY
# ==========================================
if role == "📱 Consumer Feed":
    st.header("✨ Infinite AI Discovery Feed")
    st.write("Set your exact preferences. Curato builds complete lifestyle bundles tailored to you.")
    
    # 1. Primary Intent
    user_vibe = st.text_input("🎯 What are you planning or looking for?", placeholder="e.g., Planning to propose to my girlfriend, or hosting a weekend get-together...")
    
    # 2. Advanced Personalization Filters (Collapsible for clean UI)
    with st.expander("⚙️ Advanced Personalization Filters", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            user_budget = st.selectbox(
                "💰 Total Budget Range", 
                ["Under ₹1,000", "₹1,000 - ₹5,000", "₹5,000 - ₹15,000", "₹15,000 - ₹50,000", "₹50,000+", "No Limit"]
            )
            user_location = st.text_input("📍 City / Location Context", placeholder="e.g., Hyderabad, Mumbai, New Delhi...")
            
        with col2:
            user_timeline = st.selectbox(
                "⏳ Urgency / Timeline",
                ["Need it today (Local/Digital only)", "Within a few days", "Planning ahead (Standard shipping fine)"]
            )
            user_context = st.text_area("specific Tastes & Preferences", placeholder="e.g., Prefer North Indian food, love minimalist aesthetics, prefer buying from Amazon or Swiggy...", height=68)
            
    if st.button("Curate My Options", type="primary") and user_vibe:
        with st.spinner(f"🧠 AI is architecting options for {user_budget} in {user_location if user_location else 'your area'}..."):
            
            # The AI prompt now integrates ALL filters
            prompt = f"""
            You are Curato, an advanced e-commerce AI designed for the Indian market. 
            
            USER PROFILE & CONSTRAINTS:
            - Goal: "{user_vibe}"
            - Total Budget: "{user_budget}"
            - Location: "{user_location if user_location else 'India'}"
            - Timeline: "{user_timeline}"
            - Specific Tastes: "{user_context}"
            
            Provide a comprehensive recommendation bundle covering 4 to 5 distinct categories relevant to their goal.
            
            CRITICAL FILTER INSTRUCTIONS:
            - BUDGET: You MUST provide exactly 3 options per category (Value, Mid-Range, Premium) that fit within the {user_budget} total limit.
            - LOCATION/TIMELINE: If the timeline is "today", only suggest local venues in {user_location}, digital goods, or rapid delivery services (like Zomato/Blinkit). Do not suggest standard e-commerce shipping.
            - TASTES: Heavily weigh their specific tastes ({user_context}) when selecting merchants, cuisines, and aesthetics.
            - Pricing MUST be in Indian Rupees (₹).
            - Format STRICTLY as a valid JSON array of objects. Do not include markdown formatting or backticks.
            
            Example format:
            [
              {{
                "category_name": "Venue & Dining",
                "options": [
                  {{"name": "Local Cafe Reservation", "merchant": "Zomato Dine-in", "price": 800, "tier": "Value", "emoji": "☕"}},
                  {{"name": "Premium Rooftop Table", "merchant": "District Dining", "price": 3000, "tier": "Mid-Range", "emoji": "🍽️"}},
                  {{"name": "Luxury Hotel Cabana", "merchant": "Taj Hotels", "price": 8000, "tier": "Premium", "emoji": "🏰"}}
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
                
                st.success("Your Personalized Options are Ready!")
                
                for cluster in ai_data:
                    st.markdown(f"### ✨ {cluster['category_name']}")
                    cols = st.columns(3)
                    
                    for idx, item in enumerate(cluster.get('options', [])[:3]):
                        with cols[idx]:
                            with st.container(border=True):
                                if "Premium" in item['tier'] or "Upgrade" in item['tier']:
                                    st.warning(f"💎 **{item['tier']}**")
                                elif "Mid-Range" in item['tier'] or "Sweet Spot" in item['tier']:
                                    st.info(f"🎯 **{item['tier']}**")
                                else:
                                    st.success(f"🌱 **{item['tier']}**")
                                    
                                st.markdown(f"## {item.get('emoji', '✨')}")
                                st.markdown(f"**{item['name']}**")
                                st.caption(f"🏬 {item['merchant']}")
                                
                                if item['price'] == 0:
                                    st.markdown("**₹0 (Free)**")
                                else:
                                    st.markdown(f"**₹{item['price']}**")
                                
                                if st.button(f"❤️ Select", key=f"btn_{cluster['category_name']}_{idx}", use_container_width=True):
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
    mid_matches = sum(1 for item in st.session_state.user_likes if "Mid" in item.get('tier', ''))
    
    simulated_impressions = (match_count * 1420) + 5400
    take_rate_revenue = sum(item['price'] * 0.05 for item in st.session_state.user_likes)
    
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    kpi_col1.metric("Platform Impressions", f"{simulated_impressions:,}", "+24% AI boost")
    kpi_col2.metric("Mid-Range Conversions", f"{mid_matches}", "Core Segment")
    kpi_col3.metric("Premium Conversions", f"{premium_matches}", "High Value")
    kpi_col4.metric("Your Commission Paid", f"₹{take_rate_revenue:,.2f}")
