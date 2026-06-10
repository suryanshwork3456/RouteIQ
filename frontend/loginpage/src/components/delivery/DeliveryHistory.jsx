import StatusBadge from "../dashboard/StatusBadge";
import {LineChart,Line, XAxis,YAxis,CartesianGrid,Tooltip,ResponsiveContainer,
} from "recharts";

import { monthlyEarnings,deliveryHistory,
} from "../../data/RiderData";

function DeliveryHistory() {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      <div style={{ background: "#fff", borderRadius: 16, padding: 24, boxShadow: "0 1px 4px rgba(0,0,0,0.07)" }}>
        <p style={{ margin: "0 0 4px", fontWeight: 700, fontSize: 15, color: "#111827" }}>Monthly Earnings Trend</p>
        <p style={{ margin: "0 0 16px", fontSize: 12, color: "#9ca3af" }}>January – June 2025</p>
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={monthlyEarnings} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
            <XAxis dataKey="month" tick={{ fontSize: 11, fill: "#9ca3af" }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fontSize: 11, fill: "#9ca3af" }} axisLine={false} tickLine={false} />
            <Tooltip contentStyle={{ borderRadius: 10, fontSize: 12, border: "none", boxShadow: "0 2px 12px rgba(0,0,0,0.1)" }} formatter={(v) => [`₹${v}`, "Earnings"]} />
            <Line type="monotone" dataKey="earnings" stroke="#f97316" strokeWidth={3} dot={{ r: 5, fill: "#f97316", stroke: "#fff", strokeWidth: 2 }} activeDot={{ r: 7 }} />
          </LineChart>
        </ResponsiveContainer>
      </div>
      <div style={{ background: "#fff", borderRadius: 16, padding: 24, boxShadow: "0 1px 4px rgba(0,0,0,0.07)" }}>
        <p style={{ margin: "0 0 16px", fontWeight: 700, fontSize: 15, color: "#111827" }}>All Deliveries</p>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
          <thead>
            <tr>
              {["Order", "Customer", "Address", "Time", "Amount", "Status"].map((h) => (
                <th key={h} style={{ textAlign: "left", padding: "8px 12px", color: "#9ca3af", fontWeight: 600, fontSize: 11, textTransform: "uppercase", letterSpacing: 0.5, background: "#fafafa", borderBottom: "1px solid #f3f4f6" }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {deliveryHistory.map((d, i) => (
              <tr key={d.id} style={{ borderBottom: i < deliveryHistory.length - 1 ? "1px solid #f9fafb" : "none" }}>
                <td style={{ padding: "12px", fontWeight: 600, color: "#f97316" }}>{d.id}</td>
                <td style={{ padding: "12px", color: "#111827" }}>{d.customer}</td>
                <td style={{ padding: "12px", color: "#6b7280", maxWidth: 160 }}>{d.address}</td>
                <td style={{ padding: "12px", color: "#6b7280" }}>{d.time}</td>
                <td style={{ padding: "12px", fontWeight: 600, color: "#111827" }}>{d.amount}</td>
                <td style={{ padding: "12px" }}><StatusBadge status={d.status} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
export default DeliveryHistory;