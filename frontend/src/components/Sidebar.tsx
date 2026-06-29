import { NavLink } from "react-router-dom";

const navItems = [
  { to: "/unit-converter", label: "Unit Converter", icon: "🔢" },
  { to: "/linewidth-converter", label: "Linewidth Converter", icon: "📏" },
  { to: "/", label: "About", icon: "ℹ️", end: true },
];

export function Sidebar() {
  return (
    <aside className="flex w-64 shrink-0 flex-col border-r border-slate-200 bg-white">
      <div className="border-b border-slate-200 px-5 py-4">
        <div className="flex items-center gap-2">
          <span className="text-xl">🔬</span>
          <div>
            <h1 className="text-sm font-semibold text-slate-900">
              Photonics Calculator
            </h1>
            <p className="text-xs text-slate-500">React frontend</p>
          </div>
        </div>
      </div>
      <nav className="flex flex-col gap-1 p-3">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.end}
            className={({ isActive }) =>
              [
                "rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-sky-100 text-sky-900"
                  : "text-slate-600 hover:bg-slate-100 hover:text-slate-900",
              ].join(" ")
            }
          >
            <span className="mr-2">{item.icon}</span>
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
