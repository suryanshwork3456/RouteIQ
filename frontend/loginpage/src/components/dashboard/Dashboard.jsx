import StatCard from "./StatCard";
import StatusBadge from "./StatusBadge";
import { Package, CheckCircle2, Star,Navigation,
} from "lucide-react";

import { AreaChart, Area, BarChart, Bar, XAxis,YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell,
} from "recharts";

import {weeklyData,deliveryHistory,statusData,
} from "../../data/RiderData";

function Dashboard() {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
      <div style={{ display: "flex", gap: 16, flexWrap: "wrap" }}>
        <StatCard icon={Package} label="Active Orders" value="12" sub="↑ 3 from yesterday" accent="#f97316" />
        <StatCard icon={CheckCircle2} label="Completed" value="58" sub="This week" accent="#22c55e" />
        <StatCard icon={Star} label="Rating" value="4.8" sub="50 reviews" accent="#eab308" />
        <StatCard icon={Navigation} label="Distance Today" value="38 km" sub="142 km this week" accent="#3b82f6" />
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
        <div style={{ background: "#fff", borderRadius: 16, padding: 24, boxShadow: "0 1px 4px rgba(0,0,0,0.07)" }}>
          <p style={{ margin: "0 0 4px", fontWeight: 700, fontSize: 15, color: "#111827" }}>Weekly Deliveries</p>
          <p style={{ margin: "0 0 16px", fontSize: 12, color: "#9ca3af" }}>Mon – Sun performance</p>
          <ResponsiveContainer width="100%" height={180}>
            <AreaChart data={weeklyData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="delivGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#f97316" stopOpacity={0.15} />
                  <stop offset="95%" stopColor="#f97316" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
              <XAxis dataKey="day" tick={{ fontSize: 11, fill: "#9ca3af" }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: "#9ca3af" }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={{ borderRadius: 10, fontSize: 12, border: "none", boxShadow: "0 2px 12px rgba(0,0,0,0.1)" }} />
              <Area type="monotone" dataKey="deliveries" stroke="#f97316" strokeWidth={2.5} fill="url(#delivGrad)" dot={{ r: 4, fill: "#f97316" }} />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div style={{ background: "#fff", borderRadius: 16, padding: 24, boxShadow: "0 1px 4px rgba(0,0,0,0.07)" }}>
          <p style={{ margin: "0 0 4px", fontWeight: 700, fontSize: 15, color: "#111827" }}>Earnings Overview</p>
          <p style={{ margin: "0 0 16px", fontSize: 12, color: "#9ca3af" }}>Daily earnings in ₹</p>
          <ResponsiveContainer width="100%" height={180}>
            <BarChart data={weeklyData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" vertical={false} />
              <XAxis dataKey="day" tick={{ fontSize: 11, fill: "#9ca3af" }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: "#9ca3af" }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={{ borderRadius: 10, fontSize: 12, border: "none", boxShadow: "0 2px 12px rgba(0,0,0,0.1)" }} formatter={(v) => [`₹${v}`, "Earnings"]} />
              <Bar dataKey="earnings" radius={[6, 6, 0, 0]}>
                {weeklyData.map((_, i) => <Cell key={i} fill={i === 5 ? "#f97316" : "#fed7aa"} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1.5fr 1fr", gap: 20 }}>
        <div style={{ background: "#fff", borderRadius: 16, padding: 24, boxShadow: "0 1px 4px rgba(0,0,0,0.07)" }}>
          <p style={{ margin: "0 0 16px", fontWeight: 700, fontSize: 15, color: "#111827" }}>Today's Deliveries</p>
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {deliveryHistory.slice(0, 4).map((d) => (
              <div key={d.id} style={{
                display: "flex", alignItems: "center", gap: 12,
                padding: "10px 14px", borderRadius: 12, background: "#fafafa",
                border: "1px solid #f3f4f6"
              }}>
                <div style={{
                  width: 36, height: 36, borderRadius: 10,
                  background: "#ffedd5", display: "flex", alignItems: "center", justifyContent: "center"
                }}>
                  <Package size={16} color="#f97316" />
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <p style={{ margin: 0, fontSize: 13, fontWeight: 600, color: "#111827" }}>{d.id} · {d.customer}</p>
                  <p style={{ margin: 0, fontSize: 11, color: "#9ca3af", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{d.address}</p>
                </div>
                <div style={{ textAlign: "right", flexShrink: 0 }}>
                  <StatusBadge status={d.status} />
                  <p style={{ margin: "4px 0 0", fontSize: 11, color: "#9ca3af" }}>{d.time}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div style={{ background: "#fff", borderRadius: 16, padding: 24, boxShadow: "0 1px 4px rgba(0,0,0,0.07)" }}>
          <p style={{ margin: "0 0 16px", fontWeight: 700, fontSize: 15, color: "#111827" }}>Order Breakdown</p>
          <ResponsiveContainer width="100%" height={160}>
            <PieChart>
              <Pie data={statusData} cx="50%" cy="50%" innerRadius={45} outerRadius={70} paddingAngle={3} dataKey="value">
                {statusData.map((entry, i) => <Cell key={i} fill={entry.color} />)}
              </Pie>
              <Tooltip contentStyle={{ borderRadius: 10, fontSize: 12, border: "none" }} />
            </PieChart>
          </ResponsiveContainer>
          <div style={{ display: "flex", flexDirection: "column", gap: 6, marginTop: 8 }}>
            {statusData.map((s) => (
              <div key={s.name} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", fontSize: 12 }}>
                <span style={{ display: "flex", alignItems: "center", gap: 6 }}>
                  <span style={{ width: 8, height: 8, borderRadius: "50%", background: s.color, display: "inline-block" }} />
                  <span style={{ color: "#6b7280" }}>{s.name}</span>
                </span>
                <span style={{ fontWeight: 600, color: "#111827" }}>{s.value}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
export default Dashboard;