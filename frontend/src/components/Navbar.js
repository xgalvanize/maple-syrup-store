import React from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../state/AuthContext";
import { useQuery, gql } from "@apollo/client";

const GET_CART = gql`
  query Cart {
    cart {
      id
      items {
        id
      }
    }
  }
`;

const ME = gql`
  query Me {
    me {
      id
      isStaff
    }
  }
`;

export default function Navbar() {
  const { isLoggedIn, logout } = useAuth();
  const { data } = useQuery(GET_CART, { skip: !isLoggedIn, fetchPolicy: "cache-and-network" });
  const { data: meData } = useQuery(ME, { skip: !isLoggedIn });
  const cartCount = data?.cart?.items?.length || 0;
  const isStaff = meData?.me?.isStaff;

  return (
    <nav className="nav">
      <div className="nav-brand">
        <div className="logo-icon" title="Maple Syrup Store">🍁</div>
        <Link to="/" className="nav-title" title="Home">Maple Syrup</Link>
      </div>
      <div className="nav-links">
        <Link to="/" title="Browse products">Shop</Link>
        <Link
          to="/cart"
          className="nav-link-cart"
          title="View shopping cart"
          aria-label="Cart"
        >
          <svg
            className="cart-icon"
            viewBox="0 0 24 24"
            aria-hidden="true"
            focusable="false"
          >
            <path
              d="M3 4h2l1.7 9.1a2 2 0 0 0 2 1.6h7.6a2 2 0 0 0 2-1.5L20 7H7"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <circle cx="10" cy="19" r="1.8" fill="currentColor" />
            <circle cx="17" cy="19" r="1.8" fill="currentColor" />
          </svg>
          {cartCount > 0 && <span className="cart-badge" title={`${cartCount} items in cart`}>{cartCount}</span>}
        </Link>
        {isLoggedIn && <Link to="/orders" title="View your orders">Orders</Link>}
        {isLoggedIn && isStaff && <Link to="/admin" title="Admin dashboard">Admin</Link>}
        {!isLoggedIn && <Link to="/login" title="Sign in to your account">Login</Link>}
        {!isLoggedIn && <Link to="/register" title="Create a new account">Register</Link>}
        {isLoggedIn && (
          <button className="linklike" type="button" onClick={logout} title="Sign out">Logout</button>
        )}
      </div>
    </nav>
  );
}
