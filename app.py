import os
import time
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
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# GET GEMINI API KEY
# ============================================================

API_KEY = None

# For Streamlit Cloud
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass

# For local computer
if not API_KEY:
    API_KEY = os.getenv("GEMINI_API_KEY")


# Stop application if API key is missing
if not API_KEY:
    st.error("❌ Gemini API key not found.")

    st.info(
        "For Streamlit Cloud, add GEMINI_API_KEY in "
        "Manage app → Settings → Secrets."
    )

    st.stop()


# ============================================================
# GEMINI CLIENT
# ============================================================

client = genai.Client(api_key=API_KEY)

MODEL_NAME = "gemini-3.6-flash"


# ============================================================
# MAIN TITLE
# ============================================================

st.title("🌱 Smart Plant Health & Care Assistant")

st.markdown(
    """
### 🤖 AI-Powered Plant Analysis

Upload a photo of your plant and let AI analyze its appearance,
identify the plant, identify possible visible issues, and provide
personalized plant-care recommendations.
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
    type=[
        "jpg",
        "jpeg",
        "png"
    ],
    help="Upload a clear photo of the plant, leaves, stem, or flowers."
)


# ============================================================
# WHEN IMAGE IS UPLOADED
# ============================================================

if uploaded_file is not None:

    image_bytes = uploaded_file.getvalue()

    mime_type = uploaded_file.type


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
- Leaf color
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
- Signs of overwatering
- Signs of underwatering


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

List common pests that may affect this plant and simple
prevention methods.


12. 🦠 Common Diseases

List common diseases that can affect this plant.

Do NOT claim that the plant definitely has a disease unless it is
clearly supported by visible evidence.


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

Give a score from 1 to 10 based on the visible condition of the
plant.

Explain the reason briefly.


16. ⚠️ Important Warning

Mention that AI image analysis is an assistive tool and that serious
plant disease or pest problems should be confirmed by a gardening,
agriculture, or plant-health expert.


Keep the response clear, structured, and beginner-friendly.
"""


        # ====================================================
        # AI ANALYSIS WITH RETRY
        # ====================================================

        with st.spinner(
            "🤖 AI is analyzing your plant image... Please wait."
        ):

            try:

                response = None

                max_attempts = 4


                for attempt in range(max_attempts):

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
                                            mime_type=mime_type
                                        )
                                    ]
                                )
                            ]
                        )


                        # Successful response
                        break


                    except Exception as e:

                        error_text = str(e)


                        # Errors that can be retried
                        transient_error = any(
                            code in error_text
                            for code in [
                                "503",
                                "UNAVAILABLE",
                                "429",
                                "RESOURCE_EXHAUSTED",
                                "500",
                                "502",
                                "504"
                            ]
                        )


                        # If error is not temporary,
                        # immediately show the error
                        if not transient_error:
                            raise


                        # Final attempt
                        if attempt == max_attempts - 1:
                            raise


                        # Retry timing:
                        # 5 seconds
                        # 10 seconds
                        # 20 seconds

                        wait_time = 5 * (2 ** attempt)


                        st.warning(
                            f"""
⚠️ Gemini is temporarily busy.

Retrying automatically...

Attempt {attempt + 2}/{max_attempts}

Please wait approximately {wait_time} seconds.
"""
                        )


                        time.sleep(wait_time)


                # =================================================
                # CHECK RESPONSE
                # =================================================

                if response is None:
                    raise Exception(
                        "Gemini did not return a response."
                    )


                result = response.text


                if not result:

                    st.error(
                        "❌ Gemini returned an empty response."
                    )

                    st.stop()


                # =================================================
                # DISPLAY RESULT
                # =================================================

                st.success(
                    "✅ Plant analysis completed successfully!"
                )


                st.divider()


                st.header("🌱 AI Plant Analysis")


                st.markdown(result)


                st.divider()


                # =================================================
                # CREATE DOWNLOADABLE REPORT
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

This report was generated using AI-assisted
multimodal plant image analysis.

Plant identification and health observations
may not always be certain.

Serious plant disease or pest problems should
be confirmed by a gardening, agriculture,
or plant-health expert.
"""


                # =================================================
                # DOWNLOAD BUTTON
                # =================================================

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

                error_text = str(e)


                # -----------------------------------------------
                # 503 ERROR
                # -----------------------------------------------

                if (
                    "503" in error_text
                    or "UNAVAILABLE" in error_text
                ):

                    st.error(
                        "❌ Gemini is temporarily unavailable."
                    )

                    st.info(
                        """
Gemini is currently experiencing high demand.

Please wait a little and click
"Analyze Plant with AI" again.
"""
                    )


                # -----------------------------------------------
                # 429 ERROR
                # -----------------------------------------------

                elif (
                    "429" in error_text
                    or "RESOURCE_EXHAUSTED" in error_text
                ):

                    st.error(
                        "❌ Gemini API request limit reached."
                    )

                    st.info(
                        """
Too many requests were made in a short period.

Please wait a little before trying again.
"""
                    )


                # -----------------------------------------------
                # OTHER ERRORS
                # -----------------------------------------------

                else:

                    st.error(
                        "❌ AI analysis failed."
                    )

                    st.warning(
                        """
Please check your Gemini API key,
internet connection, and Gemini model
availability.
"""
                    )

                    st.code(error_text)


# ============================================================
# NO IMAGE UPLOADED
# ============================================================

else:

    st.info(
        "👆 Please upload a plant image above "
        "to start the AI analysis."
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()


st.caption(
    "🌱 Smart Plant Health & Care Assistant | "
    "AI-powered multimodal plant analysis"
)