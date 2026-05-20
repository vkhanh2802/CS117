import { useMemo, useState } from 'react'
import './App.css'

const QUESTIONS = [
  {
    id: 'time_of_day',
    title: 'Bạn thường dùng điện thoại vào thời điểm nào khi việc học bị ảnh hưởng?',
    help: 'Model dùng thông tin này để tái tạo đặc trưng thời gian như hour, day_of_week.',
    options: [
      { label: 'Buổi sáng', value: 'Morning' },
      { label: 'Buổi chiều', value: 'Afternoon' },
      { label: 'Buổi tối', value: 'Evening' },
      { label: 'Đêm muộn', value: 'Night', derives: { is_late_night: 1 } },
    ],
  },
  {
    id: 'app_category',
    title: 'Nhóm ứng dụng nào làm bạn dễ mất tập trung nhất?',
    options: [
      { label: 'Mạng xã hội', value: 'Social' },
      { label: 'Game', value: 'Gaming' },
      { label: 'Học tập / năng suất', value: 'Productivity' },
      { label: 'Video / giải trí', value: 'Entertainment' },
      { label: 'Hệ thống / tiện ích', value: 'System' },
    ],
  },
  {
    id: 'duration_minutes',
    title: 'Một lần cầm điện thoại khi đang học thường kéo dài bao lâu?',
    options: [
      { label: 'Dưới 10 phút', value: 8 },
      { label: '10-30 phút', value: 20 },
      { label: '30-60 phút', value: 45 },
      { label: 'Trên 60 phút', value: 75 },
    ],
  },
  {
    id: 'unlock_count',
    title: 'Trong một buổi học, bạn mở khóa điện thoại khoảng bao nhiêu lần?',
    options: [
      { label: '1-3 lần', value: 2 },
      { label: '4-6 lần', value: 5 },
      { label: '7-10 lần', value: 8 },
      { label: 'Trên 10 lần', value: 12 },
    ],
  },
  {
    id: 'notification_count',
    title: 'Bạn thường nhận bao nhiêu thông báo trong lúc học?',
    options: [
      { label: '0-3 thông báo', value: 2 },
      { label: '4-10 thông báo', value: 7 },
      { label: '11-20 thông báo', value: 15 },
      { label: 'Trên 20 thông báo', value: 25 },
    ],
  },
  {
    id: 'hours_to_deadline',
    title: 'Deadline gần nhất của bạn còn khoảng bao lâu?',
    options: [
      { label: 'Trên 3 ngày', value: 96 },
      { label: '2-3 ngày', value: 60 },
      { label: 'Trong 24-48 giờ', value: 36 },
      { label: 'Dưới 24 giờ', value: 12 },
    ],
  },
  {
    id: 'task_priority',
    title: 'Nhiệm vụ hiện tại quan trọng ở mức nào?',
    options: [
      { label: 'Thấp', value: 'Low' },
      { label: 'Trung bình', value: 'Medium' },
      { label: 'Cao', value: 'High' },
    ],
  },
  {
    id: 'assignment_count',
    title: 'Hiện bạn còn bao nhiêu bài tập / đầu việc học tập?',
    options: [
      { label: '0-1 việc', value: 1 },
      { label: '2-3 việc', value: 3 },
      { label: '4-5 việc', value: 5 },
      { label: 'Trên 5 việc', value: 7 },
    ],
  },
  {
    id: 'is_class_time',
    title: 'Việc dùng điện thoại này có xảy ra trong giờ học không?',
    options: [
      { label: 'Không', value: 0 },
      { label: 'Có', value: 1 },
    ],
  },
  {
    id: 'is_study_period',
    title: 'Đây có phải khung thời gian bạn dự định dùng để học không?',
    options: [
      { label: 'Không', value: 0 },
      { label: 'Có', value: 1 },
    ],
  },
]

const RESULT_META = {
  Low: {
    label: 'Thấp',
    tone: 'low',
    title: 'Bạn đang kiểm soát khá ổn',
  },
  Medium: {
    label: 'Trung bình',
    tone: 'medium',
    title: 'Có dấu hiệu trì hoãn cần theo dõi',
  },
  High: {
    label: 'Cao',
    tone: 'high',
    title: 'Nguy cơ trì hoãn đang rõ',
  },
}

