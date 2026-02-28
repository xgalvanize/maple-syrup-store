import React from "react";

export default function ProductCard({ product, onAdd }) {
  return (
    <div className="card" title="Click Add to Cart to purchase this product">
      {product.imageUrl && (
        <img className="product-image" src={product.imageUrl} alt={product.name} title={product.description} />
      )}
      <div className="card-body">
        <h3 title="Product name">{product.name}</h3>
        <p className="muted" title="Product description">{product.description}</p>
        <div className="row">
          <strong title="Price per unit">${(product.priceCents / 100).toFixed(2)}</strong>
          <button className="button" type="button" onClick={() => onAdd(product.id)} title="Add this item to your shopping cart">Add to Cart</button>
        </div>
      </div>
    </div>
  );
}
