import React from "react";
import Header from "./components/Header";
import EmotionUploader from "./components/EmotionUploader";
import IntroSection from "./components/IntroSection";

export default function App() {
  return (
    <div className="bg-gray-900 text-white min-h-screen w-full">
      <Header />
      <IntroSection/>
      <EmotionUploader />
    </div>
  );
}