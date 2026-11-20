import { useEffect, useRef, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { ArrowUpRight, Bot, Building2, Database, ExternalLink, Plus, Send, Sparkles, TriangleAlert } from 'lucide-react';

type Source = { source: string; title: string; url: string; n?: number };
type Msg = { role: 'user' | 'assistant'; content: string; sources?: Source[]; retrieved?: Source[]; cited?: boolean; error?: boolean };
type Health = { documents: number; documents_by_source: Record<string, number>; model: string };

const API = (import.meta.env.VITE_API_URL as string | undefined)?.replace(/\/$/, '') ?? '';
const WELCOME =
  'Welcome to your AI Real Estate Assistant. Explore property projects, locations, amenities, pricing information and more from DarGlobal and Wasalt. How can I help you today?';
const PROMPTS = [
  'Explore DarGlobal projects',
  'Explore Wasalt properties',
  'Compare DarGlobal and Wasalt',
  'Find properties by location',
  'Explore available amenities',
];

const badge = (s: string) =>
  s === 'DarGlobal' ? 'bg-gold/20 text-[#8a6a35] border-gold/60' : 'bg-emerald-100 text-emerald-800 border-emerald-300';

export default function App() {
  const [msgs, setMsgs] = useState<Msg[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [health, setHealth] = useState<Health | null>(null);
  const endRef = useRef<HTMLDivElement>(null);
  const started = msgs.length > 0;

  useEffect(() => {
    fetch(`${API}/health`).then((r) => (r.ok ? r.json() : null)).then(setHealth).catch(() => {});
  }, []);
  useEffect(() => { endRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [msgs, loading]);

  async function send(text = input) {
    const q = text.trim();
    if (q.length < 2 || loading) return;
    const history = msgs.filter((m) => !m.error).slice(-6).map(({ role, content }) => ({ role, content }));
    setMsgs((m) => [...m, { role: 'user', content: q }]);
    setInput('');
    setLoading(true);
    try {
      const r = await fetch(`${API}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: q, history }),
      });
      const isJson = (r.headers.get('content-type') || '').includes('application/json');
      const d = isJson ? await r.json() : null;
      if (!r.ok) {
        const detail = typeof d?.detail === 'string' ? d.detail : `The server returned HTTP ${r.status}.`;
        throw new Error(detail);
      }
      setMsgs((m) => [...m, { role: 'assistant', content: d.answer, sources: d.sources, retrieved: d.retrieved, cited: d.cited }]);
    } catch (e) {
      const msg = e instanceof TypeError ? 'Could not reach the server. Check your connection and try again.' : (e as Error).message;
      setMsgs((m) => [...m, { role: 'assistant', content: msg, error: true }]);
    } finally {
      setLoading(false);
    }
  }

  const Composer = (
    <div className="mx-auto w-full max-w-3xl">
      <div className="flex overflow-hidden rounded-xl border border-white/15 bg-white shadow-lg focus-within:ring-2 focus-within:ring-lime/60">
        <input
          value={input}
          maxLength={2000}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && send()}
          placeholder="Ask about projects, locations, prices or amenities…"
          aria-label="Your question"
          className="flex-1 bg-transparent px-4 py-4 text-[15px] text-navy-900 outline-none placeholder:text-slate-400"
        />
        <button
          onClick={() => send()}
          disabled={input.trim().length < 2 || loading}
          aria-label="Send"
          className="grid w-14 place-items-center bg-navy-900 text-lime transition hover:bg-navy-700 disabled:opacity-40"
        >
          <Send size={18} />
        </button>
      </div>
      <p className="mt-2 text-center font-mono text-[10px] tracking-wide text-slate-400">
        Answers come only from indexed public pages and will say when a detail is unavailable. Not financial advice.
      </p>
    </div>
  );

  return (
    <div className="flex h-full flex-col">
      <header className="flex h-16 shrink-0 items-center justify-between border-b border-white/10 px-5 md:px-10">
        <div className="flex items-center gap-3 text-sm font-bold tracking-[0.18em]">
          <span className="grid h-8 w-8 place-items-center rounded-full border border-lime text-lime"><Building2 size={17} /></span>
          PROPERTY<span className="text-lime">AI</span>
        </div>
        <div className="flex items-center gap-4">
          {health && (
            <span className="hidden items-center gap-2 font-mono text-[11px] uppercase tracking-wider text-slate-400 sm:flex">
              <i className="h-1.5 w-1.5 rounded-full bg-lime shadow-[0_0_0_4px_rgba(200,252,87,.15)]" /> {health.documents} documents indexed
            </span>
          )}
          {started && (
            <button onClick={() => { setMsgs([]); setInput(''); }}
              className="flex items-center gap-2 rounded border border-white/20 px-3 py-2 text-xs transition hover:border-lime hover:text-lime">
              <Plus size={14} /> New conversation
            </button>
          )}
        </div>
      </header>

      {!started ? (
        <main className="flex flex-1 flex-col overflow-y-auto">
          <section className="mx-auto grid w-full max-w-6xl flex-1 items-center gap-10 px-5 py-10 md:grid-cols-[1.1fr_1fr] md:px-10">
            <div>
              <div className="font-mono text-[11px] tracking-[0.2em] text-slate-400">RESEARCH CONCIERGE · GROUNDED IN PUBLIC SOURCES</div>
              <h1 className="mt-5 text-5xl font-semibold leading-[0.95] tracking-tight md:text-7xl">
                Property<br /><em className="font-serif font-semibold text-lime">intelligence.</em>
              </h1>
              <p className="mt-6 max-w-md text-[15px] leading-relaxed text-slate-300">
                One place to explore international luxury residences from DarGlobal and Saudi property opportunities from Wasalt, with every answer linked to its source.
              </p>
              <div className="mt-8 max-w-sm border-t border-white/15 pt-5">
                <div className="mb-3 flex items-center gap-2 font-mono text-[10px] tracking-widest text-slate-300"><Database size={14} /> INDEX COVERAGE</div>
                {['DarGlobal', 'Wasalt'].map((s) => (
                  <div key={s} className="flex items-center gap-3 py-1.5 text-sm">
                    <span className={`h-2 w-2 rounded-full ${s === 'DarGlobal' ? 'bg-gold' : 'bg-lime'}`} />
                    {s}
                    <span className="ml-auto font-mono text-[11px] text-slate-400">{health?.documents_by_source?.[s] ?? '—'} docs</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="rounded-2xl bg-ivory p-6 text-navy-900 shadow-2xl md:p-8">
              <div className="flex gap-3">
                <span className="grid h-8 w-8 shrink-0 place-items-center rounded-full bg-navy-900 text-lime"><Bot size={16} /></span>
                <p className="text-[15px] leading-relaxed text-slate-700">{WELCOME}</p>
              </div>
              <div className="mt-6 flex items-center gap-2 font-mono text-[10px] tracking-widest text-[#9b815d]"><Sparkles size={13} /> START WITH A QUESTION</div>
              <div className="mt-3 flex flex-wrap gap-2">
                {PROMPTS.map((p) => (
                  <button key={p} onClick={() => send(p)}
                    className="flex items-center gap-2 rounded-md border border-slate-300 bg-white/60 px-3 py-2 text-xs text-slate-600 transition hover:border-[#9b815d] hover:text-navy-900">
                    {p}<ArrowUpRight size={13} />
                  </button>
                ))}
              </div>
              <div className="mt-6">{Composer}</div>
            </div>
          </section>
        </main>
      ) : (
        <>
          <main className="flex-1 overflow-y-auto bg-ivory text-navy-900">
            <div className="mx-auto max-w-3xl px-4 py-6 md:px-6">
              <Bubble m={{ role: 'assistant', content: WELCOME }} />
              {msgs.map((m, i) => <Bubble key={i} m={m} />)}
              {loading && (
                <div className="my-5 flex items-center gap-3">
                  <span className="grid h-8 w-8 place-items-center rounded-full bg-navy-900 text-lime"><Bot size={16} /></span>
                  <div className="flex items-center gap-1.5 text-sm text-slate-500">
                    <span className="dot h-1.5 w-1.5 rounded-full bg-slate-500" /><span className="dot h-1.5 w-1.5 rounded-full bg-slate-500" /><span className="dot h-1.5 w-1.5 rounded-full bg-slate-500" />
                    <span className="ml-2">Searching the research index…</span>
                  </div>
                </div>
              )}
              {!loading && (
                <div className="mt-6 flex flex-wrap gap-2">
                  {PROMPTS.slice(0, 3).map((p) => (
                    <button key={p} onClick={() => send(p)} className="rounded-md border border-slate-300 px-3 py-1.5 text-xs text-slate-500 transition hover:border-[#9b815d] hover:text-navy-900">{p}</button>
                  ))}
                </div>
              )}
              <div ref={endRef} />
            </div>
          </main>
          <footer className="shrink-0 border-t border-slate-300/60 bg-[#f8f6f1] px-4 py-4">{Composer}</footer>
        </>
      )}
    </div>
  );
}

// turn "[3]" markers into internal links so they render as small clickable source chips
const linkCitations = (t: string) => t.replace(/\[(\d{1,2})\](?!\()/g, '[$1](#src-$1)');

function Bubble({ m }: { m: Msg }) {
  if (m.role === 'user') {
    return (
      <div className="my-5 flex justify-end">
        <div className="max-w-[85%] rounded-xl rounded-br-sm bg-navy-900 px-4 py-3 text-[15px] text-ivory">{m.content}</div>
      </div>
    );
  }
  if (m.error) {
    return (
      <div className="my-5 flex gap-3">
        <span className="grid h-8 w-8 shrink-0 place-items-center rounded-full bg-red-100 text-red-600"><TriangleAlert size={16} /></span>
        <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">{m.content}</div>
      </div>
    );
  }
  return (
    <div className="my-5 flex gap-3">
      <span className="grid h-8 w-8 shrink-0 place-items-center rounded-full bg-navy-900 text-lime"><Bot size={16} /></span>
      <div className="min-w-0 flex-1">
        <div className="font-mono text-[9px] tracking-[0.16em] text-slate-400">PROPERTYAI</div>
        <div className="prose-chat text-[15px] text-slate-700">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              a: (p) => {
                const cite = /^#src-(\d+)$/.exec(p.href ?? '');
                if (cite) {
                  const n = Number(cite[1]);
                  const src = (m.retrieved ?? m.sources ?? []).find((x) => x.n === n);
                  if (!src) return <sup className="cite cite-off">{n}</sup>;
                  return (
                    <sup>
                      <a className="cite" href={src.url} target="_blank" rel="noreferrer" title={`${src.source}: ${src.title}`}>{n}</a>
                    </sup>
                  );
                }
                return <a href={p.href} target="_blank" rel="noreferrer">{p.children}</a>;
              },
              table: (p) => <div className="overflow-x-auto"><table>{p.children}</table></div>,
            }}
          >
            {linkCitations(m.content)}
          </ReactMarkdown>
        </div>
        {m.sources && m.sources.length > 0 && (
          <div className="mt-3 border-t border-slate-300 pt-3">
            <div className="mb-2 font-mono text-[9px] tracking-[0.16em] text-slate-400">{m.cited ? 'SOURCES CITED' : 'RELATED SOURCES (NOT DIRECTLY CITED)'}</div>
            <div className="flex flex-col gap-1.5">
              {m.sources.map((s) => (
                <a key={s.url} href={s.url} target="_blank" rel="noreferrer"
                  className="group flex items-center gap-2 text-xs text-slate-600 hover:text-navy-900">
                  {s.n && <span className="font-mono text-[10px] text-[#a1845b]">[{s.n}]</span>}
                  <span className={`rounded border px-1.5 py-0.5 text-[10px] font-medium ${badge(s.source)}`}>{s.source}</span>
                  <span className="truncate">{s.title}</span>
                  <ExternalLink size={12} className="ml-auto shrink-0 opacity-50 group-hover:opacity-100" />
                </a>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}