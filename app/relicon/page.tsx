"use client"

import { useCallback, useEffect, useState } from "react"
import type { Genome as CreativeGenome } from "@/lib/genome"

const API = process.env.NEXT_PUBLIC_ENGINE_URL || "http://localhost:8000"
const TABS = ["Studio", "Campaigns", "Ads", "Learning", "Simulation Lab", "Data"] as const
type Tab = (typeof TABS)[number]
type Json = Record<string, any>

async function get(path: string): Promise<any> {
  const r = await fetch(API + path)
  if (!r.ok) throw new Error(`${r.status} ${await r.text()}`)
  return r.json()
}
async function post(path: string, body: unknown): Promise<any> {
  const r = await fetch(API + path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) })
  if (!r.ok) throw new Error(`${r.status} ${await r.text()}`)
  return r.json()
}

function Badge({ on, text = "SIMULATED" }: { on?: boolean; text?: string }) {
  if (!on) return null
  return <span className="ml-2 rounded bg-amber-500 px-2 py-0.5 text-xs font-bold text-black">{text}</span>
}

function Card({ title, children, sim }: { title: string; children: React.ReactNode; sim?: boolean }) {
  return (
    <section className="mb-4 rounded-lg border border-neutral-700 bg-neutral-900 p-4">
      <h2 className="mb-3 font-semibold">{title}<Badge on={sim} /></h2>
      {children}
    </section>
  )
}

function Studio() {
  const [sentence, setSentence] = useState("cold-brew coffee for night-shift nurses")
  const [duration, setDuration] = useState(15)
  const [budget, setBudget] = useState(5)
  const [draft, setDraft] = useState(false)
  const [events, setEvents] = useState<Json[]>([])
  const [done, setDone] = useState<Json | null>(null)
  const run = async () => {
    setEvents([]); setDone(null)
    const { job_id } = await post("/api/generate", { sentence, duration, budget, draft })
    const es = new EventSource(`${API}/api/jobs/${job_id}/events`)
    es.onmessage = (m) => setEvents((e) => [...e, JSON.parse(m.data)])
    es.addEventListener("done", (m) => { setDone(JSON.parse((m as MessageEvent).data)); es.close() })
  }
  return (
    <Card title="Studio: one sentence to a finished ad">
      <div className="flex flex-wrap gap-2">
        <input className="min-w-[280px] flex-1 rounded bg-neutral-800 p-2" value={sentence} onChange={(e) => setSentence(e.target.value)} />
        <label className="text-sm">seconds <input type="number" min={6} max={300} className="w-20 rounded bg-neutral-800 p-2" value={duration} onChange={(e) => setDuration(+e.target.value)} /></label>
        <label className="text-sm">budget $ <input type="number" min={0} step={0.5} className="w-20 rounded bg-neutral-800 p-2" value={budget} onChange={(e) => setBudget(+e.target.value)} /></label>
        <label className="text-sm"><input type="checkbox" checked={draft} onChange={(e) => setDraft(e.target.checked)} /> storyboard only</label>
        <button className="rounded bg-white px-4 py-2 font-semibold text-black" onClick={run}>Generate</button>
      </div>
      <ol className="mt-3 max-h-60 overflow-auto text-xs text-neutral-400">
        {events.map((e, i) => <li key={i}>{e.step} {e.status} {e.progress != null ? `${Math.round(e.progress * 100)}%` : ""}</li>)}
      </ol>
      {done && <p className="mt-2 text-sm">{done.error ? `Refused or failed: ${done.error}` : `Done: ad ${done.result.genome_id} (see Ads)`}</p>}
    </Card>
  )
}

function Campaigns() {
  const [rows, setRows] = useState<Json[]>([])
  useEffect(() => { get("/api/campaigns").then(setRows).catch(() => setRows([])) }, [])
  return (
    <Card title="Campaigns by niche">
      <table className="w-full text-sm"><thead><tr className="text-left text-neutral-400"><th>niche</th><th>ads</th><th>results</th><th>best ROAS</th></tr></thead>
        <tbody>{rows.map((r) => <tr key={r.niche}><td>{r.niche}<Badge on={r.is_simulated} /></td><td>{r.ads}</td><td>{r.with_results}</td><td>{r.best_roas.toFixed(2)}</td></tr>)}</tbody>
      </table>
    </Card>
  )
}

