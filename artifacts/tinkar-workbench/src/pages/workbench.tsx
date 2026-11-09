import { useEffect, useMemo, useState } from "react";
import {
  useGetWorkbenchStatus,
  useListScenarios,
  useRunScenario,
} from "@workspace/api-client-react";
import type { DeviceResult, ScenarioResult, Scenario } from "@workspace/api-client-react";
import {
  Play, PlayCircle, RefreshCw, Download, FileJson, Copy, Check, Search, ExternalLink,
  AlertTriangle, ChevronRight, Database, Info, X,
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";

type Stored = { result: ScenarioResult; live: boolean };
const SS_KEY = "tinkar-workbench-results";

function loadStored(): Record<number, Stored> {
  try {
    const raw = sessionStorage.getItem(SS_KEY);
    if (!raw) return {};
    const parsed = JSON.parse(raw) as Record<number, ScenarioResult>;
    const out: Record<number, Stored> = {};
    for (const [k, v] of Object.entries(parsed)) out[Number(k)] = { result: v, live: false };
    return out;
  } catch {
    return {};
  }
}

function download(name: string, text: string, type: string) {
  const url = URL.createObjectURL(new Blob([text], { type }));
  const a = document.createElement("a");
  a.href = url; a.download = name; a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

const csvCell = (v: unknown) => {
  const text = String(v ?? "");
  return `"${(/^[\s]*[=+@\-\t\r]/.test(text) ? "'" + text : text).replace(/"/g, '""')}"`;
};

function pretty(s: string) {
  if (!s) return "";
  try { return JSON.stringify(JSON.parse(s), null, 2); } catch { return s; }
}

const statusStyle: Record<string, string> = {
  found: "bg-[hsl(var(--ok)/.12)] text-[hsl(var(--ok))] border-[hsl(var(--ok)/.3)]",
  missing: "bg-[hsl(var(--warn)/.12)] text-[hsl(var(--warn))] border-[hsl(var(--warn)/.3)]",
  error: "bg-destructive/10 text-destructive border-destructive/30",
};
const parityStyle: Record<string, string> = {
  match: "text-[hsl(var(--ok))]",
  mismatch: "text-destructive",
  unavailable: "text-muted-foreground",
  not_checked: "text-muted-foreground",
};

function Pill({ status }: { status: string }) {
  return (
    <span className={`inline-flex items-center gap-1 rounded-sm border px-1.5 py-0.5 font-mono text-[11px] uppercase tracking-wide ${statusStyle[status] ?? ""}`}>
      <span className="h-1.5 w-1.5 rounded-full bg-current" />
      {status}
    </span>
  );
}

function CopyBtn({ text, id }: { text: string; id: string }) {
  const [done, setDone] = useState(false);
  return (
    <button
      data-testid={`button-copy-${id}`}
      onClick={(e) => {
        e.stopPropagation();
        navigator.clipboard?.writeText(text).then(() => { setDone(true); setTimeout(() => setDone(false), 1200); });
      }}
      className="inline-flex h-5 w-5 items-center justify-center rounded text-muted-foreground transition hover:bg-muted hover:text-foreground"
      title="Copy"
    >
      {done ? <Check className="h-3 w-3 text-[hsl(var(--ok))]" /> : <Copy className="h-3 w-3" />}
    </button>
  );
}

function StatusBar() {
  const { data, isLoading, isError, refetch } = useGetWorkbenchStatus({
    query: { refetchInterval: 30000, queryKey: ["/api/workbench/status"] },
  });
  const online = !!data?.online;
  return (
    <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs" data-testid="status-service">
      {isLoading ? (
        <span className="h-3 w-40 animate-pulse rounded bg-sidebar-accent" />
      ) : isError ? (
        <button onClick={() => refetch()} className="flex items-center gap-1.5 text-red-300 hover:underline" data-testid="button-retry-status">
          <span className="h-2 w-2 rounded-full bg-red-400" /> Status unreachable — retry
        </button>
      ) : (
        <>
          <span className="flex items-center gap-1.5">
            <span className="relative flex h-2 w-2">
              {online && <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-sidebar-primary opacity-60" />}
              <span className={`relative h-2 w-2 rounded-full ${online ? "bg-sidebar-primary" : "bg-red-400"}`} />
            </span>
            {online ? "Service online" : "Service offline"}
          </span>
          <span className="flex items-center gap-1 font-mono text-sidebar-foreground/70"><Database className="h-3 w-3" />{data?.dataset}</span>
          <span className="hidden text-sidebar-foreground/50 md:inline" title={data?.message}>{data?.message}</span>
        </>
      )}
    </div>
  );
}

function ScenarioCard({ s, active, stored, running, onSelect, onRun, disabled }: {
  s: Scenario; active: boolean; stored?: Stored; running: boolean; onSelect: () => void; onRun: () => void; disabled: boolean;
}) {
  const r = stored?.result;
  return (
    <div
      data-testid={`card-scenario-${s.id}`}
      onClick={onSelect}
      tabIndex={0}
      onKeyDown={(e) => { if (e.target === e.currentTarget && (e.key === "Enter" || e.key === " ")) { e.preventDefault(); onSelect(); } }}
      aria-label={`Select case ${s.id}: ${s.title}`}
      className={`group relative cursor-pointer overflow-hidden rounded-md border p-3 transition-all ${active ? "border-primary bg-card shadow-[0_1px_0_hsl(var(--primary)/.4),0_6px_20px_-12px_hsl(var(--primary)/.6)]" : "border-card-border bg-card/60 hover:border-primary/40 hover:bg-card"}`}
    >
      {running && <div className="absolute inset-x-0 top-0 h-0.5 overflow-hidden bg-primary/10"><div className="sweep h-full w-1/3 bg-primary" /></div>}
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0">
          <div className="font-mono text-[10px] uppercase tracking-[0.14em] text-muted-foreground">Case {String(s.id).padStart(2, "0")} · {s.deviceCount} device{s.deviceCount === 1 ? "" : "s"}</div>
          <div className="mt-0.5 font-serif text-[17px] leading-tight">{s.title}</div>
        </div>
        <button
          data-testid={`button-run-${s.id}`}
          disabled={disabled}
          onClick={(e) => { e.stopPropagation(); onRun(); }}
          className="flex h-8 shrink-0 items-center gap-1 rounded bg-primary px-2.5 text-xs font-medium text-primary-foreground transition hover:brightness-110 active:scale-95 disabled:opacity-50"
        >
          {running ? <RefreshCw className="h-3.5 w-3.5 animate-spin" /> : <Play className="h-3.5 w-3.5" />}
          {running ? "Running" : "Run"}
        </button>
      </div>
      <p className="mt-1.5 line-clamp-2 text-xs text-muted-foreground">{s.description}</p>
      <div className="mt-2 flex flex-wrap gap-1">
        {s.devices.slice(0, 4).map((d) => (
          <span key={d} className="max-w-[12rem] truncate rounded-sm bg-muted px-1.5 py-0.5 font-mono text-[10px]">{d}</span>
        ))}
        {s.devices.length > 4 && <span className="px-1 font-mono text-[10px] text-muted-foreground">+{s.devices.length - 4}</span>}
      </div>
      {r && (
        <div className="mt-2 flex items-center gap-3 border-t pt-2 font-mono text-[11px]">
          <span className="text-[hsl(var(--ok))]">{r.found} found</span>
          <span className="text-[hsl(var(--warn))]">{r.missing} missing</span>
          <span className="text-destructive">{r.errors} err</span>
          <span className="ml-auto text-muted-foreground">{stored?.live ? "this session" : "last run"}</span>
        </div>
      )}
    </div>
  );
}

function DeviceDetail({ d, onClose }: { d: DeviceResult; onClose: () => void }) {
  const [tab, setTab] = useState<"semantic" | "search" | "rest">("semantic");
  const raw = tab === "semantic" ? d.semanticJson : tab === "search" ? d.searchJson : d.restJson;
  const body = pretty(raw);
  return (
    <div className="rise flex h-full flex-col" data-testid="panel-device-detail">
      <div className="flex items-start justify-between gap-2 border-b p-4">
        <div className="min-w-0">
          <div className="flex items-center gap-2"><Pill status={d.status} /><span className={`font-mono text-[11px] ${parityStyle[d.parity]}`}>parity: {d.parity.replace("_", " ")}</span></div>
          <h3 className="mt-1 font-serif text-xl leading-tight">{d.label}</h3>
          <div className="mt-1 grid grid-cols-[auto_1fr] gap-x-2 font-mono text-[11px] text-muted-foreground"><span>requested</span><span className="text-foreground">{d.label}</span><span>returned</span><span className="text-foreground">{d.name || "none"}{d.name && d.name !== d.label ? " (candidate variant)" : ""}</span><span>query</span><span>{d.query}</span></div>
        </div>
        <button onClick={onClose} className="rounded p-1 text-muted-foreground hover:bg-muted" data-testid="button-close-detail"><X className="h-4 w-4" /></button>
      </div>
      <div className="space-y-4 overflow-y-auto p-4 text-sm">
        {d.message && <p className="rounded border-l-2 border-primary/50 bg-muted/60 px-3 py-2 text-xs">{d.message}</p>}
        <div className="grid grid-cols-3 gap-2">
          {[["Semantics", d.semanticCount], ["STAMPs", d.stampCount], ["LIDR", d.lidrCount]].map(([k, v]) => (
            <div key={k} className="rounded border bg-background/60 p-2">
              <div className="font-mono text-lg tabular-nums">{v}</div>
              <div className="text-[10px] uppercase tracking-wider text-muted-foreground">{k}</div>
            </div>
          ))}
        </div>
        <p className="text-xs text-muted-foreground"><span className="font-medium text-foreground">LIDR:</span> {d.lidrMessage || (d.lidrCount === 0 ? "No LIDR records returned for this concept. Zero is a valid result on the public subset, not a failure." : "")}</p>
        {d.status === "found" && <p className="text-xs text-muted-foreground">Found means the terminology record was retrieved. It does not imply full clinical DeX completeness; clinical fields such as sensitivity are unavailable in this subset.</p>}
        <div>
          <div className="mb-1 text-[10px] uppercase tracking-wider text-muted-foreground">Public IDs</div>
          {d.publicIds.length ? d.publicIds.map((id) => (
            <div key={id} className="flex items-center gap-1 font-mono text-xs"><span className="break-all">{id}</span><CopyBtn text={id} id={id} /></div>
          )) : <div className="text-xs text-muted-foreground">None returned</div>}
        </div>
        {d.patterns.length > 0 && (
          <div>
            <div className="mb-1 text-[10px] uppercase tracking-wider text-muted-foreground">Patterns</div>
            <div className="flex flex-wrap gap-1">{d.patterns.map((p) => <span key={p} className="rounded-sm bg-accent px-1.5 py-0.5 font-mono text-[11px] text-accent-foreground">{p}</span>)}</div>
          </div>
        )}
        <div>
          <div className="mb-1 flex items-center gap-1 border-b">
            {(["semantic", "search", "rest"] as const).map((t) => (
              <button key={t} data-testid={`tab-raw-${t}`} onClick={() => setTab(t)}
                className={`-mb-px border-b-2 px-2 py-1 font-mono text-[11px] transition ${tab === t ? "border-primary text-foreground" : "border-transparent text-muted-foreground hover:text-foreground"}`}>
                {t}
              </button>
            ))}
            {body && <span className="ml-auto"><CopyBtn text={body} id={`raw-${tab}`} /></span>}
          </div>
          {body ? (
            <pre className="max-h-[50vh] overflow-auto rounded bg-sidebar p-3 font-mono text-[11px] leading-relaxed text-sidebar-foreground">{body}</pre>
          ) : <div className="rounded border border-dashed p-4 text-center text-xs text-muted-foreground">No {tab} payload returned for this device.</div>}
        </div>
      </div>
    </div>
  );
}

export default function Workbench() {
  const { toast } = useToast();
  const scenarios = useListScenarios();
  const run = useRunScenario();
  const [results, setResults] = useState<Record<number, Stored>>(loadStored);
  const [selected, setSelected] = useState<number | null>(null);
  const [runningId, setRunningId] = useState<number | null>(null);
  const [runAll, setRunAll] = useState(false);
  const [filter, setFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState<"all" | "found" | "missing" | "error">("all");
  const [detail, setDetail] = useState<DeviceResult | null>(null);

  const list = scenarios.data ?? [];
  useEffect(() => {
    if (selected == null && list.length) setSelected(list[0].id);
  }, [list, selected]);

  useEffect(() => {
    const plain: Record<number, ScenarioResult> = {};
    for (const [k, v] of Object.entries(results)) plain[Number(k)] = v.result;
    try { sessionStorage.setItem(SS_KEY, JSON.stringify(plain)); } catch { /* quota */ }
  }, [results]);

  const execute = async (id: number) => {
    setRunningId(id);
    setResults((p) => p[id] ? { ...p, [id]: { ...p[id], live: false } } : p);
    try {
      const r = await run.mutateAsync({ id });
      setResults((p) => ({ ...p, [id]: { result: r, live: true } }));
      return true;
    } catch (e) {
      const msg = (e as { data?: { error?: string }; message?: string })?.data?.error ?? (e as Error)?.message ?? "Run failed";
      toast({ title: `Case ${id} failed`, description: msg, variant: "destructive" });
      return false;
    } finally {
      setRunningId(null);
    }
  };

  const runOne = (id: number) => { setSelected(id); setDetail(null); void execute(id); };
  const runEverything = async () => {
    setRunAll(true);
    for (const s of list) { setSelected(s.id); setDetail(null); await execute(s.id); }
    setRunAll(false);
  };

  const current = selected != null ? results[selected] : undefined;
  const scenario = list.find((s) => s.id === selected);
  const rows = useMemo(() => {
    const devs = current?.result.devices ?? [];
    const q = filter.trim().toLowerCase();
    return devs.filter((d) =>
      (statusFilter === "all" || d.status === statusFilter) &&
      (!q || [d.label, d.query, d.name, d.message, ...d.publicIds, ...d.patterns].join(" ").toLowerCase().includes(q)));
  }, [current, filter, statusFilter]);

  const exportCsv = () => {
    if (!current) return;
    const head = ["requestedLabel", "query", "status", "returnedName", "publicIds", "semanticCount", "semanticPatterns", "stampCount", "lidrCount", "searchParity", "clinicalSensitivity", "clinicalSpecificity", "clinicalDexFields", "message", "lidrMessage"];
    const lines = rows.map((d) => [d.label, d.query, d.status, d.name, d.publicIds.join(" "), d.semanticCount, d.patterns.join(" "), d.stampCount, d.lidrCount, d.parity, "unavailable", "unavailable", "unavailable in public subset", d.message, d.lidrMessage].map(csvCell).join(","));
    download(`tinkar-case-${current.result.scenarioId}.csv`, [head.join(","), ...lines].join("\n"), "text/csv");
  };
  const exportJson = () => current && download(`tinkar-case-${current.result.scenarioId}.json`, JSON.stringify(current.result, null, 2), "application/json");

  const busy = runningId != null || runAll;
  const r = current?.result;
  const noClinical = r ? r.devices.length > 0 && r.found === 0 : false;

  return (
    <div className="min-h-[100dvh]">
      <header className="sticky top-0 z-20 bg-sidebar text-sidebar-foreground">
        <div className="mx-auto flex max-w-[1500px] flex-wrap items-center gap-x-6 gap-y-2 px-4 py-3 md:px-6">
          <div className="flex items-baseline gap-2">
            <span className="font-serif text-xl">Tinkar</span>
            <span className="font-mono text-[11px] uppercase tracking-[0.2em] text-sidebar-primary">Workbench</span>
          </div>
          <StatusBar />
          <nav className="ml-auto flex items-center gap-3 text-xs">
            <a href="/tinkar/swagger-ui/index.html" target="_blank" rel="noreferrer" className="flex items-center gap-1 text-sidebar-foreground/80 hover:text-sidebar-foreground" data-testid="link-swagger">Swagger UI <ExternalLink className="h-3 w-3" /></a>
            <a href="/tinkar/api-docs" target="_blank" rel="noreferrer" className="flex items-center gap-1 text-sidebar-foreground/80 hover:text-sidebar-foreground" data-testid="link-api-docs">API docs <ExternalLink className="h-3 w-3" /></a>
          </nav>
        </div>
      </header>

      <main className="mx-auto grid max-w-[1500px] gap-5 px-4 py-5 md:px-6 lg:grid-cols-[320px_1fr]">
        <aside className="space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="font-mono text-[11px] uppercase tracking-[0.16em] text-muted-foreground">DeX scenarios</h2>
            <button data-testid="button-run-all" disabled={busy || !list.length} onClick={runEverything}
              className="flex items-center gap-1 rounded border border-primary/40 px-2 py-1 text-xs font-medium text-primary transition hover:bg-primary hover:text-primary-foreground disabled:opacity-50">
              {runAll ? <RefreshCw className="h-3.5 w-3.5 animate-spin" /> : <PlayCircle className="h-3.5 w-3.5" />} Run all in sequence
            </button>
          </div>
          {scenarios.isLoading && [0, 1, 2].map((i) => <div key={i} className="h-36 animate-pulse rounded-md border bg-card/60" />)}
          {scenarios.isError && (
            <div className="rounded-md border border-destructive/30 bg-destructive/5 p-4 text-sm">
              <div className="flex items-center gap-2 font-medium text-destructive"><AlertTriangle className="h-4 w-4" /> Could not load scenarios</div>
              <p className="mt-1 text-xs text-muted-foreground">The workbench API did not respond.</p>
              <button onClick={() => scenarios.refetch()} className="mt-2 flex items-center gap-1 text-xs font-medium text-primary" data-testid="button-retry-scenarios"><RefreshCw className="h-3 w-3" /> Retry</button>
            </div>
          )}
          {scenarios.isSuccess && !list.length && (
            <div className="rounded-md border border-dashed p-6 text-center text-sm text-muted-foreground">No scenarios are configured on the service.</div>
          )}
          {list.map((s, i) => (
            <div key={s.id} className="rise" style={{ animationDelay: `${i * 60}ms` }}>
              <ScenarioCard s={s} active={selected === s.id} stored={results[s.id]} running={runningId === s.id}
                onSelect={() => { setSelected(s.id); setDetail(null); }} onRun={() => runOne(s.id)} disabled={busy} />
            </div>
          ))}
          <div className="rounded-md border bg-accent/50 p-3 text-xs text-accent-foreground">
            <div className="mb-1 flex items-center gap-1 font-medium"><Info className="h-3.5 w-3.5" /> About this dataset</div>
            The public Tinkar subset does not carry the full clinical DeX fields. Absent sensitivity or performance values are reported as absent, never ranked or scored.
          </div>
        </aside>

        <section className="min-w-0">
          {!scenario ? (
            <div className="h-64 animate-pulse rounded-md border bg-card/60" />
          ) : (
            <div key={scenario.id} className="rise space-y-4">
              <div className="flex flex-wrap items-end justify-between gap-3">
                <div>
                  <div className="font-mono text-[11px] uppercase tracking-[0.16em] text-muted-foreground">Case {String(scenario.id).padStart(2, "0")}</div>
                  <h1 className="font-serif text-3xl leading-tight">{scenario.title}</h1>
                  <p className="mt-1 max-w-2xl text-sm text-muted-foreground">{scenario.description}</p>
                </div>
                <div className="flex gap-2">
                  <button data-testid="button-export-csv" disabled={!r} onClick={exportCsv} className="flex items-center gap-1 rounded border bg-card px-2.5 py-1.5 text-xs transition hover:border-primary/50 disabled:opacity-40"><Download className="h-3.5 w-3.5" /> CSV</button>
                  <button data-testid="button-export-json" disabled={!r} onClick={exportJson} className="flex items-center gap-1 rounded border bg-card px-2.5 py-1.5 text-xs transition hover:border-primary/50 disabled:opacity-40"><FileJson className="h-3.5 w-3.5" /> JSON</button>
                </div>
              </div>

              {!r ? (
                <div className="rounded-md border border-dashed bg-card/50 p-10 text-center">
                  <p className="font-serif text-lg">Not run yet</p>
                  <p className="mx-auto mt-1 max-w-sm text-sm text-muted-foreground">Run this case to query the Tinkar service for {scenario.deviceCount} device{scenario.deviceCount === 1 ? "" : "s"} and inspect identifiers, semantics and raw payloads.</p>
                  <button onClick={() => runOne(scenario.id)} disabled={busy} className="mt-4 inline-flex items-center gap-1 rounded bg-primary px-3 py-2 text-sm font-medium text-primary-foreground transition active:scale-95 disabled:opacity-50" data-testid="button-run-empty">
                    {runningId === scenario.id ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />} Run case
                  </button>
                </div>
              ) : (
                <>
                  {!current?.live && (
                    <div className="flex items-center gap-2 rounded border border-[hsl(var(--warn)/.35)] bg-[hsl(var(--warn)/.08)] px-3 py-2 text-xs" data-testid="status-stale">
                      <AlertTriangle className="h-3.5 w-3.5 text-[hsl(var(--warn))]" />
                      Previous run — not refreshed. Re-run to retrieve current results.
                    </div>
                  )}
                  <div className="grid grid-cols-2 gap-px overflow-hidden rounded-md border bg-border sm:grid-cols-5">
                    {[
                      ["Found", r.found, "text-[hsl(var(--ok))]"],
                      ["Missing", r.missing, "text-[hsl(var(--warn))]"],
                      ["Errors", r.errors, "text-destructive"],
                      ["Duration", `${r.durationMs.toLocaleString()} ms`, ""],
                      ["Executed", new Date(r.executedAt).toLocaleString(), ""],
                    ].map(([k, v, c]) => (
                      <div key={k as string} className="bg-card p-3" data-testid={`stat-${(k as string).toLowerCase()}`}>
                        <div className="text-[10px] uppercase tracking-wider text-muted-foreground">{k}</div>
                        <div className={`mt-0.5 font-mono tabular-nums ${typeof v === "number" ? "text-2xl" : "text-sm"} ${c}`}>{v}</div>
                      </div>
                    ))}
                  </div>
                  {r.devices.length > 0 && (
                    <p className="text-xs text-muted-foreground">Found = terminology record retrieved, not clinical DeX completeness. LIDR counts of 0 are valid results. </p>
                  )}
                  {(r.missing > 0 || noClinical) && (
                    <p className="text-xs text-muted-foreground">Missing devices are not passes: no record matched the exact scenario query in the loaded dataset.</p>
                  )}

                  <div className="grid gap-4 xl:grid-cols-[1fr_400px]">
                    <div className="min-w-0 overflow-hidden rounded-md border bg-card">
                      <div className="flex flex-wrap items-center gap-2 border-b p-2">
                        <div className="relative flex-1 min-w-[180px]">
                          <Search className="absolute left-2 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
                          <input data-testid="input-filter" value={filter} onChange={(e) => setFilter(e.target.value)} placeholder="Filter by label, UUID, pattern..."
                            className="h-8 w-full rounded border bg-background pl-7 pr-2 text-xs outline-none transition focus:border-ring" />
                        </div>
                        <div className="flex rounded border p-0.5">
                          {(["all", "found", "missing", "error"] as const).map((f) => (
                            <button key={f} data-testid={`filter-${f}`} onClick={() => setStatusFilter(f)}
                              className={`rounded-sm px-2 py-1 font-mono text-[11px] transition ${statusFilter === f ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:text-foreground"}`}>{f}</button>
                          ))}
                        </div>
                        <span className="font-mono text-[11px] text-muted-foreground">{rows.length}/{r.devices.length}</span>
                      </div>
                      <div className="overflow-x-auto">
                        <table className="w-full text-left text-xs">
                          <thead className="bg-muted/60 font-mono text-[10px] uppercase tracking-wider text-muted-foreground">
                            <tr><th className="px-3 py-2">Device</th><th className="px-3 py-2">Status</th><th className="px-3 py-2">Public ID</th><th className="px-3 py-2 text-right">Sem</th><th className="px-3 py-2 text-right">Stamp</th><th className="px-3 py-2 text-right">LIDR</th><th className="px-3 py-2">Parity</th><th /></tr>
                          </thead>
                          <tbody>
                            {rows.map((d, i) => (
                              <tr key={`${d.label}-${i}`} data-testid={`row-device-${i}`} onClick={() => setDetail(d)}
                                tabIndex={0} aria-label={`Inspect ${d.label}`}
                                onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); setDetail(d); } }}
                                className={`cursor-pointer border-t transition-colors hover:bg-accent/40 ${detail === d ? "bg-accent/60" : ""}`}>
                                <td className="max-w-[220px] px-3 py-2"><div className="truncate font-medium">{d.label}</div>{d.name && d.name !== d.label && <div className="truncate text-[10px] text-muted-foreground">returned: {d.name}</div>}<div className="truncate font-mono text-[10px] text-muted-foreground">{d.query}</div></td>
                                <td className="px-3 py-2"><Pill status={d.status} /></td>
                                <td className="px-3 py-2 font-mono text-[11px]">{d.publicIds[0] ? <span className="flex items-center gap-1"><span className="max-w-[150px] truncate">{d.publicIds[0]}</span>{d.publicIds.length > 1 && <span className="text-muted-foreground">+{d.publicIds.length - 1}</span>}</span> : <span className="text-muted-foreground">—</span>}</td>
                                <td className="px-3 py-2 text-right font-mono tabular-nums">{d.semanticCount}</td>
                                <td className="px-3 py-2 text-right font-mono tabular-nums">{d.stampCount}</td>
                                <td className="px-3 py-2 text-right font-mono tabular-nums">{d.lidrCount}</td>
                                <td className={`px-3 py-2 font-mono text-[11px] ${parityStyle[d.parity]}`}>{d.parity.replace("_", " ")}</td>
                                <td className="pr-2"><ChevronRight className="h-3.5 w-3.5 text-muted-foreground" /></td>
                              </tr>
                            ))}
                            {!rows.length && <tr><td colSpan={8} className="p-6 text-center text-muted-foreground">No devices match this filter.</td></tr>}
                          </tbody>
                        </table>
                      </div>
                    </div>
                    <div className="min-h-[200px] overflow-hidden rounded-md border bg-card xl:sticky xl:top-20 xl:max-h-[calc(100dvh-6rem)]">
                      {detail ? <DeviceDetail key={detail.label + detail.query} d={detail} onClose={() => setDetail(null)} /> : (
                        <div className="flex h-full min-h-[200px] items-center justify-center p-6 text-center text-xs text-muted-foreground">Select a device row to inspect public IDs, semantic field values and raw payloads.</div>
                      )}
                    </div>
                  </div>

                  <div className="grid gap-4 md:grid-cols-[1fr_1.4fr]">
                    <div className="rounded-md border bg-card p-3">
                      <h3 className="mb-2 font-mono text-[10px] uppercase tracking-wider text-muted-foreground">Limitations</h3>
                      {r.limitations.length ? (
                        <ul className="space-y-1.5 text-xs">{r.limitations.map((l, i) => <li key={i} className="flex gap-2"><span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-[hsl(var(--warn))]" />{l}</li>)}</ul>
                      ) : <p className="text-xs text-muted-foreground">None reported.</p>}
                    </div>
                    <div className="rounded-md border bg-card p-3">
                      <h3 className="mb-2 font-mono text-[10px] uppercase tracking-wider text-muted-foreground">Execution log</h3>
                      <pre className="max-h-56 overflow-auto rounded bg-sidebar p-2 font-mono text-[11px] leading-relaxed text-sidebar-foreground" data-testid="text-logs">{r.logs.length ? r.logs.join("\n") : "No log lines."}</pre>
                    </div>
                  </div>
                </>
              )}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}
