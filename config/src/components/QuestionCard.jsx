import { CheckCircle2 } from "lucide-react";

export default function QuestionCard({ question, selectedOption, onSelect }) {
  return (
    <article className="rounded-2xl bg-white p-6 shadow-md ring-1 ring-slate-200 sm:p-8">
      <p className="mb-3 text-sm font-bold uppercase text-mint-600">{question.id}</p>
      <h2 className="text-2xl font-extrabold leading-snug text-slate-900 sm:text-3xl">
        {question.question}
      </h2>

      <div className="mt-7 grid gap-3 sm:grid-cols-2">
        {question.options.map((option) => {
          const isSelected = selectedOption?.key === option.key;

          return (
            <button
              key={option.key}
              type="button"
              onClick={() => onSelect(option)}
              className={[
                "flex min-h-20 items-center gap-3 rounded-xl border px-4 py-4 text-left font-semibold shadow-sm",
                "transition-all duration-200 active:scale-95",
                isSelected
                  ? "border-mint-500 bg-mint-50 text-mint-700"
                  : "border-slate-200 bg-white text-slate-700 hover:border-skysoft-500 hover:bg-blue-50",
              ].join(" ")}
            >
              <span
                className={[
                  "grid h-9 w-9 shrink-0 place-items-center rounded-full text-sm font-extrabold",
                  isSelected ? "bg-mint-500 text-white" : "bg-slate-100 text-slate-600",
                ].join(" ")}
              >
                {isSelected ? <CheckCircle2 size={19} /> : option.key}
              </span>
              <span>{option.label}</span>
            </button>
          );
        })}
      </div>
    </article>
  );
}
