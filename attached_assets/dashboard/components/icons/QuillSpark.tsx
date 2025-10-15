export function QuillSpark({ className }: { className?: string }) {
  return (
    <svg
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      {/* Quill/Pen tip */}
      <path
        d="M4 20 L9 15 L12 12 L15 9 C16 8 17 7 18 6 C18.5 5.5 19 5 19 4.5 C19 4 18.5 3.5 18 3.5 C17.5 3.5 17 4 16.5 4.5 L9 12 L4 20 Z"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
        fill="none"
      />

      {/* Ink line */}
      <path d="M9 15 L4 20" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />

      {/* Spark burst - emanating from the tip */}
      <g opacity="0.8">
        {/* Main spark rays */}
        <path d="M15 9 L17 7" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
        <path d="M16 10 L18.5 9.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
        <path d="M14 10 L14.5 12.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />

        {/* Small accent sparks */}
        <circle cx="17.5" cy="7.5" r="0.8" fill="currentColor" />
        <circle cx="18.5" cy="10" r="0.6" fill="currentColor" />
        <circle cx="15" cy="12.5" r="0.6" fill="currentColor" />
      </g>

      {/* Energy glow */}
      <circle cx="16" cy="9" r="3" fill="currentColor" opacity="0.1" />
    </svg>
  )
}
