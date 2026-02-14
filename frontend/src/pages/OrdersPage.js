import React from "react";
import { useQuery, gql } from "@apollo/client";

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
          </div>
        ))}
      </div>
    </div>
  );
}
