import { Users, Zap } from "lucide-react";
import StatCard from "./dashboard/StatCard"; // ya correct relative path
import { nearbyRiders } from "../data/riderData";

function NearbyRiders() {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      <div style={{ display: "flex", gap: 16, flexWrap: "wrap" }}>
        <StatCard icon={Users} label="Riders Nearby" value="4" sub="Within 2 km" accent="#8b5cf6" />
        <StatCard icon={Zap} label="Active Now" value="3" sub="On delivery" accent="#22c55e" />
      </div>
      <div style={{ background: "#fff", borderRadius: 16, padding: 24, boxShadow: "0 1px 4px rgba(0,0,0,0.07)" }}>
        <p style={{ margin: "0 0 16px", fontWeight: 700, fontSize: 15, color: "#111827" }}>Riders in Your Area</p>
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          {nearbyRiders.map((r) => (
            <div key={r.name} style={{
              display: "flex", alignItems: "center", gap: 14,
              padding: "14px 16px", borderRadius: 14,
              background: "#fafafa", border: "1px solid #f3f4f6"
            }}>
              <div style={{
                width: 44, height: 44, borderRadius: "50%",
                background: r.active ? "#dcfce7" : "#f3f4f6",
                display: "flex", alignItems: "center", justifyContent: "center",
                flexShrink: 0, fontSize: 16, fontWeight: 700,
                color: r.active ? "#16a34a" : "#9ca3af"
              }}>
                {r.name[0]}
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <p style={{ margin: 0, fontWeight: 600, fontSize: 14, color: "#111827" }}>{r.name}</p>
                  <span style={{
                    fontSize: 10, fontWeight: 600, padding: "2px 8px", borderRadius: 20,
                    background: r.active ? "#dcfce7" : "#f3f4f6",
                    color: r.active ? "#16a34a" : "#9ca3af"
                  }}>{r.active ? "Active" : "Idle"}</span>
                </div>
                <p style={{ margin: "2px 0 0", fontSize: 12, color: "#9ca3af" }}>{r.deliveries} deliveries today · ⭐ {r.rating}</p>
              </div>
              <div style={{ textAlign: "right", flexShrink: 0 }}>
                <p style={{ margin: 0, fontSize: 14, fontWeight: 700, color: "#f97316" }}>{r.distance}</p>
                <p style={{ margin: "2px 0 0", fontSize: 11, color: "#9ca3af" }}>away</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
export default NearbyRiders;