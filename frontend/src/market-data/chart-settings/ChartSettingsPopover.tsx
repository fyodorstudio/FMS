import { useEffect } from 'react'
import {
  defaultChartAppearance,
  type ChartAppearance,
} from './chart-appearance-preference'
import './chart-settings-popover.css'

type ChartSettingsPopoverProps = {
  appearance: ChartAppearance
  onChange: (appearance: ChartAppearance) => void
  onClose: () => void
}

export function ChartSettingsPopover({ appearance, onChange, onClose }: ChartSettingsPopoverProps) {
  useEffect(() => {
    const closeOnEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', closeOnEscape)
    return () => window.removeEventListener('keydown', closeOnEscape)
  }, [onClose])

  return (
    <section className="chart-settings-popover" role="dialog" aria-modal="false" aria-label="Chart settings">
      <header>
        <div>
          <strong>Chart settings</strong>
          <span>Changes apply immediately and remain on this device.</span>
        </div>
        <button type="button" onClick={onClose} aria-label="Close chart settings">×</button>
      </header>

      <div className="chart-settings-content">
        <div className="chart-settings-section">
          <h2>Candles</h2>
          <label className="color-setting">
            <span><strong>Up candle</strong><small>Body, border and wick</small></span>
            <input
              type="color"
              value={appearance.upCandleColor}
              onChange={(event) => onChange({ ...appearance, upCandleColor: event.target.value })}
            />
          </label>
          <label className="color-setting">
            <span><strong>Down candle</strong><small>Body, border and wick</small></span>
            <input
              type="color"
              value={appearance.downCandleColor}
              onChange={(event) => onChange({ ...appearance, downCandleColor: event.target.value })}
            />
          </label>
          <label className="color-setting">
            <span><strong>Current price line</strong><small>Latest candle guide</small></span>
            <input
              type="color"
              value={appearance.priceLineColor}
              onChange={(event) => onChange({ ...appearance, priceLineColor: event.target.value })}
            />
          </label>
        </div>

        <div className="chart-settings-section">
          <h2>Scale and grid</h2>
          <label className="toggle-setting">
            <span><strong>Grid lines</strong><small>Horizontal and vertical guides</small></span>
            <input
              type="checkbox"
              checked={appearance.showGrid}
              onChange={(event) => onChange({ ...appearance, showGrid: event.target.checked })}
            />
          </label>
          <label className="range-setting">
            <span><strong>Default candle spacing</strong><small>{appearance.barSpacing}px</small></span>
            <input
              type="range"
              min="3"
              max="16"
              step="1"
              value={appearance.barSpacing}
              onChange={(event) => onChange({ ...appearance, barSpacing: Number(event.target.value) })}
            />
          </label>
        </div>
      </div>

      <footer>
        <button type="button" onClick={() => onChange(defaultChartAppearance)}>Reset chart settings</button>
      </footer>
    </section>
  )
}
