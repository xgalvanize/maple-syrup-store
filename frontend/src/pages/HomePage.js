import React, { useState } from "react";
import { useQuery, useMutation, gql } from "@apollo/client";
import ProductCard from "../components/ProductCard";
import { useAuth } from "../state/AuthContext";
import { useNotification } from "../state/NotificationContext";

export const GET_PRODUCTS = gql`
  query Products {
    products {
      id
      name
      description
      priceCents
      imageUrl
    }
  }
`;

const ADD_TO_CART = gql`
  mutation AddToCart($productId: ID!, $quantity: Int) {
    addToCart(productId: $productId, quantity: $quantity) {
      cart { id }
    }
  }
`;

export default function HomePage() {
  const { isLoggedIn } = useAuth();
  const { showNotification } = useNotification();
  const { loading, error, data, refetch } = useQuery(GET_PRODUCTS);
  const [addingProductId, setAddingProductId] = useState(null);
  const [addToCart] = useMutation(ADD_TO_CART, { refetchQueries: ["Cart"] });

  async function handleAdd(productId) {
    if (!isLoggedIn) {
      showNotification("Please log in to add items to your cart.", "error");
      return;
    }
    try {
      setAddingProductId(productId);
      const product = data.products.find((p) => p.id === productId);
      await addToCart({ variables: { productId, quantity: 1 } });
      showNotification(`${product?.name} added to cart!`, "success");
    } catch (err) {
      showNotification("Failed to add item to cart", "error");
    } finally {
      setAddingProductId(null);
    }
  }

  const products = data?.products || [];

  return (
    <div>
      <div className="banner">
        <img src="/images/banner.jpg" alt="Maple Syrup Banner" />
      </div>

      <header className="hero">
        <div>
          <h1>Pure Maple Syrup, Delivered</h1>
          <p>Small-batch, single-origin syrup from local farms.</p>
        </div>
        <div className="hero-badge">Interac e-Transfer</div>
      </header>

      {loading && (
        <div className="state-card" role="status" aria-live="polite">
          <h2>Loading products...</h2>
          <p className="muted">Fresh maple syrup is on the way.</p>
        </div>
      )}

      {error && (
        <div className="state-card" role="alert">
          <h2>Couldn’t load products</h2>
          <p className="muted">{error.message}</p>
          <button className="button" type="button" onClick={() => refetch()}>
            Retry
          </button>
        </div>
      )}

      {!loading && !error && products.length === 0 && (
        <div className="state-card" role="status" aria-live="polite">
          <h2>No products available yet</h2>
          <p className="muted">Please check back soon for our next syrup batch.</p>
        </div>
      )}

      {!loading && !error && products.length > 0 && (
        <div className="grid">
          {products.map((product) => (
            <ProductCard
              key={product.id}
              product={product}
              onAdd={handleAdd}
              isAdding={addingProductId === product.id}
            />
          ))}
        </div>
      )}
    </div>
  );
}
