import { useEffect, useMemo, useState } from "react";
import { ArrowRight, BrainCircuit, Loader2 } from "lucide-react";
import ProgressBar from "./components/ProgressBar.jsx";
import QuestionCard from "./components/QuestionCard.jsx";
import QuizResult from "./components/QuizResult.jsx";
import { loadQuestionsFromCSV } from "./utils/parseCSV.js";

const MODEL_FLOW = [
  "Đọc dữ liệu CSV",
  "Chuẩn hóa đặc trưng",
  "Dự đoán mức trì hoãn",
];

export default function App() {
  const [questions, setQuestions] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answersById, setAnswersById] = useState({});
  const [status, setStatus] = useState("loading");
  const [error, setError] = useState("");

  useEffect(() => {
    loadQuestionsFromCSV()
      .then((items) => {
        setQuestions(items);
        setStatus("ready");
      })
      .catch((err) => {
        setError(err.message);
        setStatus("error");
      });
  }, []);

  const currentQuestion = questions[currentIndex];
  const selectedOption = currentQuestion ? answersById[currentQuestion.id] : null;
  const isLastQuestion = questions.length > 0 && currentIndex === questions.length - 1;

  const answers = useMemo(
    () =>
      questions
        .map((question) => {
          const selected = answersById[question.id];
          if (!selected) return null;

          return {
            questionId: question.id,
            question: question.question,
            optionKey: selected.key,
            optionLabel: selected.label,
          };
        })
        .filter(Boolean),
    [answersById, questions],
  );

  function handleSelect(option) {
    if (!currentQuestion) return;

    setAnswersById((previousAnswers) => ({
      ...previousAnswers,
      [currentQuestion.id]: option,
    }));
  }

  function handleNext() {
    if (!selectedOption) return;

    if (isLastQuestion) {
      setStatus("done");
      return;
    }

    setCurrentIndex((index) => index + 1);
  }

  function handleRestart() {
    setAnswersById({});
    setCurrentIndex(0);
    setStatus("ready");
  }

  return (
    <main className="min-h-screen bg-gray-50 px-4 py-8 font-sans text-slate-900 sm:px-6 lg:px-8">
      <section className="mx-auto grid max-w-6xl gap-8 lg:grid-cols-[0.86fr_1.14fr] lg:items-start">
        <aside className="lg:sticky lg:top-8">
          <div className="inline-flex items-center gap-2 rounded-full bg-mint-50 px-4 py-2 text-sm font-extrabold uppercase text-mint-600 ring-1 ring-mint-100">
            <BrainCircuit size={18} />
            UIT CS117 Project
          </div>

          <h1 className="mt-5 text-4xl font-black leading-tight text-slate-950 sm:text-5xl">
            Phân tích ảnh hưởng của điện thoại đến việc học
          </h1>

          <p className="mt-5 text-lg leading-8 text-slate-600">
            Trắc nghiệm ngắn giúp sinh viên nhìn lại thói quen dùng điện thoại
            khi học, mức phân tâm và xu hướng trì hoãn trước deadline.
          </p>

          <div className="mt-7 rounded-2xl bg-white p-5 shadow-md ring-1 ring-slate-200">
            <ProgressBar
              current={status === "done" ? questions.length : currentIndex + 1}
              total={questions.length}
            />

            <div className="mt-5 grid grid-cols-3 gap-3 text-center">
              <Metric label="Đã chọn" value={answers.length} />
              <Metric label="Còn lại" value={Math.max(questions.length - answers.length, 0)} />
              <Metric label="Nguồn" value="CSV" />
            </div>
          </div>

          <div className="mt-5 rounded-2xl bg-white p-5 shadow-md ring-1 ring-slate-200">
            <p className="text-sm font-extrabold uppercase text-slate-500">
              Luồng xử lý model
            </p>
            <div className="mt-4 space-y-3">
              {MODEL_FLOW.map((item, index) => (
                <div key={item} className="flex items-center gap-3 text-sm font-semibold text-slate-700">
                  <span className="grid h-7 w-7 place-items-center rounded-full bg-skysoft-50 text-xs font-black text-skysoft-600">
                    {index + 1}
                  </span>
                  {item}
                </div>
              ))}
            </div>
          </div>
        </aside>

        <section className="min-h-[520px]">
          {status === "loading" && (
            <div className="grid min-h-96 place-items-center rounded-2xl bg-white shadow-md ring-1 ring-slate-200">
              <div className="flex items-center gap-3 font-bold text-slate-600">
                <Loader2 className="animate-spin text-mint-600" size={22} />
                Đang tải câu hỏi...
              </div>
            </div>
          )}

          {status === "error" && (
            <div className="rounded-2xl bg-red-50 p-6 font-semibold text-red-700 ring-1 ring-red-200">
              {error}
            </div>
          )}

          {status === "ready" && currentQuestion && (
            <div className="space-y-5 transition-all duration-300">
              <QuestionCard
                question={currentQuestion}
                selectedOption={selectedOption}
                onSelect={handleSelect}
              />

              <div className="flex justify-end">
                <button
                  type="button"
                  disabled={!selectedOption}
                  onClick={handleNext}
                  className="inline-flex items-center gap-2 rounded-xl bg-mint-600 px-6 py-3 font-bold text-white shadow-md transition-all duration-200 hover:bg-mint-500 active:scale-95 disabled:cursor-not-allowed disabled:bg-slate-300 disabled:active:scale-100"
                >
                  {isLastQuestion ? "Xem kết quả" : "Câu tiếp theo"}
                  <ArrowRight size={18} />
                </button>
              </div>
            </div>
          )}

          {status === "done" && <QuizResult answers={answers} onRestart={handleRestart} />}
        </section>
      </section>
    </main>
  );
}

function Metric({ label, value }) {
  return (
    <div className="rounded-xl bg-gray-50 px-3 py-4 ring-1 ring-slate-200">
      <p className="text-xl font-black text-slate-900">{value}</p>
      <p className="mt-1 text-xs font-bold uppercase text-slate-500">{label}</p>
    </div>
  );
}