function Ads() {
  const [ads, setAds] = useState<Json[]>([])
  const [g, setG] = useState<CreativeGenome | null>(null)
  useEffect(() => { get("/api/ads").then(setAds).catch(() => setAds([])) }, [])
  return (
    <div className="grid gap-4 md:grid-cols-2">
      <Card title="Rendered ads">
        {ads.map((a) => (
          <div key={a.genome_id} className="mb-4 border-b border-neutral-800 pb-3">
            <div className="text-sm">{a.ad_name}<Badge on={a.is_mock} text="MOCK RENDER" /></div>
            {a.videos["9:16"] && <video className="mt-2 max-h-72" controls src={API + a.videos["9:16"]} />}
            <div className="mt-1 text-xs text-neutral-400">cost ${a.cost.actual_total_usd?.toFixed(2)} · exports {Object.keys(a.videos).join(", ")}</div>
            <button className="mt-1 text-xs underline" onClick={() => get(`/api/genomes/${a.genome_id}`).then(setG)}>genome</button>
          </div>
        ))}
      </Card>
      <Card title="Genome" sim={!!g?.results?.some((r) => r.is_simulated)}>
        {g ? <pre className="max-h-[70vh] overflow-auto text-xs">{JSON.stringify(g, null, 1)}</pre> : <p className="text-sm text-neutral-400">Pick an ad.</p>}
      </Card>
    </div>
  )
}

function Learning() {
  const [niche, setNiche] = useState("coffee_nightshift")
  const [d, setD] = useState<Json | null>(null)
  const load = useCallback(() => get(`/api/learning/${niche}`).then(setD).catch(() => setD(null)), [niche])
  useEffect(() => { load() }, [load])
  const s = d?.active?.summary
  return (
    <>
      <Card title="Policy" sim={d?.active?.is_simulated}>
        <input className="rounded bg-neutral-800 p-2 text-sm" value={niche} onChange={(e) => setNiche(e.target.value)} />
        <p className="mt-2 text-sm">active: {d?.active?.version ?? "none"} · {s?.n_used ?? 0} ads used · {s?.below_floor ?? 0} below impression floor</p>
        <ul className="mt-2 text-xs">{d?.versions?.map((v: Json) => (
          <li key={v.version}>{v.version} · {v.n_obs} obs · {v.created_at.slice(0, 19)}{" "}
            <button className="underline" onClick={() => post(`/api/learning/${niche}/rollback`, { version: v.version }).then(load)}>roll back here</button></li>))}
        </ul>
      </Card>
      <Card title="Insights (90% interval excludes zero)" sim={d?.active?.is_simulated}>
        <ul className="text-sm">{s?.insights?.map((i: Json) => <li key={i.id}>{i.text}</li>)}</ul>
      </Card>
      <Card title="Scene credit (relative drop-off speed by beat)" sim={d?.active?.is_simulated}>
        <ul className="text-sm">{s && Object.entries(s.scene_credit).map(([b, v]: [string, any]) => <li key={b}>{b}: x{v.rel_hazard} (90% {v.ci90[0]}–{v.ci90[1]})</li>)}</ul>
        <p className="mt-2 text-xs text-neutral-400">fatigue: {s?.fatigue?.per_day != null ? `${(s.fatigue.per_day * 100).toFixed(1)}% hook rate per day` : "no daily data"}</p>
      </Card>
    </>
  )
}

