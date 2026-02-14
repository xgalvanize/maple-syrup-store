import React from "react";
import { useQuery, useMutation, gql } from "@apollo/client";
import { Link } from "react-router-dom";

const GET_CART = gql`
  query Cart {
    cart {
      id
      subtotalCents
      items {
        id
        quantity
        product { id name priceCents }
      }
    }
  }
`;

const UPDATE_ITEM = gql`
  mutation UpdateCartItem($itemId: ID!, $quantity: Int!) {
    updateCartItem(itemId: $itemId, quantity: $quantity) {
      cart { id }
    }
  }
`;

const REMOVE_ITEM = gql`
  mutation RemoveCartItem($itemId: ID!) {
    removeCartItem(itemId: $itemId) {
      cart { id }
    }
  }
`;

export default function CartPage() {
  const { loading, error, data } = useQuery(GET_CART, { fetchPolicy: "cache-and-network" });
  const [updateItem] = useMutation(UPDATE_ITEM, { refetchQueries: ["Cart"] });
  const [removeItem] = useMutation(REMOVE_ITEM, { refetchQueries: ["Cart"] });

  if (loading) return <p>Loading cart...</p>;
  if (error) return <p>Error: {error.message}</p>;

  const cart = data?.cart;
  if (!cart || cart.items.length === 0) {
    return <p>Your cart is empty.</p>;
  }

  return (
    <div className="card">
      <h2>Your Cart</h2>
      <ul className="list">
        {cart.items.map((item) => (
          <li key={item.id} className="list-row">
            <div>
              <strong>{item.product.name}</strong>
              <div className="muted">${(item.product.priceCents / 100).toFixed(2)}</div>
            </div>
            <div className="row">
              <input
                className="input"
                type="number"
                min="1"
                value={item.quantity}
                onChange={(e) => updateItem({ variables: { itemId: item.id, quantity: Number(e.target.value) } })}
              />
              <button className="button-outline" type="button" onClick={() => removeItem({ variables: { itemId: item.id } })}>Remove</button>
            </div>
          </li>
        ))}
      </ul>
      <div className="row space-between">
        <strong>Total: ${(cart.subtotalCents / 100).toFixed(2)}</strong>
        <Link className="button" to="/checkout">Proceed to Checkout</Link>
      </div>
    </div>
  );
}
