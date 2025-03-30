import React, { useState } from "react";

export default function App() {
  const [file, setFile] = useState(null);
  const [playlistUrl, setPlaylistUrl] = useState(null);
  const [progressStage, setProgressStage] = useState(null); // added to track progress stage

  const handleLogin = () => {
    window.location.href = "http://127.0.0.1:8000/login"; // to be adjusted if hosted externally 
  };

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUploadAndProcess = async () => {
    if (!file) return alert("Please select a video");

    const formData = new FormData();
    formData.append("video", file);

    try {
      // uploading a video video
      setProgressStage("uploading");
      const uploadResponse = await fetch("http://127.0.0.1:8000/upload_video", { // to be adjusted if hosted externally 
        method: "POST",
        body: formData,
      });

      const uploadResult = await uploadResponse.json();
      if (!uploadResult.success) {
        setProgressStage(null);
        return alert("Upload failed. Try again.");
      }

      // trigger processing
      setProgressStage("analyzing");
      const processResponse = await fetch("http://127.0.0.1:8000/process_latest", { // to be adjusted if hosted externally 
        method: "POST",
      });

      const data = await processResponse.json();

      if (data.playlist_created?.playlist_url) {
        const rawUrl = data.playlist_created.playlist_url;
        const parts = rawUrl.split("/playlist/");
        const playlistId = parts[1]?.split("?")[0];

        if (playlistId) {
          const embedUrl = `https://open.spotify.com/embed/playlist/${playlistId}`;
          setPlaylistUrl(embedUrl);
          setProgressStage("done");
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
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-900 text-white p-4">
      <h1 className="text-3xl font-bold mb-4">Emotion-Based Music Recommender</h1>

      <button
        onClick={handleLogin}
        className="mb-6 px-6 py-2 bg-green-500 rounded-lg shadow hover:bg-green-600"
      >
        Login with Spotify
      </button>

      <input
        type="file"
        accept="video/*"
        className="w-96 p-2 rounded bg-white text-black"
        onChange={handleFileChange}
      />

      <button
        onClick={handleUploadAndProcess}
        className="mt-4 px-6 py-2 bg-blue-500 rounded-lg shadow hover:bg-blue-600"
      >
        Upload & Process Video
      </button>

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
      {progressStage === "done" && (
        <div className="mt-4 text-green-400 font-semibold">✅ Playlist ready!</div>
      )}

      {playlistUrl && (
        <div className="mt-6">
          <h2 className="text-xl font-semibold">Generated Playlist:</h2>
          <iframe
            src={playlistUrl}
            width="300"
            height="380"
            allow="encrypted-media"
            className="mt-2 rounded-lg"
          ></iframe>
        </div>
      )}
    </div>
  );
}
