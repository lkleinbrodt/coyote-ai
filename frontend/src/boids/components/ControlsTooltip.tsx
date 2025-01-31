export function ControlsTooltip() {
  return (
    <div className="controls-tooltip">
      <h3>How to fly</h3>
      <div className="control-section hover-content">
        <div className="control-group">
          <div className="key-group">
            <div className="key">↑</div>
            <div className="key-row">
              <div className="key">←</div>
              <div className="key">↓</div>
              <div className="key">→</div>
            </div>
          </div>
          <span>Rotate Camera</span>
        </div>

        <div className="control-group">
          <div className="key-group">
            <div className="key">W</div>
            <div className="key-row">
              <div className="key">A</div>
              <div className="key">S</div>
              <div className="key">D</div>
            </div>
          </div>
          <span>Move Camera</span>
        </div>

        <div className="control-group">
          <div className="key-row">
            <div className="key">Q</div>
            <div className="key">E</div>
          </div>
          <span>Up / Down</span>
        </div>

        <div className="control-group">
          <div className="key-row">
            <div className="key">Space</div>
          </div>
          <span>Reset</span>
        </div>
      </div>
    </div>
  );
}
