export default function LearningHeader({ eyebrow, title, description }) {
  return (
    <header className="learning-header">
      <div>
        <span>{eyebrow}</span>
        <h1>{title}</h1>
        <p>{description}</p>
      </div>
    </header>
  )
}
