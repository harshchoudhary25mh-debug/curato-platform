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
    st.caption("MPB Project Prototype • v8.1 (Universal Engine)")

# ==========================================
# VIEW 1: TRUE AI CONSUMER DISCOVERY
# ==========================================
if role == "📱 Consumer Feed":
    st.header("✨ Infinite AI Discovery Feed")
    st.write("Search for anything from movie night to event planning. Use filters only if you need them.")
    
    # Broad, universal placeholder
    user_vibe = st.text_input(
        "🎯 What are you looking for today?", 
        placeholder="e.g., Sci-fi movies to binge watch, Monsoon reading list, or Planning a birthday..."
    )
    
    # Filters are now COLLAPSED by default and completely optional
    with st.expander("⚙️ Advanced Personalization Filters (Optional)", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            user_budget = st.selectbox(
                "💰 Total Budget Range", 
                ["Any Budget", "Under ₹1,000", "₹1,000 - ₹5,000", "₹5,000 - ₹15,000", "₹15,000 - ₹50,000", "₹50,000+"]
            )
            user_location = st.text_input("📍 City / Location (Optional)", placeholder="e.g., Hyderabad, Mumbai...")
            
        with col2:
            user_timeline = st.selectbox(
                "⏳ Urgency / Timeline",
                ["Anytime / Not applicable", "Need it today (Local/Digital)", "Within a few days", "Planning ahead"]
            )
            user_context = st.text_area("Specific Tastes (Optional)", placeholder="e.g., Prefer indie brands, no horror movies...", height=68)
            
    if st.button("Curate My Options", type="primary") and user_vibe:
        with st.spinner("🧠 AI is hunting across millions of catalogs to match your vibe..."):
            
            # Dynamically build filter instructions ONLY if the user used them
            filter_instructions = ""
            if user_budget != "Any Budget":
                filter_instructions += f"\n- BUDGET: Must fit within {user_budget}. Provide Value, Mid-Range, and Premium tiers."
            else:
                filter_instructions += f"\n- BUDGET: No strict budget. Provide 3 distinct, high-quality options per category."
                
            if user_location:
                filter_instructions += f"\n- LOCATION: Prioritize options available in or highly relevant to {user_location}."
                
            if user_timeline != "Anytime / Not applicable":
                filter_instructions += f"\n- TIMELINE: Must align with '{user_timeline}'."
                
            if user_context:
                filter_instructions += f"\n- TASTES: Strictly incorporate these preferences: {user_context}."

            # The AI prompt adapts to broad searches (like just movies) or complex ones (like events)
            prompt = f"""
            You are Curato, an advanced e-commerce AI designed for the Indian market. 
            
            USER INTENT: "{user_vibe}"
            {filter_instructions}
            
            INSTRUCTIONS:
            - Break the request into 2 to 4 logical sub-categories. (e.g., If they ask for 'Sci-fi movies', sub-categories could be 'Cyberpunk Thrillers', 'Space Operas', etc. If they ask for an event, sub-categories could be 'Decor', 'Venues', 'Gifts').
            - Within EACH category, provide exactly 3 distinct options.
            - Pricing MUST be in Indian Rupees (₹). Use 0 for free digital items/streaming.
            - Format STRICTLY as a valid JSON array of objects. Do not include markdown formatting or backticks.
            
            Example format:
            [
              {{
                "category_name": "Mind-Bending Sci-Fi",
                "options": [
                  {{"name": "Interstellar", "merchant": "Amazon Prime", "price": 0, "tier": "Included in Sub", "emoji": "🌌"}},
                  {{"name": "Blade Runner 2049", "merchant": "Apple TV Rent", "price": 120, "tier": "Standard Rental", "emoji": "🤖"}},
                  {{"name": "Dune (4K Blu-Ray)", "merchant": "Amazon India", "price": 1499, "tier": "Physical Collector", "emoji": "🏜️"}}
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
                                # Dynamic color tags based on keywords
                                if any(word in str(item.get('tier', '')).lower() for word in ['premium', 'upgrade', 'collector', 'luxury']):
                                    st.warning(f"💎 **{item.get('tier', 'Option')}**")
                                elif any(word in str(item.get('tier', '')).lower() for word in ['mid', 'standard', 'sweet']):
                                    st.info(f"🎯 **{item.get('tier', 'Option')}**")
                                else:
                                    st.success(f"🌱 **{item.get('tier', 'Option')}**")
                                    
                                st.markdown(f"## {item.get('emoji', '✨')}")
                                st.markdown(f"**{item['name']}**")
                                st.caption(f"🏬 {item['merchant']}")
                                
                                if item['price'] == 0:
                                    st.markdown("**₹0 (Free / Stream)**")
                                else:
                                    st.markdown(f"**₹{item['price']}**")
                                
                                if st.button(f"❤️ Match", key=f"btn_{cluster['category_name']}_{idx}", use_container_width=True):
                                    st.session_state.user_likes.append(item)
                                    st.toast(f"Added {item['name']} to your Taste Vector!", icon="✅")
                    st.markdown("---")
                                
            except Exception as e:
                st.error(f"Something went wrong while parsing the data: {str(e)}")
                st.info("Here is the raw text the AI tried to send back so we can debug it:")
                st.write(response.text if 'response' in locals() else "No response from AI.")

    if len(st.session_state.user_likes) > 0:
        st.subheader("🛒 Your Taste Vector & Cart")
        for like in st.session_state.user_likes:
            st.write(f"• **{like['name']}** — ₹{like['price']} ({like['merchant']})")
        
        total_cost = sum(item['price'] for item in st.session_state.user_likes)
        st.info(f"**Total Estimated Value: ₹{total_cost}**")
# ==========================================
# VIEW 2: MERCHANT ANALYTICS HUB
# ==========================================
elif role == "📊 Merchant Hub":
    st.header("📈 Merchant Partner Dashboard")
    st.write("Simulating inbound traffic, CAC reduction, and cross-domain analytics.")
    
    # --- TOP KPI BANNER ---
    match_count = len(st.session_state.user_likes)
    premium_matches = sum(1 for item in st.session_state.user_likes if any(word in str(item.get('tier', '')).lower() for word in ['premium', 'upgrade', 'collector', 'luxury']))
    
    simulated_impressions = (match_count * 1420) + 5400
    take_rate_revenue = sum(item['price'] * 0.05 for item in st.session_state.user_likes)
    
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    kpi_col1.metric("Platform Impressions", f"{simulated_impressions:,}", "+24% AI boost")
    kpi_col2.metric("Total Matches", f"{match_count}", "Active")
    kpi_col3.metric("Premium Conversions", f"{premium_matches}", "High Value")
    kpi_col4.metric("Your Commission Paid", f"₹{take_rate_revenue:,.2f}")
    
    st.markdown("---")
    
    # --- CROSS-DOMAIN INSIGHTS (Proving the Data Moat) ---
    st.subheader("🕸️ Cross-Domain Audience Insights")
    st.write("Curato's AI reveals what your matched customers are searching for in *other* categories. Use this to design cross-promotions.")
    
    # Simulated chart data demonstrating cross-category intelligence
    chart_data = pd.DataFrame(
        [45, 25, 20, 10],
        index=["Also looking for Indie Music", "Planning a trip/event", "Buying Tech Gadgets", "Ordering North Indian Food"],
        columns=["Audience Overlap %"]
    )
    st.bar_chart(chart_data, color="#4F46E5")
    
    st.markdown("---")
    
    # --- MONETIZATION & CAC (Proving the Business Model) ---
    st.subheader("⚡ Platform ROI & SaaS Monetization")
    st.info("Activate Curato+ SaaS Subscription to prioritize your catalog in relevant user vibes and access premium data.")
    
    col_a, col_b = st.columns(2)
    with col_a:
        with st.container(border=True):
            st.write("**Subscription Status**")
            saas_toggle = st.toggle("Enable Curato+ (₹2,999/month)", value=True)
            if saas_toggle:
                st.success("✅ Active: Catalog receives a +15% AI Match Boost.")
            else:
                st.warning("❌ Inactive: Standard algorithmic ranking applied.")
                
    with col_b:
        with st.container(border=True):
            st.write("**Customer Acquisition Cost (CAC) Analysis**")
            st.metric("Curato CAC vs. Google/Meta Ads", "₹45 per match", "-82% cheaper")

    # --- INVENTORY PREVIEW ---
    st.write("**Your Top Performing AI Matches (Simulated):**")
    merchant_catalog = pd.DataFrame({
        "Product Category": ["Apparel & Fashion", "Home & Decor", "Food & Beverage", "Media & Entertainment"],
        "AI Impressions": ["2,450", "1,890", "3,100", "1,200"],
        "Match Rate": ["6.2%", "5.8%", "8.1%", "4.5%"],
        "Take-Rate (5%) Paid": ["₹1,250", "₹890", "₹2,100", "₹450"]
    })
    st.dataframe(merchant_catalog, use_container_width=True, hide_index=True)
