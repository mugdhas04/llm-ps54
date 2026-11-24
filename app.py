"""PS 54 - Recipe Generator from Ingredients
Takes the ingredients a user already has and asks an LLM (Gemini) for
3 recipes that use ONLY those ingredients + basic spices.
Run:  streamlit run app.py
"""
import json
import os

import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()  # reads GEMINI_API_KEY from the .env file

MODEL = "gemini-3.8-flash"

COMMON_INGREDIENTS = [
    "rice", "wheat flour", "potato", "onion", "tomato", "garlic", "ginger",
    "egg", "milk", "paneer", "curd", "bread", "pasta", "spinach", "carrot",
    "capsicum", "peas", "cauliflower", "lentils (dal)", "chickpeas",
    "butter", "oil", "cheese", "chicken", "banana", "oats",
]

# Spices/staples the LLM is allowed to add on top of the user's list
BASIC_SPICES = "salt, pepper, turmeric, red chilli powder, cumin, coriander powder, garam masala, sugar, water, cooking oil"

PROMPT_TEMPLATE = """You are a practical home-cooking assistant that helps reduce food waste.

The user has ONLY these ingredients: {ingredients}.
Dietary preference: {diet}.
Servings: {servings}.

Rules:
1. Use ONLY the ingredients listed above plus these basic spices/staples: {spices}.
2. Do NOT add any other ingredient (no extra vegetables, sauces, dairy, meat, etc.).
3. Suggest exactly 3 different recipes. You do not have to use every ingredient in every recipe.
4. Keep steps short, numbered and beginner friendly.
5. If it is impossible to make 3 sensible recipes, return as many as are possible (minimum 1).
6. Respect the dietary preference strictly.

Return ONLY valid JSON (no markdown, no commentary) in this format:
{{
  "recipes": [
    {{
      "name": "string",
      "cook_time_minutes": 20,
      "difficulty": "Easy | Medium",
      "ingredients_used": ["string"],
      "spices_used": ["string"],
      "steps": ["string"]
    }}
  ]
}}"""


def build_prompt(ingredients, diet, servings):
    return PROMPT_TEMPLATE.format(
        ingredients=", ".join(ingredients),
        diet=diet,
        servings=servings,
        spices=BASIC_SPICES,
    )


def get_recipes(ingredients, diet, servings, api_key):
    """Call Gemini and return a list of recipe dicts."""
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=MODEL,
        contents=build_prompt(ingredients, diet, servings),
        config=types.GenerateContentConfig(
            temperature=0.7,
            response_mime_type="application/json",
        ),
    )
    text = response.text.strip()
    # Safety: strip ``` fences if the model adds them anyway
    text = text.replace("```json", "").replace("```", "").strip()
    return json.loads(text)["recipes"]


def parse_ingredients(selected, typed):
    """Merge multiselect + comma-separated text, lower-case, remove duplicates."""
    items = list(selected)
    items += [x.strip() for x in typed.replace("\n", ",").split(",")]
    seen, cleaned = set(), []
    for item in items:
        key = item.lower()
        if key and key not in seen:
            seen.add(key)
            cleaned.append(key)
    return cleaned


# ---------------------------- UI ----------------------------
st.set_page_config(page_title="Recipe Generator", page_icon="🍳")
st.title("🍳 Recipe Generator from Ingredients")
st.caption("Tell me what is in your kitchen - I will suggest recipes using only those ingredients (plus basic spices). Less food wasted!")

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error("GEMINI_API_KEY not found. Create a .env file with GEMINI_API_KEY=your_key and restart.")
    st.stop()

selected = st.multiselect("Pick ingredients you have:", COMMON_INGREDIENTS)
typed = st.text_area("Or type more ingredients (comma separated):", placeholder="e.g. beetroot, coconut, curry leaves")

col1, col2 = st.columns(2)
diet = col1.selectbox("Diet", ["No preference", "Vegetarian", "Vegan", "Eggetarian"])
servings = col2.number_input("Servings", min_value=1, max_value=10, value=2)

if st.button("Generate recipes", type="primary"):
    ingredients = parse_ingredients(selected, typed)
    if len(ingredients) < 2:
        st.warning("Please add at least 2 ingredients.")
    else:
        st.write("**Ingredients:** " + ", ".join(ingredients))
        with st.spinner("Cooking up ideas..."):
            try:
                recipes = get_recipes(ingredients, diet, servings, api_key)
            except json.JSONDecodeError:
                st.error("The model returned an unreadable answer. Please click Generate again.")
                recipes = []
            except Exception as e:  # API/network/quota errors
                st.error(f"Could not get recipes: {e}")
                recipes = []

        for i, r in enumerate(recipes, 1):
            with st.expander(f"{i}. {r['name']}  -  ⏱ {r['cook_time_minutes']} min  |  {r['difficulty']}", expanded=True):
                st.markdown("**Ingredients used:** " + ", ".join(r["ingredients_used"]))
                st.markdown("**Spices/staples:** " + ", ".join(r["spices_used"]))
                st.markdown("**Steps:**")
                for n, step in enumerate(r["steps"], 1):
                    st.write(f"{n}. {step}")