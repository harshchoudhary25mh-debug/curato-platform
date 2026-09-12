import streamlit as st
import pandas as pd
import google.generativeai as genai
import json

# --- Platform Configuration ---
st.set_page_config(page_title="Curato | AI Matchmaking", layout="wide", initial_sidebar_state="expanded")

# --- Initialize Real AI ---
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

if "user_likes" not in st.session_state:
    st.session_state.user_likes = []

# --- Navigation Sidebar ---
with st.sidebar:
    st.image("[https://cdn-icons-png.flaticon.com/512/1162/1162804.png](https://cdn-icons-png.flaticon.com/512/1162/1162804.png)", width=60)
    st.title("Curato OS")
    st.markdown("---")
    role = st.radio("Access Portal:", ["📱 Consumer Feed", "📊 Merchant Hub"])
    st.markdown("---")
    st.caption("MPB Project Prototype • v3.1 (True AI)")

# ==========================================
# VIEW 1: TRUE AI CONSUMER DISCOVERY
# ==========================================
if role == "📱 Consumer Feed":
    st.header("✨ Infinite AI Discovery Feed")
    st.write("Type literally any vibe, mood, or activity. Our AI will curate products across all categories instantly.")
    
    user_vibe = st.text_input("🎯 Describe your exact mood or vibe right now:", placeholder="e.g., Preparing for a marathon in the rain")
    
    if st.button("Generate My Curato Feed", type="primary") and user_vibe:
        with st.spinner("🧠 AI is hunting across millions of domains to match your vibe..."):
            
            # Stricter prompt for the AI
            prompt = f"""
            You are Curato, an advanced e-commerce AI. The user's vibe is: "{user_vibe}".
            Recommend exactly 4 highly specific items across different categories (Fashion, Electronics, Media/Music, Home/Lifestyle) that perfectly match this vibe.
            Format your response STRICTLY as a valid JSON array of objects. Do not include any markdown formatting, backticks, or the word 'json'.
            Example format:
            [
              {{"name": "Neon Desk Lamp", "category": "Home Decor", "merchant": "RetroGlow", "price": 45, "match_score": 98, "emoji": "💡"}}
            ]
            """
            
            try:
                response = model.generate_content(prompt)
                
                # Clean up any sneaky formatting the AI might have added
                cleaned_response = response.text.strip()
                if cleaned_response.startswith("```"):
                    cleaned_response = "\n".join(cleaned_response.split("\n")[1:-1])
                
                # Convert to data
                ai_recommendations = json.loads(cleaned_response)
                
                st.success("Feed Generated!")
                cols = st.columns(4)
                
                for idx, item in enumerate(ai_recommendations):
                    with cols[idx]:
                        with st.container(border=True):
                            st.markdown(f"## {item.get('emoji', '✨')}")
                            st.markdown(f"**{item['name']}**")
                            st.caption(f"Category: {item['category']} | 🏬 {item['merchant']}")
                            st.markdown(f"**${item['price']}**")
                            st.success(f"🎯 AI Match: {item['match_score']}%")
                            
                            if st.button(f"❤️ Match", key=f"ai_btn_{idx}", use_container_width=True):
                                st.session_state.user_likes.append(item)
                                st.toast("Item added to your Taste Vector!", icon="📈")
                                
            except Exception as e:
                # If it fails, this will tell us exactly what went wrong
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
    
    match_count = len(st.session_state.user_likes)
    simulated_impressions = (match_count * 1420) + 5400
    take_rate_revenue = match_count * 12.50
    
    kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
    kpi_col1.metric("Platform Impressions", f"{simulated_impressions:,}", "+24% AI boost")
    kpi_col2.metric("Total Match Clicks", f"{match_count}", "Live")
    kpi_col3.metric("Your Commission Paid", f"${take_rate_revenue:.2f}")
