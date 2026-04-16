import { Link, NavLink } from "react-router-dom";

const navLinkClasses =
  "px-3 py-1.5 rounded-md text-sm font-medium transition-colors hover:bg-slate-800";

function Navbar() {
  return (
    <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur">
      <nav className="max-w-5xl mx-auto px-4 py-3 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2">
          <span className="h-8 w-8 rounded-full bg-emerald-500 flex items-center justify-center text-slate-950 font-black">
            F
          </span>
          <span className="font-semibold tracking-tight">
            Fake News Detection
          </span>
        </Link>
        <div className="flex items-center gap-2">
          <NavLink
            to="/"
            end
            className={({ isActive }) =>
              `${navLinkClasses} ${
                isActive ? "bg-slate-800 text-emerald-400" : "text-slate-200"
              }`
            }
          >
            Home
          </NavLink>
          <NavLink
            to="/results"
            className={({ isActive }) =>
              `${navLinkClasses} ${
                isActive ? "bg-slate-800 text-emerald-400" : "text-slate-200"
              }`
            }
          >
            Results
          </NavLink>
          <NavLink
            to="/history"
            className={({ isActive }) =>
              `${navLinkClasses} ${
                isActive ? "bg-slate-800 text-emerald-400" : "text-slate-200"
              }`
            }
          >
            History
          </NavLink>
          <NavLink
            to="/admin"
            className={({ isActive }) =>
              `${navLinkClasses} ${
                isActive ? "bg-slate-800 text-emerald-400" : "text-slate-200"
              }`
            }
          >
            Admin
          </NavLink>
        </div>
      </nav>
    </header>
  );
}

export default Navbar;

