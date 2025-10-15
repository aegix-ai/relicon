export function CubeIcon({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M12 2L4 7L12 12L20 7L12 2Z" stroke="currentColor" fill="none" />
      <path d="M4 7V17L12 22V12L4 7Z" stroke="currentColor" fill="none" />
      <path d="M20 7V17L12 22V12L20 7Z" stroke="currentColor" fill="none" />
    </svg>
  )
}
