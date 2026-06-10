import { useState, useRef, useEffect } from "react";
import Navbar from "../components/Navbar";
import Sidebar from "../components/Sidebar";
import Dashboard from "../components/dashboard/Dashboard";
import DeliveryStatus from "../components/delivery/DeliveryStatus";
import DeliveryHistory from "../components/delivery/DeliveryHistory";
import RouteMap from "../components/RouteMap";
import NearbyRiders from "../components/NearbyRiders";
import Ratings from "../components/Ratings";


function RiderDashboard() {
  const [activeTab, setActiveTab] = useState("Dashboard");
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const profileRef = useRef(null);

  useEffect(() => {
    const handler = (e) => {
      if (profileRef.current && !profileRef.current.contains(e.target)) {
        setProfileOpen(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const renderContent = () => {
    switch (activeTab) {
      case "Delivery Status": return <DeliveryStatus />;
      case "Route Map": return <RouteMap />;
      case "Delivery History": return <DeliveryHistory />;
      case "Nearby Riders": return <NearbyRiders />;
      case "Ratings": return <Ratings />;
      default: return <Dashboard />;
    }
  };
   return (
  <div
    style={{
      display: "flex",
      minHeight: "100vh",
      background: "#f8fafc",
    }}
  >
    <Sidebar
      activeTab={activeTab}
      setActiveTab={setActiveTab}
      sidebarOpen={sidebarOpen}
      setSidebarOpen={setSidebarOpen}
    />

    <div style={{ flex: 1, display: "flex", flexDirection: "column" }}>
      <Navbar
        activeTab={activeTab}
        profileOpen={profileOpen}
        setProfileOpen={setProfileOpen}
        profileRef={profileRef}
        setSidebarOpen={setSidebarOpen}
      />

      <main style={{ padding: 24, flex: 1 }}>
        {renderContent()}
      </main>
    </div>
  </div>
);
}
export default RiderDashboard;
