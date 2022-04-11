<template>
  <svg
    width="88"
    height="88"
    viewBox="0 0 88 88"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <g filter="url(#filter0_d)">
      <rect
        x="15"
        y="15"
        width="42"
        height="42"
        rx="15"
        fill="url(#paint0_linear)"
      />
    </g>
    <g filter="url(#filter1_bd)">
      <rect
        x="28.5884"
        y="28.5881"
        width="49.4118"
        height="49.4118"
        rx="15"
        fill="url(#paint1_radial)"
      />
    </g>
    <path
      d="M40.9414 64.4118C53.0521 64.4118 65.6473 59.2078 65.6473 42.1765"
      stroke="url(#paint2_linear)"
      stroke-width="4"
      stroke-linecap="round"
    />
    <defs>
      <filter
        id="filter0_d"
        x="0"
        y="0"
        width="72"
        height="72"
        filterUnits="userSpaceOnUse"
        color-interpolation-filters="sRGB"
      >
        <feFlood flood-opacity="0" result="BackgroundImageFix" />
        <feColorMatrix
          in="SourceAlpha"
          type="matrix"
          values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0"
        />
        <feOffset />
        <feGaussianBlur stdDeviation="7.5" />
        <feColorMatrix
          type="matrix"
          values="0 0 0 0 0.447059 0 0 0 0 0.298039 0 0 0 0 0.976471 0 0 0 0.2 0"
        />
        <feBlend
          mode="normal"
          in2="BackgroundImageFix"
          result="effect1_dropShadow"
        />
        <feBlend
          mode="normal"
          in="SourceGraphic"
          in2="effect1_dropShadow"
          result="shape"
        />
      </filter>
      <filter
        id="filter1_bd"
        x="18.5884"
        y="18.5881"
        width="69.4118"
        height="69.4118"
        filterUnits="userSpaceOnUse"
        color-interpolation-filters="sRGB"
      >
        <feFlood flood-opacity="0" result="BackgroundImageFix" />
        <feGaussianBlur in="BackgroundImage" stdDeviation="3" />
        <feComposite
          in2="SourceAlpha"
          operator="in"
          result="effect1_backgroundBlur"
        />
        <feColorMatrix
          in="SourceAlpha"
          type="matrix"
          values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0"
        />
        <feOffset />
        <feGaussianBlur stdDeviation="5" />
        <feColorMatrix
          type="matrix"
          values="0 0 0 0 0.447059 0 0 0 0 0.298039 0 0 0 0 0.976471 0 0 0 0.2 0"
        />
        <feBlend
          mode="normal"
          in2="effect1_backgroundBlur"
          result="effect2_dropShadow"
        />
        <feBlend
          mode="normal"
          in="SourceGraphic"
          in2="effect2_dropShadow"
          result="shape"
        />
      </filter>
      <linearGradient
        id="paint0_linear"
        x1="25.05"
        y1="24.7674"
        x2="54.3037"
        y2="37.6032"
        gradientUnits="userSpaceOnUse"
      >
        <stop stop-color="#724CF9" />
        <stop offset="1" stop-color="#8E6EFD" />
      </linearGradient>
      <radialGradient
        id="paint1_radial"
        cx="0"
        cy="0"
        r="1"
        gradientUnits="userSpaceOnUse"
        gradientTransform="translate(41.559 37.8528) rotate(52.4222) scale(42.6825 72.6259)"
      >
        <stop stop-color="#8E6EFD" stop-opacity="0.7" />
        <stop offset="1" stop-color="#8E6EFD" stop-opacity="0.1" />
      </radialGradient>
      <linearGradient
        id="paint2_linear"
        x1="46.8532"
        y1="47.3475"
        x2="63.4333"
        y2="55.4308"
        gradientUnits="userSpaceOnUse"
      >
        <stop stop-color="white" />
        <stop offset="1" stop-color="#EEEAFD" />
      </linearGradient>
    </defs>
  </svg>
</template>

<script>
export default {};
</script>
