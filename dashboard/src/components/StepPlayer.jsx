import Icon from './Icon.jsx'

export default function StepPlayer({ index, total, playing, speed, onPlaying, onStep, onReset, onSpeed }) {
  const progress = total > 1 ? (index / (total - 1)) * 100 : 0
  return (
    <div className="player" aria-label="Controles de reproducción de la traza">
      <div className="player-buttons">
        <button className="icon-button icon-button--soft" onClick={onReset} disabled={!total} aria-label="Reiniciar">
          <Icon name="reset" />
        </button>
        <button className="icon-button icon-button--soft" onClick={() => onStep(-1)} disabled={index <= 0} aria-label="Paso anterior">
          <Icon name="back" />
        </button>
        <button className="play-button" onClick={() => onPlaying(!playing)} disabled={!total || index >= total - 1} aria-label={playing ? 'Pausar' : 'Reproducir'}>
          <Icon name={playing ? 'pause' : 'play'} size={20} />
        </button>
        <button className="icon-button icon-button--soft" onClick={() => onStep(1)} disabled={!total || index >= total - 1} aria-label="Paso siguiente">
          <Icon name="next" />
        </button>
      </div>
      <div className="timeline">
        <div className="timeline-labels"><span>Paso {total ? index + 1 : 0}</span><span>{total} estados</span></div>
        <div className="timeline-track" aria-hidden="true"><span style={{ width: `${progress}%` }} /></div>
      </div>
      <label className="speed-select">
        <span>VELOCIDAD</span>
        <select value={speed} onChange={(event) => onSpeed(Number(event.target.value))}>
          <option value={0.5}>0.5×</option>
          <option value={1}>1×</option>
          <option value={2}>2×</option>
          <option value={5}>5×</option>
        </select>
      </label>
    </div>
  )
}
