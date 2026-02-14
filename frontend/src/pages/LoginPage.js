import React, { useState } from "react";
import { useMutation, gql } from "@apollo/client";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../state/AuthContext";

const LOGIN = gql`
  mutation TokenAuth($username: String!, $password: String!) {
    tokenAuth(username: $username, password: $password) { token }
  }
`;

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const { login } = useAuth();
  const navigate = useNavigate();

  const [tokenAuth, { loading, error }] = useMutation(LOGIN);

  async function handleSubmit(e) {
    e.preventDefault();
    const result = await tokenAuth({ variables: { username, password } });
    login(result.data.tokenAuth.token);
    navigate("/");
  }

  return (
    <div className="card narrow">
      <h2>Login</h2>
      <form className="form" onSubmit={handleSubmit}>
        <label className="label">Username</label>
        <input className="input" value={username} onChange={(e) => setUsername(e.target.value)} />

        <label className="label">Password</label>
        <input className="input" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />

        <button className="button" type="submit" disabled={loading}>{loading ? "Loading..." : "Login"}</button>
      </form>
      {error && <p className="error">{error.message}</p>}
    </div>
  );
}