function App() {
  const [currentIndex, setCurrentIndex] = useState(0)
  const [answers, setAnswers] = useState({})
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const currentQuestion = QUESTIONS[currentIndex]
  const selectedValue = answers[currentQuestion.id]?.value
  const isLastQuestion = currentIndex === QUESTIONS.length - 1
  const progress = Math.round(((currentIndex + 1) / QUESTIONS.length) * 100)

  const payload = useMemo(() => buildPredictionPayload(answers), [answers])

  function handleSelect(option) {
    setAnswers((previousAnswers) => ({
      ...previousAnswers,
      [currentQuestion.id]: option,
    }))
    setError('')
  }

  async function handleNext() {
    if (selectedValue === undefined) return

    if (!isLastQuestion) {
      setCurrentIndex((index) => index + 1)
      return
    }

    await submitPrediction()
  }

  async function submitPrediction() {
    setIsSubmitting(true)
    setError('')

    try {
      const response = await fetch('/api/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Không thể dự đoán kết quả.')
      }

      setResult(data)
    } catch (requestError) {
      setError(
        `${requestError.message} Hãy chắc chắn Flask backend đang chạy ở http://127.0.0.1:5000.`,
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  function handleBack() {
    setCurrentIndex((index) => Math.max(index - 1, 0))
    setError('')
  }

  function handleRestart() {
    setAnswers({})
    setCurrentIndex(0)
    setResult(null)
    setError('')
  }

  if (result) {
    return (
      <main className="app-shell">
        <ResultPanel
          answers={answers}
          result={result}
          onRestart={handleRestart}
        />
      </main>
    )
  }

  return (
    <main className="app-shell">
      <section className="intro-panel">
        <p className="eyebrow">UIT CS117 - Student Phone Impact</p>
        <h1>Dự đoán mức độ trì hoãn từ thói quen dùng điện thoại</h1>
        <p className="intro-copy">
          Câu trả lời của bạn được chuyển thành các feature giống pipeline train model:
          thời điểm, nhóm app, thời lượng, deadline, thông báo và số lần mở khóa.
        </p>

        <div className="model-card">
          <span>Best model</span>
          <strong>XGBoost</strong>
          <small>Label: Low / Medium / High</small>
        </div>
      </section>

      <section className="quiz-panel">
        <div className="progress-row">
          <span>
            Câu {currentIndex + 1}/{QUESTIONS.length}
          </span>
          <span>{progress}%</span>
        </div>
        <div className="progress-track">
          <div className="progress-fill" style={{ width: `${progress}%` }} />
        </div>

        <article className="question-card">
          <p className="question-id">{currentQuestion.id}</p>
          <h2>{currentQuestion.title}</h2>
          {currentQuestion.help && <p className="question-help">{currentQuestion.help}</p>}

          <div className="option-grid">
            {currentQuestion.options.map((option) => {
              const isSelected = selectedValue === option.value

              return (
                <button
                  key={`${currentQuestion.id}-${option.value}`}
                  type="button"
                  className={`option-button ${isSelected ? 'selected' : ''}`}
                  onClick={() => handleSelect(option)}
                >
                  <span className="option-dot">{isSelected ? '✓' : ''}</span>
                  {option.label}
                </button>
              )
            })}
          </div>
        </article>

        {error && <p className="error-message">{error}</p>}

        <div className="action-row">
          <button
            type="button"
            className="secondary-button"
            onClick={handleBack}
            disabled={currentIndex === 0 || isSubmitting}
          >
            Quay lại
          </button>
          <button
            type="button"
            className="primary-button"
            onClick={handleNext}
            disabled={selectedValue === undefined || isSubmitting}
          >
            {isSubmitting ? 'Đang dự đoán...' : isLastQuestion ? 'Dự đoán ngay' : 'Câu tiếp theo'}
          </button>
        </div>
      </section>
    </main>
  )
}

function buildPredictionPayload(answers) {
  const payload = {
    time_of_day: 'Evening',
    app_category: 'Social',
    duration_minutes: 20,
    is_class_time: 0,
    is_study_period: 1,
    is_late_night: 0,
    hours_to_deadline: 48,
    task_priority: 'Medium',
    assignment_count: 2,
    notification_count: 5,
    unlock_count: 4,
  }

  Object.entries(answers).forEach(([fieldName, option]) => {
    payload[fieldName] = option.value

    if (option.derives) {
      Object.assign(payload, option.derives)
    }
  })

  if (payload.time_of_day === 'Night') {
    payload.is_late_night = 1
  }

  return payload
}

function ResultPanel({ answers, result, onRestart }) {
  const meta = RESULT_META[result.label] || RESULT_META.Medium
  const probabilities = result.probabilities || {}
  const maxProbability = Math.max(0, ...Object.values(probabilities))

  return (
    <section className="result-layout">
      <div className={`result-card ${meta.tone}`}>
        <p className="eyebrow">Kết quả dự đoán</p>
        <h1>{meta.title}</h1>
        <div className="level-badge">Mức trì hoãn: {meta.label}</div>
        <p className="intro-copy">{result.advice}</p>

        <div className="probability-list">
          {Object.entries(probabilities).map(([label, value]) => (
            <div
              key={label}
              className={`probability-row ${value === maxProbability ? 'top-probability' : ''}`}
            >
              <span>{RESULT_META[label]?.label || label}</span>
              <strong>{Math.round(value * 100)}%</strong>
              <div className="probability-track">
                <div style={{ width: `${Math.round(value * 100)}%` }} />
              </div>
            </div>
          ))}
        </div>

        <button type="button" className="primary-button" onClick={onRestart}>
          Làm lại khảo sát
        </button>
      </div>

      <div className="result-details-grid">
        <section className="white-card">
          <h2>Các tín hiệu model đang chú ý</h2>
          <div className="explanation-list">
            {result.explanations?.map((item) => (
              <div key={item.title} className={`explanation-item ${item.tone}`}>
                <strong>{item.title}</strong>
                <p>{item.detail}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="white-card">
          <h2>Câu trả lời đã chọn</h2>
          <div className="answer-list">
            {QUESTIONS.map((question) => (
              <div key={question.id}>
                <span>{question.title}</span>
                <strong>{answers[question.id]?.label}</strong>
              </div>
            ))}
          </div>
        </section>
      </div>
    </section>
  )
}

export default App
