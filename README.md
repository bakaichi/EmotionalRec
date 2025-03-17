# 🎵 EmotionalRec - Emotion-Based Music Recommendation System

## **📌 Overview**
EmotionalRec is an AI-driven **music recommendation system** that analyzes **facial expressions from video** and recommends **personalized Spotify playlists** based on emotions.

## **🚀 How It Works**
1. **Emotion Detection** 🧠
   - Processes video frames using **DeepFace** and **OpenCV**.
   - Detects emotions (Happy, Sad, Angry, Calm) from facial expressions.
   
2. **Music Recommendation** 🎵
   - Sends the detected emotion to the **FastAPI-based recommender**.
   - Recommender selects **songs/playlists** based on the user's mood.
   - Uses **Spotify API** to fetch recommendations.

3. **Personalized Playlists** 🎧
   - If logged in, the recommender uses the user’s **Spotify listening history**.
   - A **custom playlist** is created and saved to the user's Spotify account.
   
## **🛠 Technologies Used**
- **DeepFace** (Emotion detection)
- **OpenCV** (Video processing)
- **FastAPI** (Backend API)
- **Spotipy** (Spotify API integration)
- **Google Colab** (Running emotion detection model)
- **Ngrok** (Exposing API for Colab)
- **Python** (Core logic)

---

## **🔧 Setup Guide**

### **1️⃣ Clone the Repository**
```bash
git clone https://github.com/your-username/EmotionalRec.git
cd EmotionalRec
```

### **2️⃣ Install Dependencies**
Create a virtual environment and install required packages:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
```

### **3️⃣ Set Up Environment Variables**
Create a `.env` file in the root directory and add your **Spotify API credentials**:
```ini
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
REDIRECT_URI=http://localhost:8000/callback
```

### **4️⃣ Start the Recommender API**
```bash
uvicorn main:app --reload
```
The API should now be running at: **`http://127.0.0.1:8000`**

### **5️⃣ Expose API to Google Colab (Ngrok)**
If running detection on Google Colab, you need to expose the local API:
```bash
ngrok http 8000
```
Copy the **ngrok public URL** and update it in `colab_notebook`.

---

## **📡 Authentication (Spotify OAuth)**
### **Login & Get Access Token**
To authenticate Spotify users:
1. Visit `http://127.0.0.1:8000/login` in your browser.
2. Click the Spotify login link.
3. After logging in, Spotify will redirect you to `http://127.0.0.1:8000/callback` with an **access token**.
4. Token is stored in `.cache` and used for personalized recommendations.

---

## **🚀 Running the Emotion Detector (Google Colab)**
1. Open **Google Colab**
2. Upload `colab_notebook.ipynb`.
3. Modify `RECOMMENDER_API_URL` with your **ngrok link**.
4. Run all cells to start emotion detection.
5. After detection, the system sends the **most common emotion** to the recommender.

---

## **🎯 API Endpoints**
### **📌 Emotion-Based Music Recommendation**
- **`POST /recommend`** – Receive an emotion and return song recommendations.
  - **Payload:** `{ "emotion": "happy", "access_token": "your_token" }`
  - **Response:** List of recommended songs.

- **`POST /create-playlist/{emotion}`** – Creates a Spotify playlist for the user.
  - **Requires Spotify Login.**
  - **Returns:** Playlist link.

### **📌 Spotify Authentication**
- **`GET /login`** – Redirects to Spotify login.
- **`GET /callback`** – Handles OAuth callback, retrieves tokens.

---

## **📌 Contributors**
- **Your Name (@bakaichi)** – Main Developer 💻

---

🔥 **Enjoy Emotion-Based Music Recommendations!** 🎧

