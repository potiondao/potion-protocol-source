<template>
  <div
    class="
      w-screen
      h-screen
      fixed
      z-[9999]
      inset-0
      flex
      items-center
      justify-center
      bg-deep-black-900 bg-opacity-50
      backdrop-filter backdrop-blur-sm
    "
  >
    <svg class="w-48 h-48 animate-spin" fill="none" viewBox="0 0 150 150">
      <circle
        cx="75"
        cy="75"
        r="69"
        stroke="url(#paint0_radial)"
        stroke-width="12"
      ></circle>
      <defs>
        <radialGradient
          id="paint0_radial"
          cx="0"
          cy="0"
          r="1"
          gradientTransform="rotate(35 -43 50) scale(157.6 268.164)"
          gradientUnits="userSpaceOnUse"
        >
          <stop stop-color="var(--primary-500)" />
          <stop offset="1" stop-color="var(--primary-400)" stop-opacity="0" />
        </radialGradient>
      </defs>
    </svg>
  </div>
</template>
