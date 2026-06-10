const StatCard = ({ icon: Icon, label, value, sub, accent }) => (
  <div style={{
    background: "#fff",
    borderRadius: 16,
    padding: "20px 24px",
    boxShadow: "0 1px 4px rgba(0,0,0,0.07)",
    display: "flex",
    flexDirection: "column",
    gap: 12,
    flex: 1,
    minWidth: 160,
  }}>
    <div style={{
      width: 40, height: 40, borderRadius: 12,
      background: accent + "18",
      display: "flex", alignItems: "center", justifyContent: "center"
    }}>
      <Icon size={20} color={accent} />
    </div>
    <div>
      <p style={{ margin: 0, fontSize: 13, color: "#9ca3af", fontWeight: 500 }}>{label}</p>
      <p style={{ margin: "4px 0 0", fontSize: 26, fontWeight: 700, color: "#111827" }}>{value}</p>
      {sub && <p style={{ margin: "2px 0 0", fontSize: 12, color: "#6b7280" }}>{sub}</p>}
    </div>
  </div>
);
export default StatCard;