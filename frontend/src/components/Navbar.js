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
        <div className="logo-icon">🍁</div>
        <Link to="/" className="nav-title">Maple Syrup</Link>
      </div>
      <div className="nav-links">
        <Link to="/">Shop</Link>
        <Link to="/cart" className="nav-link-cart">
          Cart
          {cartCount > 0 && <span className="cart-badge">{cartCount}</span>}
        </Link>
        {isLoggedIn && <Link to="/orders">Orders</Link>}
        {isLoggedIn && isStaff && <Link to="/admin">Admin</Link>}
        {!isLoggedIn && <Link to="/login">Login</Link>}
        {!isLoggedIn && <Link to="/register">Register</Link>}
        {isLoggedIn && (
          <button className="linklike" type="button" onClick={logout}>Logout</button>
        )}
      </div>
    </nav>
  );
}
