import
 { LayoutDashboard,Package,Map,History, Users, Star, X,Truck, ChevronRight,} from "lucide-react";

 const menuItems = [
  { name: "Dashboard", icon: LayoutDashboard },
  { name: "Delivery Status", icon: Package },
  { name: "Route Map", icon: Map },
  { name: "Delivery History", icon: History },
  { name: "Nearby Riders", icon: Users },
  { name: "Ratings", icon: Star },
];
function Sidebar({
  activeTab,
  setActiveTab,
  sidebarOpen,
  setSidebarOpen,
}) {
  return (
    <>
       <aside style={{
        position: "fixed", left: 0, top: 0, bottom: 0, width: 240,
        background: "#fff", boxShadow: "2px 0 12px rgba(0,0,0,0.08)",
        zIndex: 50, transform: sidebarOpen ? "translateX(0)" : "translateX(-100%)",
        transition: "transform 0.28s cubic-bezier(0.4,0,0.2,1)",
        display: "flex", flexDirection: "column", padding: "24px 16px",
      }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 32 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <div style={{
              width: 36, height: 36, borderRadius: 10,
              background: "linear-gradient(135deg, #f97316, #ea580c)",
              display: "flex", alignItems: "center", justifyContent: "center"
            }}>
              <Truck size={18} color="#fff" />
            </div>
            <span style={{ fontSize: 18, fontWeight: 800, color: "#f97316", letterSpacing: -0.5 }}>LogiFlow</span>
          </div>
          <button onClick={() => setSidebarOpen(false)} style={{ border: "none", background: "none", cursor: "pointer", padding: 4, borderRadius: 8, color: "#9ca3af" }}>
            <X size={18} />
          </button>
        </div>

        <p style={{ margin: "0 0 8px 8px", fontSize: 10, fontWeight: 700, color: "#d1d5db", textTransform: "uppercase", letterSpacing: 1 }}>Menu</p>

        <nav style={{ display: "flex", flexDirection: "column", gap: 4, flex: 1 }}>
          {menuItems.map(({ name, icon: Icon }) => {
            const active = activeTab === name;
            return (
              <button
                key={name}
                onClick={() => { setActiveTab(name); setSidebarOpen(false); }}
                style={{
                  display: "flex", alignItems: "center", gap: 12,
                  width: "100%", padding: "11px 14px", border: "none",
                  borderRadius: 12, cursor: "pointer", textAlign: "left", fontSize: 14,
                  fontWeight: active ? 700 : 500, transition: "all 0.15s",
                  background: active ? "#fff7ed" : "transparent",
                  color: active ? "#f97316" : "#4b5563",
                  boxShadow: active ? "inset 0 0 0 1.5px #fed7aa" : "none",
                }}
              >
                <Icon size={18} />
                {name}
                {active && <ChevronRight size={14} style={{ marginLeft: "auto" }} />}
              </button>
            );
          })}
        </nav>

        <div style={{
          marginTop: 24, padding: "14px 16px", borderRadius: 14,
          background: "#fff7ed", border: "1px solid #fed7aa"
        }}>
          <p style={{ margin: "0 0 2px", fontSize: 12, fontWeight: 700, color: "#f97316" }}>Today's Goal</p>
          <p style={{ margin: "0 0 8px", fontSize: 11, color: "#9a3412" }}>20 deliveries · ₹1,600</p>
          <div style={{ height: 6, borderRadius: 6, background: "#fed7aa", overflow: "hidden" }}>
            <div style={{ width: "60%", height: "100%", borderRadius: 6, background: "#f97316" }} />
          </div>
          <p style={{ margin: "4px 0 0", fontSize: 11, color: "#9ca3af" }}>12 / 20 completed</p>
        </div>
      </aside>
    </>
  );
}

export default Sidebar;