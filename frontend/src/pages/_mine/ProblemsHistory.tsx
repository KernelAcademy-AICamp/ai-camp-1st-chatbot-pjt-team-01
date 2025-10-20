import { useEffect, useMemo, useState } from "react";
import { api } from "../../lib/api";

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
  created_at: string; // ISO
};

const topics: Topic[] = ["macro", "finance", "trade", "stats"];
const levels: Level[] = ["basic", "intermediate", "advanced"];

export default function ProblemsHistory() {
  const [topic, setTopic] = useState<"" | Topic>("");
  const [level, setLevel] = useState<"" | Level>("");
  const [limit, setLimit] = useState<number>(10);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>("");
  const [data, setData] = useState<ProblemResponse[]>([]);
  const [expanded, setExpanded] = useState<Record<number, boolean>>({});

  const query = useMemo(() => {
    const params = new URLSearchParams();
    if (topic) params.set("topic", topic);
    if (level) params.set("level", level);
    params.set("limit", String(limit));
    return params.toString();
  }, [topic, level, limit]);

  const fetchList = async () => {
    setLoading(true);
    setError("");
    try {
      const { data } = await api.get<ProblemResponse[]>(`/problems?${query}`);
      setData(data);
      setExpanded({});
    } catch (e: any) {
      setData([]);
      setError(e?.message || "조회 실패");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchList();
  }, [query]);

  const toggle = (idx: number) =>
    setExpanded((prev) => ({ ...prev, [idx]: !prev[idx] }));

  const downloadJSON = (obj: any, name = "problems.json") => {
    const blob = new Blob([JSON.stringify(obj, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = name;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div style={{ padding: 24, maxWidth: 1100, margin: "0 auto" }}>
      <h2 style={{ marginBottom: 8 }}>📚 저장된 문제 보관함</h2>
      <p style={{ marginTop: 0, color: "#8aa", marginBottom: 16 }}>
        MongoDB에 저장된 문제 세트를 불러와 필터링/다운로드할 수 있습니다.
      </p>

      {/* 필터 바 */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
          gap: 12,
          alignItems: "end",
          marginBottom: 16,
        }}
      >
        <div>
          <label>주제(Topic)</label>
          <select
            value={topic}
            onChange={(e) => setTopic(e.target.value as any)}
            style={input}
          >
            <option value="">(전체)</option>
            {topics.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label>난이도(Level)</label>
          <select
            value={level}
            onChange={(e) => setLevel(e.target.value as any)}
            style={input}
          >
            <option value="">(전체)</option>
            {levels.map((lv) => (
              <option key={lv} value={lv}>
                {lv}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label>개수(limit)</label>
          <input
            type="number"
            min={1}
            max={50}
            value={limit}
            onChange={(e) =>
              setLimit(Math.min(50, Math.max(1, Number(e.target.value))))
            }
            style={input}
          />
        </div>

        <div>
          <button onClick={fetchList} disabled={loading} style={btnPrimary}>
            {loading ? "불러오는 중..." : "새로고침"}
          </button>
        </div>
      </div>

      {/* 상태 */}
      {error && (
        <div style={{ color: "salmon", marginBottom: 12 }}>⚠️ {error}</div>
      )}
      {!loading && !error && data.length === 0 && (
        <div style={{ color: "#9ab", marginTop: 24 }}>
          저장된 문제가 없습니다. 먼저 <b>/problems</b>에서 문제를 생성해 주세요.
        </div>
      )}

      {/* 리스트 */}
      <div style={{ display: "grid", gap: 12 }}>
        {data.map((set, idx) => {
          const created = new Date(set.created_at);
          const dateLabel = `${created.toLocaleString()}`;
          const isOpen = !!expanded[idx];

          return (
            <div key={idx} style={card}>
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "1fr auto auto",
                  gap: 8,
                  alignItems: "center",
                }}
              >
                <div>
                  <div style={{ fontWeight: 700, fontSize: 16 }}>
                    {set.topic} · {set.level} · {set.items.length}문항
                  </div>
                  <div style={{ color: "#7fa" }}>{dateLabel}</div>
                </div>

                <button
                  onClick={() =>
                    downloadJSON(
                      set,
                      `problems_${set.topic}_${set.level}_${created
                        .toISOString()
                        .replace(/[:.]/g, "-")}.json`
                    )
                  }
                  style={btnGhost}
                >
                  JSON 다운로드
                </button>

                <button onClick={() => toggle(idx)} style={btn}>
                  {isOpen ? "접기" : "자세히"}
                </button>
              </div>

              {isOpen && (
                <div style={{ marginTop: 12 }}>
                  <table style={{ width: "100%", borderCollapse: "collapse" }}>
                    <thead>
                      <tr>
                        <th style={th}>#</th>
                        <th style={th}>문제</th>
                        <th style={th}>보기</th>
                        <th style={th}>정답</th>
                        <th style={th}>해설</th>
                      </tr>
                    </thead>
                    <tbody>
                      {set.items.map((it, i) => (
                        <tr key={i}>
                          <td style={td}>{i + 1}</td>
                          <td style={td}>{it.question}</td>
                          <td style={td}>
                            {it.options ? (
                              <ul style={{ margin: 0, paddingLeft: 16 }}>
                                {it.options.map((op, k) => (
                                  <li key={k}>{op}</li>
                                ))}
                              </ul>
                            ) : (
                              <i style={{ color: "#89a" }}>주관식</i>
                            )}
                          </td>
                          <td style={td}>{it.answer}</td>
                          <td style={td}>{it.explanation}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>

                  {/* 원본 JSON */}
                  <details style={{ marginTop: 8 }}>
                    <summary>원본 JSON 보기</summary>
                    <pre style={pre}>{JSON.stringify(set, null, 2)}</pre>
                  </details>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

const input: React.CSSProperties = {
  width: "100%",
  padding: "8px",
  borderRadius: 8,
  border: "1px solid #333",
  background: "#111",
  color: "#eef",
};

const btn: React.CSSProperties = {
  padding: "8px 12px",
  borderRadius: 8,
  border: "1px solid #333",
  background: "#1f2937",
  color: "#eef",
  cursor: "pointer",
};

const btnPrimary: React.CSSProperties = {
  ...btn,
  background: "#b58b43",
  borderColor: "#b58b43",
  color: "#090b12",
  fontWeight: 700,
};

const btnGhost: React.CSSProperties = {
  ...btn,
  background: "transparent",
};

const card: React.CSSProperties = {
  border: "1px solid #2a2f3a",
  borderRadius: 12,
  padding: 12,
  background: "#0b0f17",
};

const th: React.CSSProperties = {
  borderBottom: "1px solid #2a2f3a",
  textAlign: "left",
  padding: "8px 6px",
  whiteSpace: "nowrap",
  fontWeight: 700,
};

const td: React.CSSProperties = {
  borderBottom: "1px solid #1a2030",
  textAlign: "left",
  padding: "8px 6px",
  verticalAlign: "top",
};

const pre: React.CSSProperties = {
  background: "#080d18",
  color: "#c9f0ff",
  padding: 12,
  borderRadius: 8,
  overflowX: "auto",
};
