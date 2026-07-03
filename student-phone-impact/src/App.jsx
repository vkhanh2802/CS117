import { useState } from 'react'
import './App.css'

const APP_GROUPS = ['Productivity', 'Social', 'Entertainment', 'Gaming', 'System']

const KNOWN_APPS = [
  'VSCode',
  'Notion',
  'Google Docs',
  'YouTube',
  'Facebook',
  'Instagram',
  'TikTok',
  'Discord',
  'Messenger',
  'Chrome',
  'Spotify',
]

const QUESTIONS = [
  {
    id: 'app_name',
    title: 'Bạn đang dùng ứng dụng nào trong phiên học hiện tại?',
    options: [
      { label: 'VSCode', value: 'VSCode' },
      { label: 'Notion', value: 'Notion' },
      { label: 'Google Docs', value: 'Google Docs' },
      { label: 'YouTube', value: 'YouTube' },
      { label: 'Facebook', value: 'Facebook' },
      { label: 'Instagram', value: 'Instagram' },
      { label: 'TikTok', value: 'TikTok' },
      { label: 'Discord', value: 'Discord' },
      { label: 'Messenger', value: 'Messenger' },
      { label: 'Chrome', value: 'Chrome' },
      { label: 'Spotify', value: 'Spotify' },
    ],
  },
  {
    id: 'app_usage_minutes',
    title: 'Thời lượng sử dụng ứng dụng trong phiên này?',
    options: [
      { label: 'Dưới 10 phút', value: 8 },
      { label: '10-30 phút', value: 20 },
      { label: '30-60 phút', value: 45 },
      { label: 'Trên 60 phút', value: 75 },
    ],
  },
  {
    id: 'app_open_count',
    title: 'Số lần mở điện thoại hoặc mở app trong phiên học?',
    options: [
      { label: '0-2 lần', value: 2 },
      { label: '3-5 lần', value: 4 },
      { label: '6-9 lần', value: 8 },
      { label: 'Trên 10 lần', value: 12 },
    ],
  },
  {
    id: 'notification_count',
    title: 'Số thông báo nhận được trong lúc học?',
    options: [
      { label: '0-3 thông báo', value: 2 },
      { label: '4-10 thông báo', value: 7 },
      { label: '11-20 thông báo', value: 15 },
      { label: 'Trên 20 thông báo', value: 25 },
    ],
  },
  {
    id: 'hours_to_deadline',
    title: 'Deadline gần nhất còn bao nhiêu giờ?',
    options: [
      { label: 'Trên 3 ngày', value: 96 },
      { label: '2-3 ngày', value: 60 },
      { label: '24-48 giờ', value: 36 },
      { label: 'Dưới 24 giờ', value: 12 },
    ],
  },
  {
    id: 'task_importance',
    title: 'Mức độ quan trọng của nhiệm vụ hiện tại?',
    options: [
      { label: 'Thấp', value: 'Low' },
      { label: 'Trung bình', value: 'Medium' },
      { label: 'Cao', value: 'High' },
    ],
  },
  {
    id: 'pending_tasks_count',
    title: 'Số đầu việc bạn còn cần hoàn thành?',
    options: [
      { label: '0-1 đầu việc', value: 1 },
      { label: '2-3 đầu việc', value: 3 },
      { label: '4-5 đầu việc', value: 5 },
      { label: 'Trên 5 đầu việc', value: 7 },
    ],
  },
  {
    id: 'task_relevance',
    title: 'Hoạt động/app hiện tại có phục vụ nhiệm vụ chính không?',
    options: [
      { label: 'Related (phù hợp)', value: 'Related' },
      { label: 'Neutral (trung tính)', value: 'Neutral' },
      { label: 'Unrelated (không phù hợp)', value: 'Unrelated' },
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
  const [userConfig, setUserConfig] = useState(() => ({
    t_low: 0.35,
    t_high: 0.7,
    main_task_description: 'Làm bài tập lập trình',
    related_groups: ['Productivity'],
    related_apps_input: 'VSCode, Notion, Google Docs',
    app_group_mapping: {
      VSCode: 'Productivity',
      Notion: 'Productivity',
      'Google Docs': 'Productivity',
      YouTube: 'Entertainment',
      Facebook: 'Social',
      Instagram: 'Social',
      TikTok: 'Entertainment',
      Discord: 'Social',
      Messenger: 'Social',
      Chrome: 'System',
      Spotify: 'Entertainment',
    },
  }))

  const currentQuestion = QUESTIONS[currentIndex]
  const selectedValue = answers[currentQuestion.id]?.value
  const isLastQuestion = currentIndex === QUESTIONS.length - 1
  const progress = Math.round(((currentIndex + 1) / QUESTIONS.length) * 100)

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

    const payload = buildPredictionPayload(answers, userConfig)

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

  function handleConfigChange(fieldName, value) {
    setUserConfig((previous) => ({
      ...previous,
      [fieldName]: value,
    }))
  }

  function handleGroupMappingChange(appName, groupName) {
    setUserConfig((previous) => ({
      ...previous,
      app_group_mapping: {
        ...previous.app_group_mapping,
        [appName]: groupName,
      },
    }))
  }

  function toggleRelatedGroup(groupName) {
    setUserConfig((previous) => {
      const exists = previous.related_groups.includes(groupName)
      return {
        ...previous,
        related_groups: exists
          ? previous.related_groups.filter((group) => group !== groupName)
          : [...previous.related_groups, groupName],
      }
    })
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
          Luồng mới nhận đầy đủ Input theo đề bài: hành vi dùng điện thoại, bối cảnh học tập,
          cấu hình ngưỡng và mapping app-group do người dùng tự định nghĩa.
        </p>

        <div className="model-card">
          <span>Output API</span>
          <strong>Risk score + xác suất</strong>
          <small>Label: Low / Medium / High theo ngưỡng tùy biến</small>
        </div>

        <div className="config-card">
          <h2>Cấu hình phiên học</h2>
          <label>
            Nhiệm vụ chính
            <textarea
              value={userConfig.main_task_description}
              onChange={(event) => handleConfigChange('main_task_description', event.target.value)}
              rows={2}
            />
          </label>

          <div className="threshold-row">
            <label>
              T_low
              <input
                type="number"
                step="0.01"
                min="0"
                max="1"
                value={userConfig.t_low}
                onChange={(event) => handleConfigChange('t_low', event.target.value)}
              />
            </label>
            <label>
              T_high
              <input
                type="number"
                step="0.01"
                min="0"
                max="1"
                value={userConfig.t_high}
                onChange={(event) => handleConfigChange('t_high', event.target.value)}
              />
            </label>
          </div>

          <label>
            Related apps (phân tách bằng dấu phẩy)
            <input
              type="text"
              value={userConfig.related_apps_input}
              onChange={(event) => handleConfigChange('related_apps_input', event.target.value)}
            />
          </label>

          <div>
            <p className="config-title">Related groups</p>
            <div className="chip-grid">
              {APP_GROUPS.map((groupName) => {
                const active = userConfig.related_groups.includes(groupName)
                return (
                  <button
                    key={groupName}
                    type="button"
                    className={`chip-button ${active ? 'active' : ''}`}
                    onClick={() => toggleRelatedGroup(groupName)}
                  >
                    {groupName}
                  </button>
                )
              })}
            </div>
          </div>

          <div>
            <p className="config-title">Bảng mapping app-group</p>
            <div className="mapping-grid">
              {KNOWN_APPS.map((appName) => (
                <label key={appName}>
                  <span>{appName}</span>
                  <select
                    value={userConfig.app_group_mapping[appName]}
                    onChange={(event) => handleGroupMappingChange(appName, event.target.value)}
                  >
                    {APP_GROUPS.map((groupName) => (
                      <option key={groupName} value={groupName}>
                        {groupName}
                      </option>
                    ))}
                  </select>
                </label>
              ))}
            </div>
          </div>
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

function buildPredictionPayload(answers, userConfig) {
  const payload = {}

  Object.entries(answers).forEach(([fieldName, option]) => {
    payload[fieldName] = option.value
  })

  const relatedApps = userConfig.related_apps_input
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean)

  payload.user_config = {
    t_low: Number(userConfig.t_low),
    t_high: Number(userConfig.t_high),
    main_task_description: userConfig.main_task_description,
    related_groups: userConfig.related_groups,
    related_apps: relatedApps,
    app_group_mapping: userConfig.app_group_mapping,
  }

  return payload
}

function ResultPanel({ answers, result, onRestart }) {
  const meta = RESULT_META[result.label] || RESULT_META.Medium
  const scorePercent = Math.round(result.risk_probability * 100)

  return (
    <section className="result-layout">
      <div className={`result-card ${meta.tone}`}>
        <p className="eyebrow">Kết quả dự đoán</p>
        <h1>{meta.title}</h1>
        <div className="level-badge">Mức trì hoãn: {meta.label} ({result.label})</div>
        <p className="intro-copy">
          Risk score: <strong>{result.risk_score}</strong>/100 | Xác suất nguy cơ: <strong>{scorePercent}%</strong>
        </p>

        <div className="probability-list">
          <div className="probability-row top-probability">
            <span>Xác suất nguy cơ trì hoãn</span>
            <strong>{scorePercent}%</strong>
            <div className="probability-track">
              <div style={{ width: `${scorePercent}%` }} />
            </div>
          </div>
          <div className="probability-row">
            <span>Ngưỡng Low</span>
            <strong>{Math.round(result.thresholds_applied.t_low * 100)}%</strong>
          </div>
          <div className="probability-row">
            <span>Ngưỡng High</span>
            <strong>{Math.round(result.thresholds_applied.t_high * 100)}%</strong>
          </div>
        </div>

        <button type="button" className="primary-button" onClick={onRestart}>
          Làm lại khảo sát
        </button>
      </div>

      <div className="result-details-grid">
        <section className="white-card">
          <h2>Các tín hiệu model đang chú ý</h2>
          <div className="explanation-list">
            {result.key_factors?.map((item) => (
              <div key={item.factor} className={`explanation-item ${item.tone === 'risk' ? 'risk' : 'positive'}`}>
                <strong>{item.factor} ({item.impact > 0 ? '+' : ''}{item.impact})</strong>
                <p>{item.detail}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="white-card">
          <h2>Gợi ý hỗ trợ phù hợp</h2>
          <div className="answer-list">
            {result.recommendations?.map((item) => (
              <div key={item}>
                <span>Action</span>
                <strong>{item}</strong>
              </div>
            ))}
          </div>

          <h2 className="sub-title">Thông tin đã chọn</h2>
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
