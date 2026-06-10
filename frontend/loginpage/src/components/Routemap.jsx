import { Clock, Navigation, Zap } from "lucide-react";
import StatCard from "./dashboard/StatCard";

function RouteMap() {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      <div style={{ display: "flex", gap: 16, flexWrap: "wrap" }}>
        <StatCard icon={Clock} label="Est. Time" value="24 min" sub="Next delivery" accent="#8b5cf6" />
        <StatCard icon={Navigation} label="Distance Left" value="8.4 km" sub="To next stop" accent="#f97316" />
        <StatCard icon={Zap} label="Speed" value="32 km/h" sub="Current speed" accent="#22c55e" />
      </div>
      <div style={{ background: "#fff", borderRadius: 16, padding: 24, boxShadow: "0 1px 4px rgba(0,0,0,0.07)" }}>
        <p style={{ margin: "0 0 16px", fontWeight: 700, fontSize: 15, color: "#111827" }}>Route Map</p>
        <div style={{
          height: 280, borderRadius: 12,
          background: "linear-gradient(135deg, #e0f2fe 0%, #bae6fd 30%, #e0f2fe 60%, #dbeafe 100%)",
          display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
          position: "relative", overflow: "hidden", border: "1px solid #e0f2fe"
        }}>
          <svg width="100%" height="100%" style={{ position: "absolute", top: 0, left: 0 }} viewBox="0 0 600 280" preserveAspectRatio="none">
            <path d="M80,220 Q200,180 280,140 Q360,100 480,80" stroke="#f97316" strokeWidth="3" fill="none" strokeDasharray="8 4" />
            <circle cx="80" cy="220" r="10" fill="#f97316" />
            <circle cx="480" cy="80" r="10" fill="#22c55e" />
            <circle cx="280" cy="140" r="8" fill="#3b82f6" />
          </svg>
          <div style={{ zIndex: 1, display: "flex", flexDirection: "column", alignItems: "center", gap: 8 }}>
            <Navigation size={28} color="#f97316" />
            <p style={{ margin: 0, fontSize: 13, fontWeight: 600, color: "#1e40af" }}>Route visualization</p>
            <p style={{ margin: 0, fontSize: 12, color: "#3b82f6" }}>3 stops on today's route</p>
          </div>
        </div>
        <div style={{ display: "flex", gap: 12, marginTop: 16 }}>
          {[
            { label: "Start", address: "Warehouse, Sector 18", color: "#f97316" },
            { label: "Stop 1", address: "Order #2841, Noida", color: "#3b82f6" },
            { label: "End", address: "Order #2840, Delhi", color: "#22c55e" },
          ].map((s) => (
            <div key={s.label} style={{
              flex: 1, padding: "12px 14px", borderRadius: 12, background: "#fafafa",
              border: "1px solid #f3f4f6"
            }}>
              <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 4 }}>
                <div style={{ width: 8, height: 8, borderRadius: "50%", background: s.color }} />
                <p style={{ margin: 0, fontSize: 11, fontWeight: 700, color: s.color, textTransform: "uppercase", letterSpacing: 0.5 }}>{s.label}</p>
              </div>
              <p style={{ margin: 0, fontSize: 12, color: "#374151" }}>{s.address}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
export default RouteMap;
