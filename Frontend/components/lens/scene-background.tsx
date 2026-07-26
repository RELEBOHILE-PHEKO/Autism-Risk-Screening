export function SceneBackground() {
  return (
    <div className="scene-bg" aria-hidden="true">
      {/* Perspective floor grid receding into the horizon */}
      <div className="scene-grid scene-grid--floor" />
      {/* Perspective ceiling grid */}
      <div className="scene-grid scene-grid--ceiling" />
      {/* Horizon glow band */}
      <div className="scene-horizon" />
      {/* Floating parallax depth motes */}
      <div className="scene-motes">
        {Array.from({ length: 14 }).map((_, i) => (
          <span key={i} className={`mote mote-${i % 7}`} />
        ))}
      </div>
      {/* CRT scanlines for a tech HUD feel */}
      <div className="scene-scanlines" />
      {/* Vignette to keep foreground content readable */}
      <div className="scene-vignette" />
    </div>
  )
}
