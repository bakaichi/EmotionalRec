import React from "react";

export default function IntroSection() {
  return (
    <section className="w-full flex flex-col justify-center items-center text-center bg-orange-400 py-20 px-6">
      {/* Title */}
      <h2 className="text-6xl mt-6 sm:text-8xl font-extrabold text-gray-900 mb-4">
        Want Your Emotions to Build Your Playlist?
      </h2>

      {/* Subtext */}
      <p className="text-lg sm:text-xl text-gray-800 mb-2 max-w-2xl">
        Upload a short video. Let our AI detect your mood and build a playlist tailored to your feelings.
      </p>

      {/* Character image */}
      <img
        src="/intro-section.png"
        alt="emotion mascot"
        className=" max-w-[300px] sm:max-w-[400px] md:max-w-[500px]"
      />
    </section>
  );
}
