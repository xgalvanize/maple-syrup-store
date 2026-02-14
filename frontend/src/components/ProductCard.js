import React from "react";

export default function ProductCard({ product, onAdd }) {
  return (
    <div className="card">
      {product.imageUrl && (
        <img className="product-image" src={product.imageUrl} alt={product.name} />
      )}
      <div className="card-body">
        <h3>{product.name}</h3>
        <p className="muted">{product.description}</p>
        <div className="row">
          <strong>${(product.priceCents / 100).toFixed(2)}</strong>
          <button className="button" type="button" onClick={() => onAdd(product.id)}>Add to Cart</button>
        </div>
      </div>
    </div>
  );
}
