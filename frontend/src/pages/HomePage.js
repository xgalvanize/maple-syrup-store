import React from "react";
import { useQuery, useMutation, gql } from "@apollo/client";
import ProductCard from "../components/ProductCard";
import { useAuth } from "../state/AuthContext";

const GET_PRODUCTS = gql`
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
  const { loading, error, data } = useQuery(GET_PRODUCTS);
  const [addToCart] = useMutation(ADD_TO_CART, { refetchQueries: ["Cart"] });

  if (loading) return <p>Loading products...</p>;
  if (error) return <p>Error: {error.message}</p>;

  async function handleAdd(productId) {
    if (!isLoggedIn) return alert("Please log in to add items to your cart.");
    await addToCart({ variables: { productId, quantity: 1 } });
  }

  return (
    <div>
      <header className="hero">
        <div>
          <h1>Pure Maple Syrup, Delivered</h1>
          <p>Small-batch, single-origin syrup from local farms.</p>
        </div>
        <div className="hero-badge">Interac e-Transfer</div>
      </header>

      <div className="grid">
        {data.products.map((product) => (
          <ProductCard key={product.id} product={product} onAdd={handleAdd} />
        ))}
      </div>
    </div>
  );
}
