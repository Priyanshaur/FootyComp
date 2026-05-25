import { Link, useLocation } from 'react-router-dom'
import { BarChart3, GitCompare, Target, Sparkles } from 'lucide-react'

const navLinks = [
  { to: '/compare', label: 'Compare', icon: GitCompare },
  { to: '/fit', label: 'Fit Analysis', icon: Target },
  { to: '/predict', label: 'Predictor', icon: Sparkles },
]

export default function Navbar() {
  const location = useLocation()

  return (
    <nav
      className="fixed top-0 left-0 right-0 z-50 border-b border-white/[0.06]"
      style={{ backgroundColor: 'rgba(10,15,30,0.85)', backdropFilter: 'blur(20px)' }}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2.5 group">
            <div
              className="w-8 h-8 rounded-lg bg-amber-500 flex items-center justify-center
                         group-hover:bg-amber-400 transition-colors duration-200 amber-glow"
            >
              <BarChart3 size={18} className="text-navy-950" />
            </div>
            <span className="text-xl font-bold">
              <span className="text-gradient">Foot</span>
              <span className="text-slate-100">IQ</span>
            </span>
          </Link>

          {/* Nav links */}
          <div className="flex items-center gap-1">
            {navLinks.map(({ to, label, icon: Icon }) => {
              const active = location.pathname === to
              return (
                <Link
                  key={to}
                  to={to}
                  id={`nav-${label.toLowerCase().replace(' ', '-')}`}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium
                             transition-all duration-200 ${
                    active
                      ? 'bg-amber-500/15 text-amber-400 border border-amber-500/20'
                      : 'text-slate-400 hover:text-slate-100 hover:bg-white/5'
                  }`}
                >
                  <Icon size={15} />
                  {label}
                </Link>
              )
            })}
          </div>
        </div>
      </div>
    </nav>
  )
}
