import { ResponsiveBar } from '@nivo/bar'
import { ResponsiveLine } from '@nivo/line'

const COLORS = { danado: '#dc695d', intacto: '#168c71' }
const chartTheme = {
  background: 'transparent',
  text: { fontFamily: 'Inter, ui-sans-serif, sans-serif', fontSize: 11, fill: '#67756c' },
  axis: {
    domain: { line: { stroke: '#d9e5dc', strokeWidth: 1 } },
    ticks: { line: { stroke: '#d9e5dc', strokeWidth: 1 }, text: { fill: '#748078', fontSize: 11 } },
    legend: { text: { fill: '#5f6d63', fontSize: 12 } },
  },
  grid: { line: { stroke: '#e9efea', strokeWidth: 1, strokeDasharray: '3 5' } },
  tooltip: { container: { borderRadius: 10, boxShadow: '0 12px 28px rgba(18, 42, 29, .15)', color: '#172c20', fontSize: 12 } },
}

export default function Semana10Charts({ ejemplos, referencia = ejemplos }) {
  const visibles = ejemplos.map((item) => item.etiqueta)
  const maxIntensidad = Math.max(0.01, ...referencia.flatMap((item) => item.histograma_intensidad)) * 1.12
  const maxLbp = Math.max(0.01, ...referencia.flatMap((item) => item.histograma_lbp)) * 1.12
  const lineData = ejemplos.map((ejemplo) => ({
    id: ejemplo.etiqueta,
    data: ejemplo.histograma_intensidad.map((probabilidad, indice) => ({
      x: indice * 8 + 4,
      y: probabilidad,
    })),
  }))
  const barData = Array.from({ length: 18 }, (_, indice) => ({
    patron: String(indice),
    danado: ejemplos.find((item) => item.etiqueta === 'danado')?.histograma_lbp[indice] ?? 0,
    intacto: ejemplos.find((item) => item.etiqueta === 'intacto')?.histograma_lbp[indice] ?? 0,
  }))

  return (
    <section className="semana10-chart-section" aria-label="Gráficas comparativas de Semana 10">
      <div className="semana10-chart-intro">
        <span className="eyebrow">03 · COMPARACIÓN INTERACTIVA</span>
        <h2>{ejemplos.length === 2 ? 'Dos firmas visuales, lado a lado' : 'Firma visual del paquete seleccionado'}</h2>
        <p>Pasa el cursor para leer cada valor. {ejemplos.length === 2 ? 'Se comparan dos ejemplos de entrenamiento.' : 'Se muestra solo el caso seleccionado.'} No son probabilidades de daño.</p>
        <div className="semana10-chart-legend" aria-label="Leyenda de clases">
          {visibles.includes('danado') && <span><i className="semana10-swatch semana10-swatch--danado" /> Dañado</span>}
          {visibles.includes('intacto') && <span><i className="semana10-swatch semana10-swatch--intacto" /> Intacto</span>}
        </div>
      </div>
      <div className="semana10-chart-grid">
        <article className="semana10-chart-card">
          <div className="semana10-chart-card__heading">
            <span>01 / TONO</span>
            <h3>Histograma de intensidad</h3>
            <p>32 intervalos del gris, desde negro (0) hasta blanco (255).</p>
          </div>
          <div className="semana10-chart-canvas" role="img" aria-label="Líneas comparativas de 32 probabilidades de intensidad para un ejemplo dañado y uno intacto">
            <ResponsiveLine
              data={lineData}
              theme={chartTheme}
              colors={({ id }) => COLORS[id]}
              margin={{ top: 18, right: 18, bottom: 45, left: 48 }}
              xScale={{ type: 'linear', min: 0, max: 256 }}
              yScale={{ type: 'linear', min: 0, max: maxIntensidad }}
              axisBottom={{ tickValues: [0, 64, 128, 192, 256], tickSize: 0, tickPadding: 12, legend: 'Intensidad (0–255)', legendOffset: 38, legendPosition: 'middle' }}
              axisLeft={{ tickSize: 0, tickPadding: 10, tickValues: 4, format: (value) => Number(value).toFixed(2) }}
              enableGridX={false}
              enablePoints={false}
              lineWidth={3}
              curve="monotoneX"
              useMesh
              enableSlices="x"
              animate={false}
            />
          </div>
          <p className="semana10-chart-card__foot">Cada curva suma 1. El desplazamiento tonal puede depender de la iluminación, no del daño.</p>
        </article>
        <article className="semana10-chart-card">
          <div className="semana10-chart-card__heading">
            <span>02 / TEXTURA</span>
            <h3>Patrones locales LBP</h3>
            <p>18 categorías de textura uniforme calculadas en toda la escena.</p>
          </div>
          <div className="semana10-chart-canvas" role="img" aria-label="Barras comparativas de 18 patrones LBP para un ejemplo dañado y uno intacto">
            <ResponsiveBar
              data={barData}
              keys={visibles}
              indexBy="patron"
              groupMode="grouped"
              maxValue={maxLbp}
              theme={chartTheme}
              colors={({ id }) => COLORS[id]}
              margin={{ top: 18, right: 18, bottom: 45, left: 48 }}
              padding={0.28}
              innerPadding={2}
              borderRadius={3}
              axisBottom={{ tickSize: 0, tickPadding: 12, tickValues: ['0', '4', '8', '12', '17'], legend: 'Patrón LBP', legendOffset: 38, legendPosition: 'middle' }}
              axisLeft={{ tickSize: 0, tickPadding: 10, tickValues: 4, format: (value) => Number(value).toFixed(2) }}
              enableGridX={false}
              enableLabel={false}
              animate={false}
              tooltip={({ id, indexValue, value, color }) => <div className="semana10-tooltip"><i style={{ background: color }} /><strong>{id === 'danado' ? 'Dañado' : 'Intacto'}</strong><span>Patrón {indexValue}: {(Number(value) * 100).toFixed(2)} %</span></div>}
            />
          </div>
          <p className="semana10-chart-card__foot">LBP también mide la textura de la banda: no es una lectura exclusiva del cartón.</p>
        </article>
      </div>
    </section>
  )
}
