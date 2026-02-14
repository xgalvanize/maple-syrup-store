import React, { useState, useEffect } from "react";
import { useMutation, useQuery, useLazyQuery, gql } from "@apollo/client";
import { useNavigate } from "react-router-dom";

const CHECKOUT = gql`
  mutation Checkout(
    $paymentReference: String!
    $payerEmail: String!
    $shippingAddress1: String!
    $shippingAddress2: String
    $shippingCity: String!
    $shippingCountry: String!
    $shippingRegion: String!
    $shippingPostal: String!
  ) {
    checkout(
      paymentReference: $paymentReference
      payerEmail: $payerEmail
      shippingAddress1: $shippingAddress1
      shippingAddress2: $shippingAddress2
      shippingCity: $shippingCity
      shippingCountry: $shippingCountry
      shippingRegion: $shippingRegion
      shippingPostal: $shippingPostal
    ) {
      order { id status paymentReference payerEmail totalCents shippingCents }
    }
  }
`;

const GET_CART = gql`
  query Cart {
    cart {
      id
      subtotalCents
    }
  }
`;

const SHIPPING_ESTIMATE = gql`
  query ShippingEstimate($country: String!, $region: String!, $postal: String!) {
    shippingEstimate(country: $country, region: $region, postal: $postal) {
      cents
      zone
    }
  }
`;

export default function CheckoutPage() {
  const navigate = useNavigate();
  const [paymentReference, setPaymentReference] = useState("");
  const [payerEmail, setPayerEmail] = useState("");
  const [shippingAddress1, setShippingAddress1] = useState("");
  const [shippingAddress2, setShippingAddress2] = useState("");
  const [shippingCity, setShippingCity] = useState("");
  const [shippingCountry, setShippingCountry] = useState("CA");
  const [shippingRegion, setShippingRegion] = useState("ON");
  const [shippingPostal, setShippingPostal] = useState("");

  const { data: cartData } = useQuery(GET_CART, { fetchPolicy: "cache-and-network" });
  const [fetchShipping, { data: shippingData }] = useLazyQuery(SHIPPING_ESTIMATE);
  const [checkout, { data, loading, error }] = useMutation(CHECKOUT, { refetchQueries: ["Cart", "Orders"] });

  useEffect(() => {
    if (shippingCountry && shippingRegion && shippingPostal) {
      fetchShipping({ variables: { country: shippingCountry, region: shippingRegion, postal: shippingPostal } });
    }
  }, [shippingCountry, shippingRegion, shippingPostal, fetchShipping]);

  async function handleSubmit(e) {
    e.preventDefault();
    const result = await checkout({
      variables: {
        paymentReference,
        payerEmail,
        shippingAddress1,
        shippingAddress2,
        shippingCity,
        shippingCountry,
        shippingRegion,
        shippingPostal,
      }
    });
    if (result?.data?.checkout?.order?.id) {
      navigate("/orders");
    }
  }

  const subtotal = cartData?.cart?.subtotalCents || 0;
  const shippingCents = shippingData?.shippingEstimate?.cents || 0;
  const shippingZone = shippingData?.shippingEstimate?.zone || "";
  const total = subtotal + shippingCents;

  return (
    <div className="card">
      <h2>Checkout (Interac e-Transfer)</h2>
      <p className="muted">Send an Interac e-Transfer to payments@maplesyrup.co and enter the confirmation number below.</p>
      <form className="form" onSubmit={handleSubmit}>
        <label className="label">Street Address</label>
        <input className="input" value={shippingAddress1} onChange={(e) => setShippingAddress1(e.target.value)} required />

        <label className="label">Address Line 2 (Optional)</label>
        <input className="input" value={shippingAddress2} onChange={(e) => setShippingAddress2(e.target.value)} />

        <label className="label">City</label>
        <input className="input" value={shippingCity} onChange={(e) => setShippingCity(e.target.value)} required />

        <label className="label">Transfer Confirmation Number</label>
        <input className="input" value={paymentReference} onChange={(e) => setPaymentReference(e.target.value)} required />

        <label className="label">Payer Email</label>
        <input className="input" type="email" value={payerEmail} onChange={(e) => setPayerEmail(e.target.value)} required />

        <label className="label">Shipping Country</label>
        <select className="input" value={shippingCountry} onChange={(e) => setShippingCountry(e.target.value)} required>
          <option value="CA">Canada</option>
          <option value="US">United States</option>
          <option value="OTHER">Other</option>
        </select>

        <label className="label">Shipping Province/Region</label>
        {shippingCountry === "CA" ? (
          <select className="input" value={shippingRegion} onChange={(e) => setShippingRegion(e.target.value)} required>
            <option value="ON">Ontario</option>
            <option value="QC">Quebec</option>
            <option value="BC">British Columbia</option>
            <option value="AB">Alberta</option>
            <option value="MB">Manitoba</option>
            <option value="SK">Saskatchewan</option>
            <option value="NS">Nova Scotia</option>
            <option value="NB">New Brunswick</option>
            <option value="NL">Newfoundland and Labrador</option>
            <option value="PE">Prince Edward Island</option>
            <option value="NT">Northwest Territories</option>
            <option value="NU">Nunavut</option>
            <option value="YT">Yukon</option>
          </select>
        ) : (
          <input className="input" value={shippingRegion} onChange={(e) => setShippingRegion(e.target.value)} required />
        )}

        <label className="label">Postal/ZIP Code</label>
        <input className="input" value={shippingPostal} onChange={(e) => setShippingPostal(e.target.value)} required />

        <button className="button" type="submit" disabled={loading}>{loading ? "Submitting..." : "Place Order"}</button>
      </form>
      <div className="notice">
        <div className="row space-between"><span>Subtotal</span><strong>${(subtotal / 100).toFixed(2)}</strong></div>
        <div className="row space-between"><span>Shipping (est.)</span><strong>${(shippingCents / 100).toFixed(2)}</strong></div>
        {shippingZone && (
          <div className="row space-between"><span>Zone</span><strong>{shippingZone}</strong></div>
        )}
        <div className="row space-between"><span>Total</span><strong>${(total / 100).toFixed(2)}</strong></div>
      </div>
      {error && <p className="error">{error.message}</p>}
      {data?.checkout?.order && (
        <div className="notice">
          Order #{data.checkout.order.id} is {data.checkout.order.status}. We will confirm your Interac e-Transfer shortly.
        </div>
      )}
    </div>
  );
}
