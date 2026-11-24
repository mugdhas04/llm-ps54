# PS 54 - Recipe Generator from Ingredients

**Problem:** Food gets wasted at home. This app suggests 3 recipes using *only* the ingredients the user already has (plus basic spices), with steps and cook time.

**Stack:** Python, Streamlit, Google Gemini 2.5 Flash (API), python-dotenv.

## How to run
1. Get a free API key from https://aistudio.google.com/apikey
2. Copy `.env.example` to `.env` and paste your key.
3. ```
   pip install -r requirements.txt
   streamlit run app.py
   ```

## How it works
Multiselect + text list of ingredients -> prompt "use only these + basic spices" -> Gemini returns JSON -> app shows 3 recipes with ingredients used, steps and cook time.

## Screenshots
Add 1-2 screenshots here (`screenshots/` folder).
