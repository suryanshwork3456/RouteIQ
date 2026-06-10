import { Menu, Bell } from "lucide-react";
function Navbar({activeTab,profileOpen,setProfileOpen,profileRef,setSidebarOpen,}) {
  return (
    <>
      <header style={{
          background: "#fff", borderBottom: "1px solid #f3f4f6",
          padding: "0 24px", height: 64,
          display: "flex", alignItems: "center", justifyContent: "space-between",
          position: "sticky", top: 0, zIndex: 30,
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
            <button
              onClick={() => setSidebarOpen(true)}
              style={{
                border: "1px solid #e5e7eb", background: "#fff", cursor: "pointer",
                width: 38, height: 38, borderRadius: 10,
                display: "flex", alignItems: "center", justifyContent: "center", color: "#374151"
              }}
            >
              <Menu size={20} />
            </button>
            <div>
              <p style={{ margin: 0, fontSize: 16, fontWeight: 700, color: "#111827" }}>{activeTab}</p>
              <p style={{ margin: 0, fontSize: 12, color: "#9ca3af" }}>Wednesday, 11 Jun 2025</p>
            </div>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <button style={{
              border: "1px solid #e5e7eb", background: "#fff", cursor: "pointer",
              width: 38, height: 38, borderRadius: 10, display: "flex", alignItems: "center", justifyContent: "center",
              position: "relative", color: "#374151"
            }}>
              <Bell size={18} />
              <span style={{
                position: "absolute", top: 6, right: 6, width: 8, height: 8,
                borderRadius: "50%", background: "#f97316", border: "2px solid #fff"
              }} />
            </button>

            <div ref={profileRef} style={{ position: "relative" }}>
              <button
                onClick={() => setProfileOpen((p) => !p)}
                style={{
                  display: "flex", alignItems: "center", gap: 10,
                  border: "1px solid #e5e7eb", background: "#fff",
                  padding: "6px 12px 6px 6px", borderRadius: 40, cursor: "pointer"
                }}
              >
                <img
                  src="https://i.pravatar.cc/40?img=12"
                  alt="Rider"
                  style={{ width: 30, height: 30, borderRadius: "50%", objectFit: "cover" }}
                />
                <span style={{ fontSize: 13, fontWeight: 600, color: "#111827" }}>Ravi Kumar</span>
              </button>

              {profileOpen && (
                <div style={{
                  position: "absolute", right: 0, top: "calc(100% + 10px)",
                  width: 240, background: "#fff", borderRadius: 16,
                  boxShadow: "0 8px 32px rgba(0,0,0,0.12)", border: "1px solid #f3f4f6",
                  overflow: "hidden", zIndex: 100,
                }}>
                  <div style={{
                    padding: "20px 20px 16px",
                    borderBottom: "1px solid #f3f4f6",
                    display: "flex", flexDirection: "column", alignItems: "center", gap: 10
                  }}>
                    <img
                      src="https://i.pravatar.cc/80?img=12"
                      alt="Rider"
                      style={{ width: 64, height: 64, borderRadius: "50%", objectFit: "cover", border: "3px solid #fed7aa" }}
                    />
                    <div style={{ textAlign: "center" }}>
                      <p style={{ margin: 0, fontWeight: 700, fontSize: 15, color: "#111827" }}>Ravi Kumar</p>
                      <p style={{ margin: "2px 0 0", fontSize: 12, color: "#9ca3af" }}>ravi.kumar@routeiq.in</p>
                    </div>
                    <div style={{ display: "flex", gap: 16, marginTop: 4 }}>
                      {[{ label: "Rating", value: "4.8" }, { label: "Trips", value: "58" }, { label: "km", value: "142" }].map((s) => (
                        <div key={s.label} style={{ textAlign: "center" }}>
                          <p style={{ margin: 0, fontWeight: 700, fontSize: 15, color: "#f97316" }}>{s.value}</p>
                          <p style={{ margin: 0, fontSize: 10, color: "#9ca3af" }}>{s.label}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                  <div style={{ padding: "8px" }}>
                    {["My Profile", "Settings", "Support"].map((item) => (
                      <button key={item} style={{
                        width: "100%", textAlign: "left", padding: "10px 12px",
                        fontSize: 13, color: "#374151", background: "none", border: "none",
                        borderRadius: 10, cursor: "pointer", fontWeight: 500,
                      }}
                        onMouseOver={(e) => e.target.style.background = "#f9fafb"}
                        onMouseOut={(e) => e.target.style.background = "none"}
                      >{item}</button>
                    ))}
                    <div style={{ borderTop: "1px solid #f3f4f6", marginTop: 4, paddingTop: 4 }}>
                      <button style={{
                        width: "100%", textAlign: "left", padding: "10px 12px",
                        fontSize: 13, color: "#ef4444", background: "none", border: "none",
                        borderRadius: 10, cursor: "pointer", fontWeight: 500,
                      }}>Sign Out</button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </header>

    </>
  );
}

export default Navbar;