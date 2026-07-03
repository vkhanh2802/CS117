import Papa from "papaparse";

const REQUIRED_COLUMNS = ["ID", "Question", "OptionA", "OptionB", "OptionC", "OptionD"];

export function parseQuestionsCSV(csvText) {
  const parsed = Papa.parse(csvText, {
    header: true,
    skipEmptyLines: true,
    transformHeader: (header) => header.trim(),
    transform: (value) => value.trim(),
  });

  if (parsed.errors.length > 0) {
    throw new Error(parsed.errors[0].message);
  }

  const fields = parsed.meta.fields || [];
  const missingColumns = REQUIRED_COLUMNS.filter((column) => !fields.includes(column));
  if (missingColumns.length > 0) {
    throw new Error(`CSV thiếu cột: ${missingColumns.join(", ")}`);
  }

  return parsed.data.map((row, index) => ({
    id: row.ID || `Q${index + 1}`,
    question: row.Question,
    options: [
      { key: "A", label: row.OptionA },
      { key: "B", label: row.OptionB },
      { key: "C", label: row.OptionC },
      { key: "D", label: row.OptionD },
    ].filter((option) => option.label),
  }));
}

export async function loadQuestionsFromCSV(path = "/questions.csv") {
  const response = await fetch(path);
  if (!response.ok) {
    throw new Error("Không thể tải file câu hỏi CSV.");
  }

  const csvText = await response.text();
  return parseQuestionsCSV(csvText);
}
