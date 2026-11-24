// AiCric logo (the supplied artwork, cut to a transparent circle).
// The wordmark "AiCric" is shown as text next to it in the header, so the image has no alt text.
export default function Logo({ size = 46 }) {
  return <img src="/aicric-logo.png" width={size} height={size} alt="" style={{ display: 'block' }} />
}