function Lab() {
  const [sc, setSc] = useState<Json[]>([])
  const [pick, setPick] = useState("coffee_nightshift@tiktok")
  const [log, setLog] = useState<Json[]>([])
  const [ev, setEv] = useState<Json | null>(null)
  const [busy, setBusy] = useState(false)
  useEffect(() => { get("/api/sim/scenarios").then(setSc).catch(() => setSc([])); get("/api/eval").then(setEv).catch(() => setEv(null)) }, [])
  const run = async () => { setBusy(true); try { setLog((await post("/api/sim/run", { scenario: pick, generations: 3, batch: 8 })).log) } finally { setBusy(false) } }
  const curves: Json = ev?.summary?.curves ?? {}
  return (
    <>
      <Card title="Run the loop on a simulated market" sim>
        <select className="rounded bg-neutral-800 p-2 text-sm" value={pick} onChange={(e) => setPick(e.target.value)}>
          {sc.map((s) => <option key={s.name} value={s.name}>{s.name}: {s.sentence}</option>)}
        </select>
        <button disabled={busy} className="ml-2 rounded bg-white px-3 py-2 text-sm font-semibold text-black" onClick={run}>{busy ? "running…" : "Run 3 generations"}</button>
        <ul className="mt-2 text-sm">{log.map((l) => <li key={l.generation}>gen {l.generation}: policy {l.policy}, mean ROAS {l.mean_roas.toFixed(2)}, max {l.max_roas.toFixed(2)}</li>)}</ul>
      </Card>
      <Card title="Evaluation: share of oracle by generation" sim>
        {ev?.available ? (
          <table className="w-full text-sm"><tbody>{Object.entries(curves).map(([m, c]: [string, any]) => (
            <tr key={m}><td className="pr-3">{m}</td><td>{c.map((x: number) => `${Math.round(x * 100)}%`).join(" · ")}</td></tr>))}</tbody></table>
        ) : <p className="text-sm text-neutral-400">Run `make eval` first.</p>}
      </Card>
    </>
  )
}

function Data() {
  const [text, setText] = useState("")
  const [preset, setPreset] = useState("meta")
  const [rep, setRep] = useState<Json | null>(null)
  const [hist, setHist] = useState<Json[]>([])
  useEffect(() => { get("/api/imports").then(setHist).catch(() => setHist([])) }, [rep])
  return (
    <Card title="Import real results (CSV export)">
      <p className="mb-2 text-xs text-neutral-400">Ads must be published as rlc_&lt;genome_id&gt;_&lt;variant&gt;. Rows without that name are listed, never guessed.</p>
      <select className="rounded bg-neutral-800 p-2 text-sm" value={preset} onChange={(e) => setPreset(e.target.value)}><option value="meta">Meta</option><option value="tiktok">TikTok</option></select>
      <input type="file" accept=".csv" className="ml-2 text-sm" onChange={async (e) => setText((await e.target.files?.[0]?.text()) ?? "")} />
      <button className="ml-2 rounded bg-white px-3 py-1 text-sm font-semibold text-black" disabled={!text} onClick={async () => setRep(await post("/api/import", { csv_text: text, preset }))}>Import</button>
      {rep && <p className="mt-2 text-sm">{rep.matched}/{rep.rows} matched · {rep.unmatched.length} unmatched · {rep.errors.length} errors</p>}
      <ul className="mt-2 text-xs text-neutral-400">{hist.map((h, i) => <li key={i}>{h.file}: {h.matched}/{h.rows} matched</li>)}</ul>
    </Card>
  )
}

export default function ReliconConsole() {
  const [tab, setTab] = useState<Tab>("Studio")
  return (
    <main className="min-h-screen bg-neutral-950 p-4 text-neutral-100 md:p-8">
      <h1 className="mb-1 text-2xl font-bold">Relicon</h1>
      <p className="mb-4 text-xs text-neutral-400">Engine: {API}. Badges mark simulated results and mock renders.</p>
      <nav className="mb-4 flex flex-wrap gap-2">
        {TABS.map((t) => <button key={t} onClick={() => setTab(t)} className={`rounded px-3 py-1 text-sm ${t === tab ? "bg-white text-black" : "bg-neutral-800"}`}>{t}</button>)}
      </nav>
      {tab === "Studio" && <Studio />}
      {tab === "Campaigns" && <Campaigns />}
      {tab === "Ads" && <Ads />}
      {tab === "Learning" && <Learning />}
      {tab === "Simulation Lab" && <Lab />}
      {tab === "Data" && <Data />}
    </main>
  )
}
