import React from "react";

export default function Header() {
  const scrollToForm = () => {
    document
      .getElementById("emotion-form")
      .scrollIntoView({ behavior: "smooth" });
  };

  return (
    <section className="relative w-full h-screen flex flex-col justify-center items-center text-center bg-yellow-400 overflow-hidden">
      {/* animated blob */}
      <div
        className="absolute bottom-0 w-[400px] h-[400px] bg-pink-400 rounded-full blur-3xl opacity-70 animate-pulse"
        style={{ zIndex: 0 }}
      ></div>

      {/* Main Title */}
      <h1 className="mt-20 text-6xl sm:text-8xl font-extrabold text-gray-900 mb-4 z-10">
        EmotionalRec
      </h1>

      {/* Subtitle */}
      <p className="text-lg sm:text-xl text-gray-800 mb-6 z-10">
        Let your Face Choose The Music
      </p>

      {/* Button */}
      <button
        onClick={scrollToForm}
        className="z-10 bg-black text-white px-6 py-3 rounded-full hover:scale-105 transition"
      >
        Generate Your Playlist
      </button>

      {/* Hero Image */}
      <img
        src="/hero.png"
        alt="dancing mascot"
        className="mt-12 w-full max-w z-10"
      />

      {/* Wavy Divider */}
      <div className="absolute bottom-0 left-0 w-full overflow-hidden leading-none z-10">
        <svg
          viewBox="0 0 1440 120"
          xmlns="http://www.w3.org/2000/svg"
          className="w-full h-[50px] drop-shadow-lg"
          preserveAspectRatio="none"
        >
          <path
            fill="#fb923c" 
            d="M0,0 C360,80 1080,80 1440,0 L1440,120 L0,120 Z"
          />
        </svg>
      </div>
    </section>
  );
}
