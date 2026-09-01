const paths = {
  route: <><circle cx="6" cy="19" r="2"/><circle cx="18" cy="5" r="2"/><path d="M6 17V9a4 4 0 0 1 4-4h6"/><path d="m14 13 4 4 4-4"/></>,
  brain: <><path d="M9.5 4.5A3 3 0 0 0 5 7.1 3.5 3.5 0 0 0 5.5 14 3 3 0 0 0 10 17v2"/><path d="M14.5 4.5A3 3 0 0 1 19 7.1a3.5 3.5 0 0 1-.5 6.9A3 3 0 0 1 14 17v2"/><path d="M9.5 4.5c0-1.4 1.1-2.5 2.5-2.5s2.5 1.1 2.5 2.5V19H9.5V4.5Z"/><path d="M5.5 10H9M15 8h4"/></>,
  rules: <><path d="M9 5h11M9 12h11M9 19h11"/><path d="m3 5 1.2 1.2L6.7 3.7M3 12l1.2 1.2 2.5-2.5M3 19l1.2 1.2 2.5-2.5"/></>,
  play: <path d="m8 5 11 7-11 7V5Z"/>,
  pause: <><path d="M9 5v14M15 5v14"/></>,
  back: <><path d="M11 19 4 12l7-7M19 19l-7-7 7-7"/></>,
  next: <><path d="m13 5 7 7-7 7M5 5l7 7-7 7"/></>,
  reset: <><path d="M3 12a9 9 0 1 0 3-6.7L3 8"/><path d="M3 3v5h5"/></>,
  spark: <><path d="m12 3 1.2 3.8L17 8l-3.8 1.2L12 13l-1.2-3.8L7 8l3.8-1.2L12 3Z"/><path d="m5 14 .7 2.3L8 17l-2.3.7L5 20l-.7-2.3L2 17l2.3-.7L5 14ZM19 13l.6 1.4L21 15l-1.4.6L19 17l-.6-1.4L17 15l1.4-.6L19 13Z"/></>,
  alert: <><path d="M12 9v4M12 17h.01"/><path d="M10.3 3.7 2.6 17a2 2 0 0 0 1.7 3h15.4a2 2 0 0 0 1.7-3L13.7 3.7a2 2 0 0 0-3.4 0Z"/></>,
  check: <path d="m5 12 4 4L19 6"/>,
  activity: <path d="M3 12h4l2.5-7 5 14 2.5-7h4"/>,
  menu: <><path d="M4 7h16M4 12h16M4 17h16"/></>,
  close: <><path d="m6 6 12 12M18 6 6 18"/></>,
  lab: <><path d="M9 3h6M10 3v5l-5.8 9.3A2.4 2.4 0 0 0 6.2 21h11.6a2.4 2.4 0 0 0 2-3.7L14 8V3"/><path d="M7.5 15h9"/></>,
  code: <><path d="m8 9-4 3 4 3M16 9l4 3-4 3M14 5l-4 14"/></>,
  document: <><path d="M6 2h8l4 4v16H6z"/><path d="M14 2v5h5M9 12h6M9 16h6"/></>,
  search: <><circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/></>,
  raw: <><path d="M4 5h16v14H4zM8 9l-2 3 2 3M12 15h4"/></>,
}

export default function Icon({ name, size = 18, className = '' }) {
  return (
    <svg
      aria-hidden="true"
      className={className}
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      {paths[name] || paths.spark}
    </svg>
  )
}
