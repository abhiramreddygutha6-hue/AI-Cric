// Efficiency score (0-100) drawn as a ring: green = strong, gold = middling, red = weak.
export default function ScoreRing({ score, size = 44 }) {
  const stroke = Math.max(3, Math.round(size / 11))
  const r = (size - stroke) / 2
  const c = 2 * Math.PI * r
  const tier = score >= 70 ? 'high' : score >= 40 ? 'mid' : 'low'
  const mid = size / 2
  return (
    <span className={`ring ring-${tier}`} style={{ width: size, height: size }} role="img" aria-label={`Score ${score} out of 100`}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} aria-hidden="true">
        <circle className="ring-bg" cx={mid} cy={mid} r={r} strokeWidth={stroke} fill="none" />
        <circle
          className="ring-fg" cx={mid} cy={mid} r={r} strokeWidth={stroke} fill="none"
          strokeDasharray={`${(score / 100) * c} ${c}`} strokeLinecap="round"
          transform={`rotate(-90 ${mid} ${mid})`}
        />
      </svg>
      <span className="ring-num" style={{ fontSize: size * 0.34 }}>{Math.round(score)}</span>
    </span>
  )
}
