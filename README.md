<<<<<<< HEAD

=======
>>>>>>> 982f4fd (Update README to professional English format)
🌍 AI-Powered Global Disaster & Climate Risk Analytics Dashboard
An end-to-end data analytics pipeline that collects real-time global disaster, weather, and air quality data, cleans it with pandas, visualizes it in Tableau, and enables natural-language querying through an AI chatbot powered by Groq LLM.
Overview
This project integrates three live public APIs to build a unified dataset of natural disasters, weather conditions, and air quality across major global cities. The cleaned dataset powers both an interactive Tableau dashboard and a Streamlit web app with an AI chatbot that answers questions in plain English and generates charts on demand.
Features
Live data ingestion from three independent APIs (disasters, weather, air quality)
Automated data cleaning — deduplication, missing-value handling, date normalization
Tableau-ready export for building interactive geographic visualizations
AI chatbot (Groq LLM) that answers natural-language questions about the dataset and can pull specific city/record-level data
Dynamic chart generation — the chatbot renders Plotly charts based on the question asked
Streamlit web app wrapping the dataset preview and chatbot in a single interface
Tech Stack
Layer	Tools
Data Collection	Python, requests
Data Processing	pandas
Visualization	Tableau Public, Plotly
AI / LLM	Groq API (Llama 3.3 70B)
Web App	Streamlit
APIs	NASA EONET, OpenWeatherMap, OpenAQ
Project Structure
disaster-dashboard/
├── .env.example          # Template for API keys
├── requirements.txt      # Python dependencies
├── app.py                # Streamlit app entry point
├── src/
│   ├── data_collection.py   # Pulls data from the 3 APIs
│   ├── data_cleaning.py     # Cleans data and builds the Tableau-ready dataset
│   └── chatbot_groq.py      # Groq LLM chatbot logic
└── data/
    ├── raw/                  # Raw API responses
    └── processed/            # Cleaned, analysis-ready CSVs
Getting Started
1. Set up the Python environment
bash
git clone https://github.com/Rajdeep2902/ai-disaster-climate-dashboard.git
cd ai-disaster-climate-dashboard
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
pip install -r requirements.txt
2. Configure API keys
All APIs used are free.
API	Sign up
NASA EONET	No key required (DEMO_KEY works out of the box)
OpenWeatherMap	home.openweathermap.org/users/sign_up
OpenAQ	explore.openaq.org/register
Groq	console.groq.com/keys
bash
cp .env.example .env
# then edit .env and add your keys
3. Collect and clean the data
bash
python src/data_collection.py
python src/data_cleaning.py
This produces data/processed/master_dataset.csv, ready for Tableau or the chatbot.
4. Visualize in Tableau
Open Tableau Public → Connect → Text File → select data/processed/master_dataset.csv. Drag Lat/Lon onto Rows/Columns to build a map, and use Data Type for color-coding.
5. Run the chatbot app
bash
streamlit run app.py
This opens a local web app at http://localhost:8501 where you can:
Preview the cleaned dataset
Ask natural-language questions, e.g.:
"Show disaster count by type"
"What's the weather in Delhi?"
"Show map of all records"
The chatbot answers in plain text via Groq LLM and renders a Plotly chart when relevant.
Sample Output
2,492 total records across disasters, weather, and air quality
2,466 disaster events (wildfires, storms, floods) pulled from NASA EONET
Live weather and air quality for 6 major global cities
Troubleshooting
Issue	Fix
ModuleNotFoundError	Activate the virtual environment, or re-run pip install -r requirements.txt
API returns 401/403	Check that .env exists in the project root and contains valid keys
OpenWeatherMap "Invalid API key"	New account keys can take up to a few hours to activate
Groq model deprecated error	Check console.groq.com for the current model name and update MODEL_NAME in chatbot_groq.py
License
This project is open source and available for personal and educational use.