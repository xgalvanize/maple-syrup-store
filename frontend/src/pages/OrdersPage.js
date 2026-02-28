import React, { useState } from "react";
import { useQuery, gql } from "@apollo/client";

const BACKEND_BASE_URL = process.env.REACT_APP_BACKEND_URL || "http://localhost:8000";

const GET_ORDERS = gql`
  query Orders {
    orders {
      id
      status
      totalCents
      createdAt
      items { id quantity priceCents product { name } }
    }
  }
`;

export default function OrdersPage() {
  const { loading, error, data } = useQuery(GET_ORDERS, { fetchPolicy: "network-only" });
  const [downloadStatus, setDownloadStatus] = useState({});

  const handleDownloadReceipt = async (orderId) => {
    console.log("Download clicked for order:", orderId);
    setDownloadStatus(prev => ({ ...prev, [orderId]: "generating" }));
    
    try {
      const token = localStorage.getItem('token');
      console.log("Token present:", !!token);
      
      // Simple fetch call to REST endpoint
      const response = await fetch(`${BACKEND_BASE_URL}/api/receipts/download/${orderId}/`, {
        method: 'GET',
        headers: {
          'Authorization': `JWT ${token}`
        }
      });

      console.log("Response status:", response.status);
      console.log("Response headers:", {
        'content-type': response.headers.get('content-type'),
        'content-length': response.headers.get('content-length'),
        'content-disposition': response.headers.get('content-disposition')
      });

      if (response.ok) {
        try {
          // Get the blob and download
          const blob = await response.blob();
          console.log("Blob created:", blob.type, blob.size, "bytes");
          
          const url = window.URL.createObjectURL(blob);
          console.log("Object URL created:", url);
          
          const a = document.createElement('a');
          a.href = url;
          a.download = `Maple-Syrup-Order-${orderId}-Receipt.pdf`;
          document.body.appendChild(a);
          console.log("About to click download link");
          a.click();
          window.URL.revokeObjectURL(url);
          a.remove();
          console.log("Download complete");
          
          setDownloadStatus(prev => ({ ...prev, [orderId]: "success" }));
          setTimeout(() => {
            setDownloadStatus(prev => ({ ...prev, [orderId]: null }));
          }, 2000);
        } catch (blobErr) {
          console.error("Error processing blob:", blobErr);
          setDownloadStatus(prev => ({ ...prev, [orderId]: "error" }));
        }
      } else {
        const errorText = await response.text();
        console.error("Download failed:", response.status, response.statusText, errorText);
        setDownloadStatus(prev => ({ ...prev, [orderId]: "error" }));
      }
    } catch (err) {
      console.error("Error downloading receipt:", err);
      setDownloadStatus(prev => ({ ...prev, [orderId]: "error" }));
    }
  };

  if (loading) return <p>Loading orders...</p>;
  if (error) return <p>Error: {error.message}</p>;

  if (!data?.orders || data.orders.length === 0) {
    return <p>You have no orders yet.</p>;
  }

  return (
    <div>
      <h2>Your Orders</h2>
      <div className="grid">
        {data.orders.map((order) => (
          <div key={order.id} className="card">
            <div className="row space-between">
              <strong>Order #{order.id}</strong>
              <span className="badge">{order.status}</span>
            </div>
            <ul className="list">
              {order.items.map((item) => (
                <li key={item.id} className="list-row">
                  <span>{item.product?.name}</span>
                  <span>Qty {item.quantity}</span>
                </li>
              ))}
            </ul>
            <div className="row space-between">
              <span>Total</span>
              <strong>${(order.totalCents / 100).toFixed(2)}</strong>
            </div>
            <div className="row space-between" style={{ marginTop: "15px" }}>
              <button
                onClick={() => handleDownloadReceipt(order.id)}
                disabled={downloadStatus[order.id] === "generating"}
                style={{
                  padding: "8px 12px",
                  backgroundColor: downloadStatus[order.id] === "error" ? "#dc3545" : "#8B4513",
                  color: "white",
                  border: "none",
                  borderRadius: "4px",
                  cursor: downloadStatus[order.id] === "generating" ? "not-allowed" : "pointer",
                  opacity: downloadStatus[order.id] === "generating" ? 0.6 : 1,
                }}
              >
                {downloadStatus[order.id] === "generating" && "Generating..."}
                {downloadStatus[order.id] === "success" && "✓ Downloaded"}
                {downloadStatus[order.id] === "error" && "✗ Failed"}
                {!downloadStatus[order.id] && "📥 Download Receipt"}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
