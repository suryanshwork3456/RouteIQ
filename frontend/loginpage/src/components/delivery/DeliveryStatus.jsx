import StatCard from "../dashboard/StatCard";
import StatusBadge from "../dashboard/StatusBadge";

import { Package,Truck, CheckCircle2,
} from "lucide-react";
import { deliveryHistory } from "../../data/RiderData";
function DeliveryStatus() {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      <div style={{ display: "flex", gap: 16, flexWrap: "wrap" }}>
        <StatCard icon={Package} label="Picked Up" value="3" sub="Ready to deliver" accent="#3b82f6" />
        <StatCard icon={Truck} label="On The Way" value="5" sub="En route" accent="#f97316" />
        <StatCard icon={CheckCircle2} label="Delivered" value="12" sub="Completed today" accent="#22c55e" />
      </div>
      <div style={{ background: "#fff", borderRadius: 16, padding: 24, boxShadow: "0 1px 4px rgba(0,0,0,0.07)" }}>
        <p style={{ margin: "0 0 16px", fontWeight: 700, fontSize: 15, color: "#111827" }}>Live Status Feed</p>
        <div style={{ display: "flex", flexDirection: "column", gap: 0 }}>
          {deliveryHistory.map((d, i) => (
            <div key={d.id} style={{
              display: "flex", alignItems: "flex-start", gap: 14,
              paddingBottom: i < deliveryHistory.length - 1 ? 16 : 0,
              marginBottom: i < deliveryHistory.length - 1 ? 16 : 0,
              borderBottom: i < deliveryHistory.length - 1 ? "1px solid #f3f4f6" : "none"
            }}>
              <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 4 }}>
                <div style={{
                  width: 36, height: 36, borderRadius: "50%",
                  background: d.status === "Delivered" ? "#dcfce7" : d.status === "In Transit" ? "#ffedd5" : "#dbeafe",
                  display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0
                }}>
                  {d.status === "Delivered" ? <CheckCircle2 size={16} color="#22c55e" /> :
                    d.status === "In Transit" ? <Truck size={16} color="#f97316" /> :
                      <Package size={16} color="#3b82f6" />}
                </div>
                {i < deliveryHistory.length - 1 && <div style={{ width: 1, height: 20, background: "#e5e7eb" }} />}
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                  <p style={{ margin: 0, fontWeight: 600, fontSize: 13, color: "#111827" }}>{d.id} · {d.customer}</p>
                  <StatusBadge status={d.status} />
                </div>
                <p style={{ margin: "3px 0 0", fontSize: 12, color: "#9ca3af" }}>{d.address} · {d.time} · {d.amount}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
export default DeliveryStatus;