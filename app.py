import os
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Smart Plant Health & Care Assistant",
    page_icon="🌱",
    layout="wide"
)


# ============================================================
# LOAD GEMINI API KEY
# ============================================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    st.error("❌ Gemini API key not found.")
    st.info("Please check your .env file.")
    st.stop()


# ============================================================
# GEMINI CLIENT
# ============================================================

client = genai.Client(api_key=API_KEY)

# Updated model
MODEL_NAME = "gemini-3.5-flash"


# ============================================================
# TITLE
# ============================================================

st.title("🌱 Smart Plant Health & Care Assistant")

st.markdown(
    """
    ### 🤖 AI-Powered Plant Analysis

    Upload a photo of your plant and let AI analyze its appearance,
    identify the plant, detect possible visible problems, and provide
    personalized care recommendations.
    """
)

st.divider()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("🌿 Plant Information")

location = st.sidebar.selectbox(
    "📍 Where is the plant located?",
    [
        "Indoor",
        "Outdoor",
        "Balcony",
        "Terrace",
        "Garden"
    ]
)

soil_condition = st.sidebar.selectbox(
    "🌱 Current soil condition",
    [
        "Dry",
        "Moist",
        "Wet",
        "Not Sure"
    ]
)

last_watered = st.sidebar.selectbox(
    "💧 When was it last watered?",
    [
        "Today",
        "Yesterday",
        "2–3 days ago",
        "More than 3 days ago",
        "Not Sure"
    ]
)

st.sidebar.divider()

st.sidebar.info(
    """
    **How it works**

    1. Upload a plant image
    2. Enter plant conditions
    3. Click Analyze Plant
    4. AI examines the image
    5. Get personalized care recommendations
    """
)


# ============================================================
# IMAGE UPLOAD
# ============================================================

st.subheader("📷 Upload Plant Image")

uploaded_file = st.file_uploader(
    "Choose a plant image",
    type=["jpg", "jpeg", "png"],
    help="Upload a clear photo of the plant, leaves, stem, or flowers."
)


# ============================================================
# DISPLAY IMAGE
# ============================================================

if uploaded_file is not None:

    image_bytes = uploaded_file.getvalue()

    file_type = uploaded_file.type

    st.success("✅ Image uploaded successfully!")

    st.image(
        image_bytes,
        caption="Uploaded Plant Image",
        use_container_width=True
    )

    st.divider()


    # ========================================================
    # ANALYZE BUTTON
    # ========================================================

    analyze_button = st.button(
        "🔍 Analyze Plant with AI",
        type="primary",
        use_container_width=True
    )


    if analyze_button:

        with st.spinner(
            "🤖 AI is analyzing your plant image... Please wait."
        ):

            # ====================================================
            # AI PROMPT
            # ====================================================

            prompt = f"""
You are an AI-powered plant health and care assistant.

Analyze the uploaded plant image carefully.

The user has provided the following information:

Plant location: {location}
Soil condition: {soil_condition}
Last watered: {last_watered}

Your task is to identify the plant if possible and provide practical
plant-care recommendations based on BOTH the image and the user's
provided information.

IMPORTANT:
- Do not pretend to be 100% certain if the plant cannot be identified.
- If identification is uncertain, clearly say so.
- Only discuss problems that are visible or reasonably suggested by
  the image.
- Do not claim that a disease is definitely present.
- Use phrases such as "possible", "may indicate", or "appears to be"
  when appropriate.
- Give simple, practical recommendations suitable for a beginner.

Return your answer using exactly these sections:

1. 🌿 Plant Identification
Include:
- Common name
- Scientific name
- Identification confidence

2. 📝 Plant Description
Briefly describe the plant and its visible characteristics.

3. ❤️ Visible Plant Health
Describe:
- Leaf condition
- Color
- Growth
- Stem condition
- Flowers/fruits if visible
- Overall visible health

4. 🚨 Possible Problems
Mention any visible or possible issues such as:
- Yellowing
- Browning
- Wilting
- Spots
- Curling
- Pest damage
- Nutrient deficiency symptoms
- Overwatering
- Underwatering
If there are no obvious problems, say so.

5. 💧 Watering Recommendation
Explain:
- Whether the plant likely needs water
- How often it should normally be watered
- How to check soil moisture
- Signs of overwatering and underwatering

6. ☀️ Sunlight Requirement
Explain:
- Required sunlight
- Indoor/outdoor placement
- Approximate daily sunlight requirement
- Whether the current location is suitable

7. 🌱 Soil Requirement
Explain:
- Suitable soil type
- Drainage requirements
- Recommended soil mixture if appropriate

8. 🌿 Fertilizer Recommendation
Explain:
- Whether fertilizer is needed
- Suitable fertilizer type
- General frequency
- Avoid excessive fertilizer

9. 🌡️ Temperature & Environment
Explain:
- Suitable temperature range
- Humidity requirements if relevant
- Environmental conditions

10. ✂️ Pruning & Maintenance
Explain:
- When to prune
- What parts can be removed
- Basic maintenance steps

11. 🐛 Common Pests
List common pests that may affect this plant and simple prevention methods.

12. 🦠 Common Diseases
List common diseases that can affect this plant.
Do NOT claim that the plant definitely has a disease unless it is clearly
supported by visible evidence.

13. 🌦️ Seasonal Care
Give simple advice for:
- Summer
- Rainy season
- Winter

14. 💡 Personalized Care Tips
Give 5 practical care tips specifically considering:
- The uploaded image
- Plant location
- Soil condition
- Last watering information

15. ⭐ Overall Plant Care Score
Give a score from 1 to 10 based on the visible condition of the plant.
Explain the reason briefly.

16. ⚠️ Important Warning
Mention that AI image analysis is an assistive tool and that serious
plant disease or pest problems should be confirmed by a gardening,
agriculture, or plant-health expert.

Keep the response clear, structured, and beginner-friendly.
"""


            # ====================================================
            # SEND IMAGE + PROMPT TO GEMINI
            # ====================================================

            try:

                response = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=[
                        types.Content(
                            role="user",
                            parts=[
                                types.Part.from_text(
                                    text=prompt
                                ),
                                types.Part.from_bytes(
                                    data=image_bytes,
                                    mime_type=file_type
                                )
                            ]
                        )
                    ]
                )


                # =================================================
                # GET AI RESPONSE
                # =================================================

                result = response.text


                # =================================================
                # DISPLAY RESULTS
                # =================================================

                st.success("✅ Plant analysis completed!")

                st.divider()

                st.header("🌱 AI Plant Analysis")

                st.markdown(result)

                st.divider()


                # =================================================
                # DOWNLOAD REPORT
                # =================================================

                report = f"""
SMART PLANT HEALTH & CARE ASSISTANT
===================================

Plant Location: {location}
Soil Condition: {soil_condition}
Last Watered: {last_watered}

AI ANALYSIS
-----------

{result}

===================================
Generated using AI-assisted image analysis.
Identification and health observations may not be certain.
"""

                st.download_button(
                    label="📥 Download Plant Care Report",
                    data=report,
                    file_name="plant_care_report.txt",
                    mime="text/plain",
                    use_container_width=True
                )


            # ====================================================
            # ERROR HANDLING
            # ====================================================

            except Exception as e:

                st.error("❌ AI analysis failed.")

                st.warning(
                    "Please check your Gemini API key, internet connection, "
                    "and Gemini model availability."
                )

                st.code(str(e))


else:

    st.info(
        "👆 Please upload a plant image above to start the AI analysis."
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "🌱 Smart Plant Health & Care Assistant | "
    "AI-powered multimodal plant analysis"
)