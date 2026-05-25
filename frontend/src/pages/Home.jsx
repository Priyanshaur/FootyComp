import { Link } from 'react-router-dom'
import {
  GitCompare,
  Target,
  Sparkles,
  TrendingUp,
  Users,
  Globe,
  ChevronRight,
  Zap,
} from 'lucide-react'

const FEATURES = [
  {
    icon: GitCompare,
    title: 'Player vs. Player',
    subtitle: 'Compare any two players',
    description:
      'Side-by-side radar charts across 8 statistical dimensions with AI-generated insight on strengths, weaknesses, and ideal team contexts.',
    to: '/compare',
    color: '#60a5fa',
    id: 'feature-compare',
    featured: false,
  },
  {
    icon: Target,
    title: 'Team Fit Analysis',
    subtitle: 'The core differentiator',
    description:
      "Quantify how well a player's statistical profile matches a team's playing style. Get a 0–100 Fit Score, category breakdown, and AI transfer insight.",
    to: '/fit',
    color: '#f59e0b',
    id: 'feature-fit',
    featured: true,
  },
  {
    icon: Sparkles,
    title: 'Cup Predictor',
    subtitle: 'AI powered by real data',
    description:
      "Predict Champions League knockout results using current team form — not historical reputation. Ask about any tie and get a streamed prediction citing actual stats.",
    to: '/predict',
    color: '#a78bfa',
    id: 'feature-predict',
    featured: false,
  },
]

const LEAGUES = [
  { name: 'Premier League', flag: '🏴󠁧󠁢󠁥󠁮󠁧󠁿', country: 'England' },
  { name: 'La Liga', flag: '🇪🇸', country: 'Spain' },
  { name: 'Bundesliga', flag: '🇩🇪', country: 'Germany' },
  { name: 'Serie A', flag: '🇮🇹', country: 'Italy' },
  { name: 'Ligue 1', flag: '🇫🇷', country: 'France' },
]

const STATS_STRIP = [
  { value: '100+', label: 'Clubs Tracked', icon: Globe },
  { value: '12,000+', label: 'Players Indexed', icon: Users },
  { value: '2 Seasons', label: 'Historical Data', icon: TrendingUp },
  { value: 'Real-time', label: 'AI Predictions', icon: Zap },
]

