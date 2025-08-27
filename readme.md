# 🌌 AstroGen

AstroGen is a simple **astrological insight generator**. It provides personalized daily astrological insights, advice in English and Hindi, and LLM-powered summaries with justifications. It also includes a lightweight **RAG-based FAQ system** to answer common astrology-related questions.

---

## 🚀 Features

- **Astrological Profile API**  
  Get your personalized astrological profile based on your details.

- **Birth Chart**  
  Get your personalized birth chart in svg format.

- **Daily Advice (English & Hindi)**  
  Provides actionable daily advice, localized in both English and Hindi.

- **LLM Summary**  
  A concise, AI-generated summary of your daily astrological insights.

- **Astrological Justification**  
  Explains the reasoning behind the generated advice and summaries.

- **FAQ API (RAG System)**  
  A retrieval-augmented generation (RAG) powered endpoint to answer common questions about astrology.

---

## 📡 API Endpoints

### 1. **Astrological Insights**

**Endpoint:** `/astrogen`  
**Description:** Returns your astrological profile, daily advice (English & Hindi), LLM summary, and justifications.

**Sample Request**

```json
{
  "name": "Bugs Bunny",
  "dob": "2000-03-03",
  "time_of_birth": "11:02",
  "city_of_birth": "Mumbai",
  "country_code": "IN"
}
```

**Sample Response:**

```json
{
  "status_code": 200,
  "content": {
    "zodiac": "Pisces",
    "astro_profile": {
      "name": "Bugs Bunny",
      "dob": "2000-03-03",
      "time_of_birth": "11:02:00",
      "city_of_birth": "Mumbai",
      "country_code": null,
      "latitude": 19.054999,
      "longitude": 72.8692035,
      "sun_sign": "Aquarius",
      "moon_sign": "Capricorn",
      "rising_sign": "Taurus",
      "panchang": {
        "tithi": "Krishna Trayodashi",
        "nakshatra": "Shravana",
        "yoga": "Parigha",
        "karana": "Gara",
        "vaar": "Friday"
      },
      "llm_summary": {
        "date": "2025-08-28",
        "summary": "Grounded practicality meets Aquarian innovation today — use steady, patient action to make creative ideas tangible.",
        "summary_translated_hindi": "जमीनी व्यावहारिकता आज एक्वेरियन नवाचार से मिलती है रचनात्मक विचारों को मूर्त बनाने के लिए स्थिर रोगी कार्रवाई का उपयोग करें ।",
        "advice": [
          "Focus on one practical project and break it into clear steps.",
          "Listen first (Shravana) before pitching ideas or negotiating.",
          "Schedule financial or relationship follow-ups in the mid‑day window.",
          "Turn inventive impulses into concrete plans rather than launching something new.",
          "Use Venus‑friendly manners (politeness, small favors) to ease cooperation."
        ],
        "advice_translated_hindi": [
          "एक व्यावहारिक परियोजना पर ध्यान केंद्रित करें और इसे स्पष्ट चरणों में विभाजित करें ।",
          "विचार रखने या बातचीत करने से पहले पहले ( श्रवण ) सुनें ।",
          "मिड - डे विंडो में वित्तीय या संबंध अनुवर्ती कार्रवाई निर्धारित करें ।",
          "कुछ नया शुरू करने के बजाय आविष्कारशील आवेगों को ठोस योजनाओं में बदल दें ।",
          "सहयोग को आसान बनाने के लिए शुक्र के अनुकूल शिष्टाचार का उपयोग करें ।"
        ],
        "lucky_window": "11:00–13:00",
        "caution": "Watch for stubbornness and small delays or gatekeepers slowing progress.",
        "justification": "Sun in Aquarius fuels fresh ideas, Moon in Capricorn and Taurus rising ground you for disciplined, steady execution; Shravana favors listening, while Parigha/Gara and Krishna Trayodashi suggest minor obstacles; Friday (Venus) supports social/financial rapport."
      }
    },
    "birth_chart": "data/9ba18e9c-9410-4dc1-962c-d1f899de46bf.svg",
    "timestamp": "2025-08-27T18:52:09.016101+00:00"
  }
}
```

### 2. **FAQ API Simple RAG**

**Endpoint:** `/astrofaqs`  
**Description:** Returns an answer for your astrological question. (This API is not LLM based and is a very simple RAG system)

**Sample Request**

```json
{
  "query": "What is astrology?"
}
```

**Sample Response:**

```json
{
  "status_code": 200,
  "content": [
    "A: Astrology is an ancient system that studies the positions and movements of celestial bodies, like planets and stars, and interprets their supposed influence on human affairs and the natural world. It is a tool for self-exploration and understanding archetypal energies, not a predictive science."
  ]
}
```

---

## ⚙️ Quick Setup

1. **Run MongoDB**  
   You can either run MongoDB locally or via Docker.  
   To spin up MongoDB using Docker, run:

```bash
  docker run -d --name mongodb -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=<YOUR_USERNAME> \
  -e MONGO_INITDB_ROOT_PASSWORD=<YOUR_PASSWORD> \
  mongodb/mongodb-community-server:latest
```

2. Configure Environment Variables
   Copy .env.example to .env and update the values.
   Example .env file:

```bash
export OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
export DATA_DIR="./data"
export MONGODB_URI="YOUR_MONGODB_URI"
export MONGODB_DATABASE="YOUR_MONGO_DATABASE_NAME"
```

3.	Set Up Python Environment
Create a virtual environment using your preferred tool (venv, pyenv, or conda), then install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate   # On Windows use: .venv\Scripts\activate

pip install -r requirements.txt
```

4. **Download Required Models**  
AstroGen depends on two Hugging Face models. Download them manually (or via the Hugging Face CLI/Python SDK) and place them inside the `models/` directory in the project root.  

- **Translation Model (English → Hindi):**  
  [`ai4bharat/indictrans2-en-indic-dist-200M`](https://huggingface.co/ai4bharat/indictrans2-en-indic-dist-200M)  

- **Embedding Model (for RAG):**  
  [`nomic-ai/nomic-embed-text-v1`](https://huggingface.co/nomic-ai/nomic-embed-text-v1)  

Example (using `huggingface_hub` Python utility):  
```bash
pip install huggingface_hub

huggingface-cli download ai4bharat/indictrans2-en-indic-dist-200M --local-dir ./models/indictrans2-en-indic-dist-200M
huggingface-cli download nomic-ai/nomic-embed-text-v1 --local-dir ./models/nomic-embed-text-v1
```

5. After completing the setup, the APIs defined in main.py can be used.
Start the app using the following commands:
```bash
chmod +x devrun.sh
./devrun.sh
```
The application will be available at:
👉 http://localhost:9999

---

## 🛠️ Technical Details

    •	LLM Summary → Generated using OpenAI’s gpt-4o-mini.
    •	Translation → English → Hindi translations powered by the IndicTrans2 (200M parameters) model.
    •	FAQs (RAG System) → Uses astrology_FAQs.txt as the knowledge base.
    •	Embeddings are generated at runtime when the API is hit.
    •	Embedding model: nomic-embed-text-v1.
