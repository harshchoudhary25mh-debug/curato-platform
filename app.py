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
    st.caption("MPB Project Prototype • v7.0 (Personalized Budget Engine)")

# ==========================================
# VIEW 1: TRUE AI CONSUMER DISCOVERY
# ==========================================
if role == "📱 Consumer Feed":
    st.header("✨ Infinite AI Discovery Feed")
    st.write("Curato builds complete lifestyle bundles tailored to your exact budget.")
    
    # 2-Step Personalized Onboarding
    col1, col2 = st.columns(2)
    with col1:
        user_vibe = st.text_input("🎯 What are you planning?", placeholder="e.g., Planning to propose to my girlfriend...")
    with col2:
        user_budget = st.selectbox(
            "💰 What is your total budget range?", 
            ["Under ₹5,000", "₹5,000 - ₹15,000", "₹15,000 - ₹50,000", "₹50,000+", "No Limit"]
        )
    
    if st.button("Curate My Options", type="primary") and user_vibe:
        with st.spinner(f"🧠 AI is architecting 3-tier options within the {user_budget} range..."):
            
            # The AI is now instructed to generate 4-5 categories with 3 tiers each
            prompt = f"""
            You are Curato, an advanced e-commerce AI designed specifically for the Indian market. 
            The user is planning: "{user_vibe}". Their total budget constraint is: "{user_budget}".
            
            Provide a comprehensive recommendation bundle covering at least 4 to 5 distinct categories (e.g., Rings/Gifts, Venues/Dinner, Decor/Flowers, Outfits/Apparel, Music/Entertainment).
            
            Within EACH category, you MUST provide exactly 3 options targeting different slices of their specific budget:
            1. "Value" (Cost-effective, highly affordable)
            2. "Mid-Range" (The sweet spot, balanced quality and price)
            3. "Premium" (The top end of their stated budget)
            
            CRITICAL INSTRUCTIONS:
            - Keep ALL prices strictly within the user's total budget of {user_budget}.
            - Ensure items feel authentically Indian and relatable.
            - Pricing MUST be in Indian Rupees (₹). Use 0 for free digital items.
            - Format your response STRICTLY as a valid JSON array of objects. Do not include markdown formatting, backticks, or the word 'json'.
            
            Example format:
            [
              {{
                "category_name": "Romantic Dinner & Venue",
                "options": [
                  {{"name": "Cozy Cafe Table Setup", "merchant": "Local Cafe", "price": 1500, "tier": "Value", "emoji": "☕"}},
                  {{"name": "Rooftop Candlelight Dinner", "merchant": "District Dining", "price": 4000, "tier": "Mid-Range", "emoji": "🍽️"}},
                  {{"name": "Luxury 5-Star Cabana", "merchant": "Taj Hotels", "price": 12000, "tier": "Premium", "emoji": "🏰"}}
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
                
                # Render the 3-Tier Choice Architecture
                for cluster in ai_data:
                    st.markdown(f"### ✨ {cluster['category_name']}")
                    cols = st.columns(3) # Changed to 3 columns
                    
                    for idx, item in enumerate(cluster.get('options', [])[:3]):
                        with cols[idx]:
                            with st.container(border=True):
                                # Visually separate the tiers with distinct colors
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
