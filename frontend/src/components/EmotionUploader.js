import React, { useState, useEffect } from "react";
import {checkToken, loginUrl, logout, uploadVideo,triggerProcessing,pollStatus,} from "../services/api";

import EmotionBreakdown from "../components/EmotionBreakdown"; // 🆕 animated breakdown

export default function EmotionUploader() {
  const [file, setFile] = useState(null);
  const [playlistUrl, setPlaylistUrl] = useState(null);
  const [detectedEmotion, setDetectedEmotion] = useState(null);
  const [emotionBreakdown, setEmotionBreakdown] = useState(null); // 🆕 store breakdown
  const [progressStage, setProgressStage] = useState(null); // added to track progress stage
  const [loggedIn, setLoggedIn] = useState(false); // added to track Spotify login

  useEffect(() => {
    // check if access token is available
    checkToken().then(setLoggedIn);
  }, []);

  const handleLogin = () => {
    window.location.href = loginUrl();
  };

  const handleLogout = () => {
    logout().then(() => {
      setLoggedIn(false);
      window.location.reload();
    });
  };

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  // polls backend until Colab sends "processing_started"
  const pollForProcessingStarted = () => {
    const interval = setInterval(async () => {
      try {
        const res = await pollStatus();
        if (res.status === "processing_started") {
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
      setProgressStage("uploading"); // show uploading spinner
      setDetectedEmotion(null);
      setEmotionBreakdown(null); //  clear previous

      const uploadRes = await uploadVideo(formData);
      if (!uploadRes.success) {
        setProgressStage(null);
        return alert("Upload failed. Try again.");
      }

      // start polling until colab sends "processing_started"
      pollForProcessingStarted();

      const data = await triggerProcessing();

      if (data.emotion) {
        setDetectedEmotion(data.emotion);
        setEmotionBreakdown(data.breakdown || null); // set breakdown if provided
        setProgressStage("generating_playlist"); // show playlist generation spinner
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
            setProgressStage("done"); // final stage
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
    <section className="relative w-full bg-gray-900 text-white py-20 px-6 text-center">
      {/* Wavy top divider */}
      <div className="absolute top-0 left-0 w-full overflow-hidden leading-none rotate-180 z-10">
        <svg viewBox="0 0 1440 120" className="w-full h-[60px]" preserveAspectRatio="none">
          <path fill="#fb923c" d="M0,0 C360,80 1080,80 1440,0 L1440,120 L0,120 Z" />
        </svg>
      </div>

      {/* Title */}
      <h2 className="text-5xl sm:text-6xl font-extrabold mb-4">Let’s Tune Into Your Emotions</h2>
      <p className="text-lg sm:text-xl text-gray-300 mb-8 max-w-2xl mx-auto">
        Login with Spotify (optional), upload a video, and let the AI read your mood to craft a playlist just for you.
      </p>

      {/* 🎵 Spotify login/logout */}
      <div className="mb-6 flex justify-center">
        {loggedIn ? (
          <button
            onClick={handleLogout}
            className="bg-red-500 hover:bg-red-600 px-4 py-2 rounded-full text-sm shadow"
          >
            Logout of Spotify
          </button>
        ) : (
          <button
            onClick={handleLogin}
            className="bg-green-500 hover:bg-green-600 px-4 py-2 rounded-full text-sm shadow"
          >
            Login with Spotify
          </button>
        )}
      </div>

      {/* Upload */}
      <div
        id="emotion-form"
        className="flex flex-col sm:flex-row justify-center items-center gap-4 mt-4"
      >
        <input
          type="file"
          accept="video/*"
          onChange={handleFileChange}
          className="w-72 sm:w-96 px-4 py-2 rounded-2xl bg-white text-black shadow"
        />
        <button
          onClick={handleUploadAndProcess}
          className="px-6 py-2 bg-blue-500 rounded-lg shadow hover:bg-blue-600"
        >
          Upload & Process Video
        </button>
      </div>

      {/*  spinner stage indicators */}
      <div className="flex justify-center mt-4">
        {progressStage === "uploading" && (
          <div className="text-yellow-300 flex items-center gap-2">
            <span className="animate-spin inline-block w-4 h-4 border-2 border-yellow-300 border-t-transparent rounded-full"></span>
            Uploading video...
          </div>
        )}
        {progressStage === "analyzing" && (
          <div className="text-blue-300 flex items-center gap-2">
            <span className="animate-spin inline-block w-4 h-4 border-2 border-blue-300 border-t-transparent rounded-full"></span>
            Analyzing emotion...
          </div>
        )}
        {progressStage === "generating_playlist" && (
          <div className="text-pink-300 flex items-center gap-2">
            <span className="animate-spin inline-block w-4 h-4 border-2 border-pink-300 border-t-transparent rounded-full"></span>
            Generating playlist...
          </div>
        )}
        {progressStage === "done" && (
          <div className="text-green-400 font-semibold">✅ Playlist ready!</div>
        )}
      </div>

      {/* emotion breakdown typewriter-style */}
      {emotionBreakdown && (
        <div className="mt-4">
          <EmotionBreakdown breakdown={emotionBreakdown} />
        </div>
      )}

      {/* playlist embed */}
      {playlistUrl && (
        <div className="mt-10 flex justify-center">
          <iframe
            src={playlistUrl}
            width="300"
            height="380"
            allow="encrypted-media"
            className="rounded-lg"
            title="Spotify Playlist"
          ></iframe>
        </div>
      )}
    </section>
  );
}
