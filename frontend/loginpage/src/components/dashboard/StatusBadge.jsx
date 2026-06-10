const StatusBadge = ({ status }) => {
  const colors = {
    Delivered: { bg: "#dcfce7", text: "#16a34a" },
    "In Transit": { bg: "#ffedd5", text: "#ea580c" },
    "Picked Up": { bg: "#dbeafe", text: "#2563eb" },
  };
  const c = colors[status] || { bg: "#f3f4f6", text: "#374151" };
  return (
    <span style={{
      background: c.bg, color: c.text,
      fontSize: 11, fontWeight: 600,
      padding: "3px 10px", borderRadius: 20,
      whiteSpace: "nowrap",
    }}>{status}</span>
  );
};
export default StatusBadge;