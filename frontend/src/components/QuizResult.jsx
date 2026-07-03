import { RotateCcw, Sparkles } from "lucide-react";

export default function QuizResult({ answers, onRestart }) {
  return (
    <section className="rounded-2xl bg-white p-6 shadow-md ring-1 ring-slate-200 sm:p-8">
      <div className="flex items-start gap-4">
        <span className="grid h-12 w-12 shrink-0 place-items-center rounded-2xl bg-mint-100 text-mint-600">
          <Sparkles size={24} />
        </span>
        <div>
          <p className="text-sm font-bold uppercase text-mint-600">Hoàn tất</p>
          <h2 className="mt-1 text-2xl font-extrabold text-slate-900">
            Câu trả lời của bạn đã được lưu
          </h2>
          <p className="mt-2 leading-7 text-slate-600">
            Đây là dữ liệu state có thể gửi tiếp sang API dự đoán hoặc lưu vào
            hệ thống phân tích mức độ trì hoãn.
          </p>
        </div>
      </div>

      <div className="mt-6 space-y-3">
        {answers.map((answer) => (
          <div key={answer.questionId} className="rounded-xl bg-gray-50 p-4 ring-1 ring-slate-200">
            <p className="text-sm font-bold text-slate-500">{answer.questionId}</p>
            <p className="mt-1 font-semibold text-slate-900">{answer.question}</p>
            <p className="mt-2 text-mint-700">
              {answer.optionKey}. {answer.optionLabel}
            </p>
          </div>
        ))}
      </div>

      <button
        type="button"
        onClick={onRestart}
        className="mt-7 inline-flex items-center gap-2 rounded-xl bg-slate-900 px-5 py-3 font-bold text-white transition-all duration-200 hover:bg-slate-700 active:scale-95"
      >
        <RotateCcw size={18} />
        Làm lại
      </button>
    </section>
  );
}
