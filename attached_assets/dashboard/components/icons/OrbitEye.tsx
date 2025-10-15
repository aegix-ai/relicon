export function OrbitEye({ className }: { className?: string }) {
  return (
    <svg
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      {/* Outer orbit circle */}
      <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="1.5" opacity="0.3" />

      {/* Orbiting element - small circle */}
      <circle cx="18" cy="8" r="1.5" fill="currentColor" opacity="0.6">
        <animateTransform
          attributeName="transform"
          type="rotate"
          from="0 12 12"
          to="360 12 12"
          dur="8s"
          repeatCount="indefinite"
        />
      </circle>

      {/* Central eye with star shape */}
      <g>
        {/* Eye outline */}
        <ellipse cx="12" cy="12" rx="5" ry="3.5" stroke="currentColor" strokeWidth="1.5" fill="none" />

        {/* Star-shaped pupil */}
        <path
          d="M12 9.5 L12.5 11 L14 11.5 L12.5 12 L12 13.5 L11.5 12 L10 11.5 L11.5 11 Z"
          fill="currentColor"
          stroke="currentColor"
          strokeWidth="0.5"
          strokeLinejoin="round"
        />

        {/* Glow effect */}
        <circle cx="12" cy="11.5" r="2" fill="currentColor" opacity="0.15" />
      </g>
    </svg>
  )
}
