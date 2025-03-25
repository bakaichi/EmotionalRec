# 🎵 EmotionalRec - Emotion-Based Music Recommendation System

## **📌 Overview**
EmotionalRec is an AI-powered **music recommendation system** that analyzes **facial expressions from user-submitted videos** to recommend **personalized Spotify playlists**.

## **🚀 How It Works**
1. **Emotion Detection** 🧠
   - Users upload videos via the frontend.
   - Videos are stored in **Google Drive**.
   - A **Google Colab notebook** polls for new uploads, processes the video using **DeepFace** (RetinaFace specifically), and sends the dominant emotion to the backend.

2. **Backend Processing** ⚙️
   - The **FastAPI backend** receives the emotion via a `POST /colab_callback` route.
   - Internally calls the `/recommend` route to fetch mood-based song suggestions.
   - Optionally creates a Spotify playlist for authenticated users.

3. **Frontend Integration** 💻
   - Built with **React** + **Tailwind CSS**.
   - Users can **log in with Spotify**, **upload a video**, and receive a **playlist embedded on the page**.

## **🛠 Technologies Used**
- **DeepFace** (emotion classification)
- **OpenCV** (video frame processing)
- **Google Colab + PyDrive2** (remote emotion detection)
- **FastAPI** (backend API)
- **Spotipy** (Spotify API for Python)
- **Google Drive API** (video uploads)
- **Ngrok** (expose FastAPI to Colab)
- **React.js** (frontend UI)
- **Tailwind CSS** (styling)

---

## **🔧 Setup Guide**

### **1️⃣ Clone the Repository**
```bash
git clone https://github.com/your-username/EmotionalRec.git
cd EmotionalRec
```

### **2️⃣ Backend Setup**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
```

### **3️⃣ Create .env File**
```ini
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
REDIRECT_URI=http://localhost:8000/callback
```

### **4️⃣ Set Up Google Drive Access**
- Go to [Google Cloud Console](https://console.cloud.google.com/)
- Create a **service account** and download the `.json` key file
- Save it as `gdrive_service_account.json` in root folder
- Share your target Drive folder with the service account email


### **5️⃣ Run the Backend**
```bash
uvicorn main:app --reload
```

### **6️⃣ Run the Frontend**
```bash
cd frontend
npm install
npm run start
```

---

## **🚀 Colab Notebook Setup**
1. Open `colab_notebook.ipynb`
2. Mount Google Drive
3. Ensure `upload_folder` points to shared Drive folder
4. Set `RECOMMENDER_API_URL` to your **ngrok** endpoint (or hosted backend), ngrok is necessary if running locally (needs a key to be used)
5. Run all cells – after emotion is detected, it sends a `POST` to `/colab_callback`

---

## **🎯 API Endpoints**

### ✅ **/upload_video**
Uploads a video file to Google Drive.

### ✅ **/process_latest**
Waits for Colab to detect emotion and send the result.
Returns playlist and recommendations.

### ✅ **/colab_callback**
Internal use by Colab to send emotion + access token (if any).
Calls `/recommend` and stores results temporarily.

### ✅ **/recommend**
Recommends songs and optionally creates a playlist.

### ✅ **/login + /callback**
Spotify login flow using OAuth.

---

## **🌐 CORS Setup**
In `main.py`, frontend has to be given access via:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```
This makes sure that requests from the React app can be processed by the FastAPI backend - due to 2 different local servers.

---

## **🧪 Example Flow**
1. User logs in with Spotify.
2. Uploads a video through frontend.
3. Video is uploaded to Google Drive.
4. Colab processes the video, detects emotion.
5. Sends emotion + token to backend.
6. Backend sends back a playlist.
7. Playlis (iFrame) is embedded in the frontend.

---

🔥 **Enjoy Emotion-Based Music Recommendations!** 🎧

