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
        <Link to="/cart" className="nav-link-cart" title="View shopping cart">
          Cart
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
