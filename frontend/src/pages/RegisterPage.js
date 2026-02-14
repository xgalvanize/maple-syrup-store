import React, { useState } from "react";
import { useMutation, gql } from "@apollo/client";
import { useNavigate } from "react-router-dom";

const REGISTER = gql`
  mutation RegisterUser($username: String!, $password: String!, $email: String) {
    registerUser(username: $username, password: $password, email: $email) {
      user { id username }
    }
  }
`;

export default function RegisterPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [email, setEmail] = useState("");
  const navigate = useNavigate();

  const [registerUser, { loading, error }] = useMutation(REGISTER);

  async function handleSubmit(e) {
    e.preventDefault();
    await registerUser({ variables: { username, password, email } });
    navigate("/login");
  }

  return (
    <div className="card narrow">
      <h2>Create Account</h2>
      <form className="form" onSubmit={handleSubmit}>
        <label className="label">Username</label>
        <input className="input" value={username} onChange={(e) => setUsername(e.target.value)} />

        <label className="label">Email</label>
        <input className="input" type="email" value={email} onChange={(e) => setEmail(e.target.value)} />

        <label className="label">Password</label>
        <input className="input" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />

        <button className="button" type="submit" disabled={loading}>{loading ? "Creating..." : "Register"}</button>
      </form>
      {error && <p className="error">{error.message}</p>}
    </div>
  );
}
