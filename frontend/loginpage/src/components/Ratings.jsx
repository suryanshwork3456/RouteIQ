import { Star, Award, Users } from "lucide-react";
import StatCard from "./dashboard/StatCard";
import { ratingReviews, ratingDist } from "../data/riderData";

function Ratings() {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      <div style={{ display: "flex", gap: 16, flexWrap: "wrap" }}>
        <StatCard icon={Star} label="Average Rating" value="4.8" sub="Last 30 days" accent="#eab308" />
        <StatCard icon={Award} label="Top Performer" value="#3" sub="In your zone" accent="#8b5cf6" />
        <StatCard icon={Users} label="Total Reviews" value="50" sub="All time" accent="#f97316" />
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
        <div style={{ background: "#fff", borderRadius: 16, padding: 24, boxShadow: "0 1px 4px rgba(0,0,0,0.07)" }}>
          <p style={{ margin: "0 0 16px", fontWeight: 700, fontSize: 15, color: "#111827" }}>Rating Distribution</p>
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {ratingDist.map((r) => (
              <div key={r.stars} style={{ display: "flex", alignItems: "center", gap: 10 }}>
                <span style={{ width: 24, fontSize: 12, color: "#6b7280", flexShrink: 0 }}>{r.stars}</span>
                <div style={{ flex: 1, height: 8, borderRadius: 6, background: "#f3f4f6", overflow: "hidden" }}>
                  <div style={{ width: `${r.pct}%`, height: "100%", borderRadius: 6, background: r.pct > 50 ? "#f97316" : r.pct > 0 ? "#fed7aa" : "#f3f4f6", transition: "width 0.5s" }} />
                </div>
                <span style={{ width: 28, fontSize: 12, color: "#111827", fontWeight: 600, flexShrink: 0, textAlign: "right" }}>{r.count}</span>
              </div>
            ))}
          </div>
        </div>
        <div style={{ background: "#fff", borderRadius: 16, padding: 24, boxShadow: "0 1px 4px rgba(0,0,0,0.07)" }}>
          <p style={{ margin: "0 0 16px", fontWeight: 700, fontSize: 15, color: "#111827" }}>Recent Reviews</p>
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {ratingReviews.map((r) => (
              <div key={r.customer} style={{ paddingBottom: 12, borderBottom: "1px solid #f3f4f6" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 4 }}>
                  <span style={{ fontSize: 13, fontWeight: 600, color: "#111827" }}>{r.customer}</span>
                  <span style={{ fontSize: 11, color: "#9ca3af" }}>{r.date}</span>
                </div>
                <p style={{ margin: "0 0 4px", fontSize: 12, color: "#6b7280" }}>{r.comment}</p>
                <span style={{ fontSize: 13, color: "#eab308" }}>{"★".repeat(r.rating)}{"☆".repeat(5 - r.rating)}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
export default Ratings;