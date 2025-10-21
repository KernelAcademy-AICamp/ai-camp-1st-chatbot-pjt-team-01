import { useMemo, useState } from "react";
import { api } from "../../lib/api";

type Mode = "mcq" | "free";
type Level = "basic" | "intermediate" | "advanced";
type Topic = "macro" | "finance" | "trade" | "stats";

type ProblemItem = {
  question: string;
  options?: string[];
  answer: string;
  explanation: string;
  topic: string;
  level: Level;
};

type ProblemResponse = {
  items: ProblemItem[];
  topic: string;
  level: Level;
  created_at: string;
};

export default function Problems() {
  const [topic, setTopic] = useState<Topic>("finance");
  const [level, setLevel] = useState<Level>("basic");
  const [mode, setMode] = useState<Mode>("mcq");
  const [count, setCount] = useState<number>(5);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>("");
  const [data, setData] = useState<ProblemResponse | null>(null);
  const isMCQ = useMemo(() => mode === "mcq", [mode]);

  const onGenerate = async () => {
    setLoading(true);
    setError("");
    setData(null);
    try {
      const { data } = await api.post<ProblemResponse>("/problems", {
        topic,
        level,
        count,
        style: mode,
      });
      setData(data);
    } catch (e: any) {
      setError(e.message || "생성 실패");
    } finally {
      setLoading(false);
    }
  };

  const onDownload = () => {
    if (!data) return;
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    const ts = new Date().toISOString().replace(/[:.]/g, "-");
    a.href = url;
    a.download = `problems_${topic}_${level}_${ts}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div style={{ padding: 24, maxWidth: 980, margin: "0 auto" }}>
      <h2 style={{ marginBottom: 16 }}>🧠 문제 생성</h2>

      {/* 옵션 폼 */}
      <div
        style={{
          display: "grid",
          gap: 12,
          gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
          alignItems: "end",
          marginBottom: 16,
        }}
      >
        <div>
          <label>주제(Topic)</label>
          <select value={topic} onChange={(e) => setTopic(e.target.value as Topic)} style={{ width: "100%", padding: 8 }}>
            <option value="macro">macro</option>
            <option value="finance">finance</option>
            <option value="trade">trade</option>
            <option value="stats">stats</option>
          </select>
        </div>

        <div>
          <label>난이도(Level)</label>
          <select value={level} onChange={(e) => setLevel(e.target.value as Level)} style={{ width: "100%", padding: 8 }}>
            <option value="basic">basic</option>
            <option value="intermediate">intermediate</option>
            <option value="advanced">advanced</option>
          </select>
        </div>

        <div>
          <label>형식(Style)</label>
          <select value={mode} onChange={(e) => setMode(e.target.value as Mode)} style={{ width: "100%", padding: 8 }}>
            <option value="mcq">mcq (객관식)</option>
            <option value="free">free (주관식)</option>
          </select>
        </div>

        <div>
          <label>개수(Count)</label>
          <input
            type="number"
            min={1}
            max={20}
            value={count}
            onChange={(e) => setCount(Math.min(20, Math.max(1, Number(e.target.value))))}
            style={{ width: "100%", padding: 8 }}
          />
        </div>

        <div>
          <button onClick={onGenerate} disabled={loading} style={{ padding: "10px 16px", width: "100%" }}>
            {loading ? "생성 중..." : "문제 생성"}
          </button>
        </div>
      </div>

      {/* 상태 표시 */}
      {error && (
        <div style={{ color: "red", marginBottom: 12 }}>
          ⚠️ {error}
        </div>
      )}

      {/* 결과 표시 */}
      {data && (
        <div style={{ display: "grid", gap: 16 }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <h3>결과</h3>
            <button onClick={onDownload}>JSON 다운로드</button>
          </div>

          {/* 표 보기 */}
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr>
                  <th style={th}>#</th>
                  <th style={th}>Question</th>
                  {isMCQ && <th style={th}>Options</th>}
                  <th style={th}>Answer</th>
                  <th style={th}>Explanation</th>
                </tr>
              </thead>
              <tbody>
                {data.items.map((it, idx) => (
                  <tr key={idx}>
                    <td style={td}>{idx + 1}</td>
                    <td style={td}>{it.question}</td>
                    {isMCQ && (
                      <td style={td}>
                        <ul style={{ margin: 0, paddingLeft: 16 }}>
                          {(it.options || []).map((op, i) => (
                            <li key={i}>{op}</li>
                          ))}
                        </ul>
                      </td>
                    )}
                    <td style={td}>{it.answer}</td>
                    <td style={td}>{it.explanation}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* JSON 보기 */}
          <pre style={{ background: "#0b1020", color: "#c9f0ff", padding: 12, borderRadius: 8, overflowX: "auto" }}>
{JSON.stringify(data, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}

const th: React.CSSProperties = {
  borderBottom: "1px solid #ddd",
  textAlign: "left",
  padding: "8px 6px",
  whiteSpace: "nowrap",
  fontWeight: 600,
};
const td: React.CSSProperties = {
  borderBottom: "1px solid #eee",
  textAlign: "left",
  padding: "8px 6px",
  verticalAlign: "top",
};