export default function Home() {
  return (
    <div className="pt-16">
      {/* ── Hero ── */}
      <section className="relative min-h-[92vh] flex items-center overflow-hidden">
        {/* Background gradients */}
        <div className="absolute inset-0 hero-gradient pointer-events-none" />
        <div
          className="absolute inset-0 pointer-events-none"
          style={{
            background:
              'radial-gradient(ellipse 60% 50% at 80% 50%, rgba(96,165,250,0.05) 0%, transparent 70%)',
          }}
        />
        {/* Subtle grid */}
        <div
          className="absolute inset-0 pointer-events-none"
          style={{
            backgroundImage:
              'linear-gradient(rgba(255,255,255,0.013) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.013) 1px, transparent 1px)',
            backgroundSize: '64px 64px',
          }}
        />

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 relative z-10">
          <div className="max-w-3xl">
            {/* Live badge */}
            <div
              className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full
                         bg-amber-500/10 border border-amber-500/20 text-amber-400 text-xs font-medium mb-8
                         animate-fade-in"
            >
              <div className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse" />
              Big 5 European Leagues · Updated Weekly
            </div>

            {/* Headline */}
            <h1 className="text-5xl sm:text-6xl lg:text-7xl font-black leading-[1.05] mb-6 animate-slide-up">
              Football analytics
              <span className="block text-gradient">that answers why.</span>
            </h1>

            <p
              className="text-xl text-slate-400 leading-relaxed mb-10 max-w-2xl animate-slide-up"
              style={{ animationDelay: '0.1s' }}
            >
              Compare players, analyse team fit with real statistics, and predict Champions League
              results using AI that reads current form — not Wikipedia.
            </p>

            <div className="flex flex-wrap gap-4 animate-slide-up" style={{ animationDelay: '0.2s' }}>
              <Link to="/fit" id="cta-fit-analysis" className="btn-primary text-base flex items-center gap-2">
                <Target size={18} />
                Try Fit Analysis
              </Link>
              <Link to="/compare" id="cta-compare" className="btn-ghost text-base flex items-center gap-2">
                <GitCompare size={18} />
                Compare Players
                <ChevronRight size={16} />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* ── Stats strip ── */}
      <section className="border-y border-white/[0.06] py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {STATS_STRIP.map(({ value, label, icon: Icon }, i) => (
              <div key={i} className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-amber-500/10 flex items-center justify-center flex-shrink-0">
                  <Icon size={18} className="text-amber-400" />
                </div>
                <div>
                  <div className="text-xl font-black text-slate-100">{value}</div>
                  <div className="text-xs text-slate-500">{label}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Features grid ── */}
      <section className="py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-black mb-4">
              Everything on one <span className="text-gradient">platform.</span>
            </h2>
            <p className="text-slate-400 text-lg max-w-2xl mx-auto">
              Sofascore shows stats. Transfermarkt shows valuations. Nobody shows whether a player
              actually <em>fits</em> how a team plays. Until now.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            {FEATURES.map((f) => (
              <Link
                key={f.to}
                to={f.to}
                id={f.id}
                className={`glass-card p-6 card-hover relative overflow-hidden group ${
                  f.featured ? 'ring-1 ring-amber-500/25' : ''
                }`}
              >
                {f.featured && (
                  <div className="absolute top-4 right-4">
                    <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-400 border border-amber-500/25">
                      Core Feature
                    </span>
                  </div>
                )}

                {/* Icon */}
                <div
                  className="w-12 h-12 rounded-xl mb-5 flex items-center justify-center"
                  style={{ backgroundColor: `${f.color}15` }}
                >
                  <f.icon size={22} style={{ color: f.color }} />
                </div>

                <div className="text-xs font-semibold uppercase tracking-wider mb-1" style={{ color: f.color }}>
                  {f.subtitle}
                </div>
                <h3 className="text-xl font-bold text-slate-100 mb-3">{f.title}</h3>
                <p className="text-slate-400 text-sm leading-relaxed mb-5">{f.description}</p>

                <div
                  className="flex items-center gap-1 text-sm font-semibold group-hover:gap-2 transition-all duration-200"
                  style={{ color: f.color }}
                >
                  Try it <ChevronRight size={14} />
                </div>

                {/* Hover glow */}
                <div
                  className="absolute -bottom-10 -right-10 w-40 h-40 rounded-full opacity-0
                             group-hover:opacity-100 transition-opacity duration-500 pointer-events-none"
                  style={{
                    background: `radial-gradient(circle, ${f.color}12 0%, transparent 70%)`,
                  }}
                />
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* ── Leagues ── */}
      <section className="py-16 border-t border-white/[0.06]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-10">
            <h2 className="text-2xl font-bold text-slate-200 mb-2">Covering the Big 5</h2>
            <p className="text-slate-500 text-sm">All major European leagues from a single unified data source</p>
          </div>
          <div className="flex flex-wrap justify-center gap-4">
            {LEAGUES.map((l) => (
              <div key={l.name} className="glass-card px-5 py-4 flex items-center gap-3 card-hover cursor-default">
                <span className="text-2xl">{l.flag}</span>
                <div>
                  <div className="font-semibold text-slate-200 text-sm">{l.name}</div>
                  <div className="text-xs text-slate-500">{l.country}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Problem / Solution CTA ── */}
      <section className="py-24 border-t border-white/[0.06]">
        <div className="max-w-3xl mx-auto px-4 text-center">
          <h2 className="text-3xl font-black mb-6">
            When you ask ChatGPT to predict a Champions League tie,
            <span className="text-slate-400"> it guesses from reputation.</span>
          </h2>
          <p className="text-slate-400 text-lg leading-relaxed mb-8">
            FootIQ&apos;s predictor fetches both teams&apos; actual stats before answering.
            Not what Bayern won in 2013. What they&apos;re doing right now.
          </p>
          <Link to="/predict" id="cta-predictor-bottom" className="btn-primary text-base inline-flex items-center gap-2">
            <Sparkles size={18} />
            Try the Predictor
          </Link>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer className="border-t border-white/[0.06] py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-wrap items-center justify-between gap-4">
          <div className="text-sm text-slate-600">© 2025 FootIQ. Data sourced from FBref.</div>
          <div className="text-sm text-slate-600">Powered by Claude · Built for football fans</div>
        </div>
      </footer>
    </div>
  )
}
