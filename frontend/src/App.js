import React, { useState, useEffect } from "react";

export default function App() {
  const [file, setFile] = useState(null);
  const [playlistUrl, setPlaylistUrl] = useState(null);
  const [progressStage, setProgressStage] = useState(null); // added to track progress stage
  const [loggedIn, setLoggedIn] = useState(false); // added to track Spotify login
  const [detectedEmotion, setDetectedEmotion] = useState(null); // added for emotion preview

  const API_BASE = process.env.REACT_APP_API_URL;

  const emotionEmojis = {
    happy: "😄",
    sad: "😢",
    angry: "😠",
    calm: "😌",
    neutral: "😐",
  };

  useEffect(() => {
    // check if access token is available
    fetch(`${API_BASE}/token`)
      .then((res) => {
        if (res.status === 200) {
          setLoggedIn(true);
        }
      })
      .catch(() => {
        setLoggedIn(false);
      });
  }, [API_BASE]);

  const handleLogin = () => {
    window.location.href = `${API_BASE}/login`;
  };

  const handleLogout = () => {
    fetch(`${API_BASE}/logout`, {
      method: "POST",
    })
      .then(() => {
        setLoggedIn(false);
        window.location.reload();
      })
      .catch((err) => {
        console.error("Logout failed:", err);
      });
  };

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  // polls backend until Colab sends "processing_started"
  const pollForProcessingStarted = () => {
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`${API_BASE}/status_check`);
        const json = await res.json();
        if (json.status === "processing_started") {
          clearInterval(interval);
          setProgressStage("analyzing"); // switch to analyzing
        }
      } catch (err) {
        console.error("Polling error:", err);
      }
    }, 2000);
  };

  const handleUploadAndProcess = async () => {
    if (!file) return alert("Please select a video");

    const formData = new FormData();
    formData.append("video", file);

    try {
      setProgressStage("uploading");

      const uploadResponse = await fetch(`${API_BASE}/upload_video`, {
        method: "POST",
        body: formData,
      });

      const uploadResult = await uploadResponse.json();
      if (!uploadResult.success) {
        setProgressStage(null);
        return alert("Upload failed. Try again.");
      }

      // start polling until colab sends "processing_started"
      pollForProcessingStarted();

      const processResponse = await fetch(`${API_BASE}/process_latest`, {
        method: "POST",
      });

      const data = await processResponse.json();

      if (data.emotion) {
        setDetectedEmotion(data.emotion);
        setProgressStage("generating_playlist");
      }

      if (data.playlist_created?.playlist_url) {
        const rawUrl = data.playlist_created.playlist_url;
        const parts = rawUrl.split("/playlist/");
        const playlistId = parts[1]?.split("?")[0];

        if (playlistId) {
          const embedUrl = `https://open.spotify.com/embed/playlist/${playlistId}`;

          // Delay to allow Spotify to sync playlist metadata
          setTimeout(() => {
            setPlaylistUrl(embedUrl);
            setProgressStage("done");
          }, 5000); // 5 seconds delay
        } else {
          setProgressStage(null);
          alert("Failed to extract playlist ID");
        }
      } else {
        setProgressStage(null);
        alert("Failed to generate playlist");
      }
    } catch (error) {
      setProgressStage(null);
      console.error("Error:", error);
      alert("An error occurred while uploading or processing the video.");
    }
  };

  return (
    <div className="relative flex flex-col items-center min-h-screen bg-gray-900 text-white p-4">
      {/* Title */}
      <h1 className="text-[5rem] font-extrabold tracking-tight uppercase text-white drop-shadow-md border-b-4 border-white pb-2 mb-12">
        EmotionalRec
      </h1>

      {/* Top right login/logout */}
      <div className="absolute top-4 right-4 flex gap-2">
        {loggedIn ? (
          <button
            onClick={handleLogout}
            className="px-4 py-1 bg-red-500 hover:bg-red-600 rounded-full text-sm font-medium shadow"
          >
            Logout
          </button>
        ) : (
          <button
            onClick={handleLogin}
            className="px-4 py-1 bg-green-500 hover:bg-green-600 rounded-full text-sm font-medium shadow"
          >
            Login with Spotify
          </button>
        )}
      </div>

      {/* Upload Row */}
      <div className="flex flex-col sm:flex-row items-center gap-4 mt-4">
        <input
          type="file"
          accept="video/*"
          onChange={handleFileChange}
          className="w-72 sm:w-96 px-4 py-2 rounded-2xl bg-white text-black shadow focus:outline-none"
        />
        <button
          onClick={handleUploadAndProcess}
          className="px-6 py-2 bg-blue-500 rounded-lg shadow hover:bg-blue-600"
        >
          Upload & Process Video
        </button>
      </div>

      {/* progress status */}
      {progressStage === "uploading" && (
        <div className="mt-4 text-yellow-300 flex items-center gap-2">
          <span className="animate-spin inline-block w-4 h-4 border-2 border-yellow-300 border-t-transparent rounded-full"></span>
          Uploading video...
        </div>
      )}
      {progressStage === "analyzing" && (
        <div className="mt-4 text-blue-300 flex items-center gap-2">
          <span className="animate-spin inline-block w-4 h-4 border-2 border-blue-300 border-t-transparent rounded-full"></span>
          Analyzing emotion...
        </div>
      )}
      {progressStage === "generating_playlist" && (
        <div className="mt-4 text-pink-300 flex items-center gap-2">
          <span className="animate-spin inline-block w-4 h-4 border-2 border-pink-300 border-t-transparent rounded-full"></span>
          Generating playlist...
        </div>
      )}
      {progressStage === "done" && (
        <div className="mt-4 text-green-400 font-semibold">✅ Playlist ready!</div>
      )}

      {/* detected emotion preview */}
      {detectedEmotion && (
        <div
          className={`rounded-xl px-6 py-4 mt-6 text-white text-center shadow-xl transition-all
            ${
              detectedEmotion === 'happy' ? 'bg-gradient-to-r from-yellow-400 via-pink-400 to-red-400' :
              detectedEmotion === 'sad' ? 'bg-gradient-to-r from-blue-400 via-indigo-500 to-purple-500' :
              detectedEmotion === 'angry' ? 'bg-gradient-to-r from-red-500 via-yellow-600 to-orange-400' :
              detectedEmotion === 'calm' ? 'bg-gradient-to-r from-teal-400 via-blue-300 to-green-300' :
              'bg-gray-600'
            }`}
        >
          <div className="text-xl font-semibold">Detected Emotion:</div>
          <div className="text-5xl">
            {emotionEmojis[detectedEmotion] || "🧠"} {detectedEmotion.charAt(0).toUpperCase() + detectedEmotion.slice(1)}
          </div>
        </div>
      )}

      {/* playlist embed */}
      {playlistUrl && (
        <div className="mt-6">
          <h2 className="text-xl font-semibold">Generated Playlist:</h2>
          <iframe
            src={playlistUrl}
            width="300"
            height="380"
            allow="encrypted-media"
            className="mt-2 rounded-lg"
            title="Spotify Playlist"
          ></iframe>
        </div>
      )}
    </div>
  );
}