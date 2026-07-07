"use client";

import { FormEvent, useEffect, useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

type Company = {
  id: number;
  name: string;
  sector: string | null;
};

type Finding = {
  id: number;
  severity: string | null;
  category: string | null;
  title: string;
  detail: string | null;
};

export default function Home() {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [selectedCompanyId, setSelectedCompanyId] = useState<number | null>(null);
  const [findings, setFindings] = useState<Finding[]>([]);
  const [answer, setAnswer] = useState("");
  const [status, setStatus] = useState("Ready");

  async function refreshCompanies() {
    const response = await fetch(`${API_BASE}/companies`);
    const data = await response.json();
    setCompanies(data);
    if (!selectedCompanyId && data.length > 0) {
      setSelectedCompanyId(data[0].id);
    }
  }

  async function refreshFindings(companyId = selectedCompanyId) {
    if (!companyId) return;
    const response = await fetch(`${API_BASE}/companies/${companyId}/findings`);
    setFindings(await response.json());
  }

  useEffect(() => {
    refreshCompanies().catch(() => setStatus("API unavailable"));
  }, []);

  useEffect(() => {
    refreshFindings().catch(() => undefined);
  }, [selectedCompanyId]);

  async function createCompany(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    await fetch(`${API_BASE}/companies`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: form.get("name"), sector: form.get("sector") || null }),
    });
    event.currentTarget.reset();
    setStatus("Company created");
    await refreshCompanies();
  }

  async function uploadDocument(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedCompanyId) return;
    const form = new FormData(event.currentTarget);
    await fetch(`${API_BASE}/companies/${selectedCompanyId}/documents?doc_type=${form.get("doc_type") || "other"}`, {
      method: "POST",
      body: form,
    });
    event.currentTarget.reset();
    setStatus("Document uploaded");
  }

  async function startRun() {
    if (!selectedCompanyId) return;
    await fetch(`${API_BASE}/companies/${selectedCompanyId}/runs`, { method: "POST" });
    setStatus("Diligence run started");
    setTimeout(() => refreshFindings(), 1500);
  }

  async function askQuestion(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedCompanyId) return;
    const form = new FormData(event.currentTarget);
    const response = await fetch(`${API_BASE}/companies/${selectedCompanyId}/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: form.get("question") }),
    });
    const data = await response.json();
    setAnswer(data.answer);
  }

  return (
    <main>
      <section className="hero">
        <p className="eyebrow">Portfolio Diligence Copilot</p>
        <h1>Run AI-native diligence on a company data room.</h1>
        <p>
          Upload documents, kick off a diligence pass, ask questions, and track source-cited findings from one local
          workspace.
        </p>
      </section>

      <section className="grid">
        <div className="card">
          <h2>Companies</h2>
          <form onSubmit={createCompany}>
            <input name="name" placeholder="Company name" required />
            <input name="sector" placeholder="Sector" />
            <button type="submit">Create company</button>
          </form>
          <select
            value={selectedCompanyId ?? ""}
            onChange={(event) => setSelectedCompanyId(Number(event.target.value))}
          >
            <option value="" disabled>
              Select a company
            </option>
            {companies.map((company) => (
              <option key={company.id} value={company.id}>
                {company.name} {company.sector ? `(${company.sector})` : ""}
              </option>
            ))}
          </select>
        </div>

        <div className="card">
          <h2>Data Room</h2>
          <form onSubmit={uploadDocument}>
            <input name="file" type="file" required />
            <select name="doc_type" defaultValue="other">
              <option value="financials">Financials</option>
              <option value="contract">Contract</option>
              <option value="board_deck">Board deck</option>
              <option value="other">Other</option>
            </select>
            <button type="submit">Upload document</button>
          </form>
          <button onClick={startRun} disabled={!selectedCompanyId}>
            Run diligence
          </button>
          <p className="status">{status}</p>
        </div>

        <div className="card">
          <h2>Ask the Data Room</h2>
          <form onSubmit={askQuestion}>
            <input name="question" placeholder="Where are the biggest risks?" required />
            <button type="submit">Ask</button>
          </form>
          {answer && <pre>{answer}</pre>}
        </div>

        <div className="card">
          <h2>Findings</h2>
          <button onClick={() => refreshFindings()} disabled={!selectedCompanyId}>
            Refresh findings
          </button>
          <div className="findings">
            {findings.map((finding) => (
              <article key={finding.id}>
                <span>{finding.severity ?? "low"}</span>
                <h3>{finding.title}</h3>
                <p>{finding.detail}</p>
              </article>
            ))}
            {findings.length === 0 && <p>No findings yet. Upload a document and run diligence.</p>}
          </div>
        </div>
      </section>
    </main>
  );
}
