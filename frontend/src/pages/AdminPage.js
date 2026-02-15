import React, { useMemo, useState } from "react";
import { useMutation, useQuery, gql } from "@apollo/client";

const ME = gql`
  query Me {
    me {
      id
      username
      isStaff
    }
  }
`;

const ADMIN_PRODUCTS = gql`
  query AdminProducts {
    adminProducts {
      id
      name
      description
      priceCents
      imageUrl
      inventory
      isActive
    }
  }
`;

const ADMIN_ORDERS = gql`
  query AdminOrders {
    adminOrders {
      id
      status
      totalCents
      paymentReference
      payerEmail
      shippingAddress1
      shippingAddress2
      shippingCity
      shippingRegion
      shippingCountry
      shippingPostal
      createdAt
      user { id username email }
      items { id quantity priceCents product { name } }
    }
  }
`;

const CREATE_PRODUCT = gql`
  mutation CreateProduct(
    $name: String!
    $description: String
    $priceCents: Int!
    $imageUrl: String
    $inventory: Int
    $isActive: Boolean
  ) {
    createProduct(
      name: $name
      description: $description
      priceCents: $priceCents
      imageUrl: $imageUrl
      inventory: $inventory
      isActive: $isActive
    ) {
      product { id name }
    }
  }
`;

const UPDATE_PRODUCT = gql`
  mutation UpdateProduct(
    $productId: ID!
    $name: String
    $description: String
    $priceCents: Int
    $imageUrl: String
    $inventory: Int
    $isActive: Boolean
  ) {
    updateProduct(
      productId: $productId
      name: $name
      description: $description
      priceCents: $priceCents
      imageUrl: $imageUrl
      inventory: $inventory
      isActive: $isActive
    ) {
      product { id name }
    }
  }
`;

const DELETE_PRODUCT = gql`
  mutation DeleteProduct($productId: ID!) {
    deleteProduct(productId: $productId) { ok }
  }
`;

const UPDATE_ORDER_STATUS = gql`
  mutation UpdateOrderStatus($orderId: ID!, $status: String!) {
    updateOrderStatus(orderId: $orderId, status: $status) {
      order { id status }
    }
  }
`;

const MARK_ORDER_PAID = gql`
  mutation MarkOrderPaid($orderId: ID!) {
    markOrderPaid(orderId: $orderId) { order { id status } }
  }
`;

const ORDER_STATUSES = [
  "PENDING_PAYMENT",
  "PAID",
  "SHIPPED",
  "DELIVERED",
  "CANCELLED",
];

export default function AdminPage() {
  const { data: meData, loading: meLoading } = useQuery(ME);
  const { data: productData, loading: productLoading, error: productError } = useQuery(ADMIN_PRODUCTS);
  const { data: orderData, loading: orderLoading, error: orderError } = useQuery(ADMIN_ORDERS);

  const [createProduct] = useMutation(CREATE_PRODUCT, { refetchQueries: ["AdminProducts"] });
  const [updateProduct] = useMutation(UPDATE_PRODUCT, { refetchQueries: ["AdminProducts"] });
  const [deleteProduct] = useMutation(DELETE_PRODUCT, { refetchQueries: ["AdminProducts"] });
  const [updateOrderStatus] = useMutation(UPDATE_ORDER_STATUS, { refetchQueries: ["AdminOrders"] });
  const [markOrderPaid] = useMutation(MARK_ORDER_PAID, { refetchQueries: ["AdminOrders"] });

  const [newProduct, setNewProduct] = useState({
    name: "",
    description: "",
    priceCents: "",
    imageUrl: "",
    inventory: "",
    isActive: true,
  });

  const [productEdits, setProductEdits] = useState({});

  const isStaff = meData?.me?.isStaff;

  const productList = useMemo(() => productData?.adminProducts || [], [productData]);
  const orderList = useMemo(() => orderData?.adminOrders || [], [orderData]);

  if (meLoading || productLoading || orderLoading) return <p>Loading admin dashboard...</p>;
  if (!isStaff) return <p>You do not have access to the admin dashboard.</p>;
  if (productError) return <p>Error: {productError.message}</p>;
  if (orderError) return <p>Error: {orderError.message}</p>;

  async function handleCreateProduct(e) {
    e.preventDefault();
    await createProduct({
      variables: {
        name: newProduct.name,
        description: newProduct.description,
        priceCents: Number(newProduct.priceCents || 0),
        imageUrl: newProduct.imageUrl,
        inventory: Number(newProduct.inventory || 0),
        isActive: Boolean(newProduct.isActive),
      },
    });
    setNewProduct({ name: "", description: "", priceCents: "", imageUrl: "", inventory: "", isActive: true });
  }

  function setProductField(productId, field, value) {
    setProductEdits((prev) => ({
      ...prev,
      [productId]: {
        ...prev[productId],
        [field]: value,
      },
    }));
  }

  async function handleUpdateProduct(product) {
    const edits = productEdits[product.id] || {};
    const variables = {
      productId: product.id,
      name: edits.name ?? product.name,
      description: edits.description ?? product.description,
      priceCents: Number(edits.priceCents ?? product.priceCents),
      imageUrl: edits.imageUrl ?? product.imageUrl,
      inventory: Number(edits.inventory ?? product.inventory),
      isActive: edits.isActive ?? product.isActive,
    };
    await updateProduct({ variables });
  }

  async function handleDeleteProduct(productId) {
    if (!window.confirm("Delete this product?")) return;
    await deleteProduct({ variables: { productId } });
  }

  async function handleMarkPaid(orderId) {
    await markOrderPaid({ variables: { orderId } });
  }

  async function handleStatusChange(orderId, status) {
    await updateOrderStatus({ variables: { orderId, status } });
  }

  return (
    <div>
      <div className="row space-between">
        <h2>Admin Dashboard</h2>
        <span className="badge">Staff</span>
      </div>

      <section className="admin-section">
        <h3>Payment Reconciliation & Orders</h3>
        {orderList.length === 0 ? (
          <p>No orders yet.</p>
        ) : (
          <div className="admin-grid">
            {orderList.map((order) => (
              <div key={order.id} className="card admin-card">
                <div className="row space-between">
                  <strong>Order #{order.id}</strong>
                  <span className="badge">{order.status}</span>
                </div>

                <div className="muted">{order.user?.username} • {order.user?.email}</div>
                <div className="muted">{order.payerEmail} • Ref: {order.paymentReference}</div>

                <div className="admin-address">
                  <strong>Ship To:</strong> {[
                    order.shippingAddress1,
                    order.shippingAddress2,
                    order.shippingCity,
                    order.shippingRegion,
                    order.shippingCountry,
                    order.shippingPostal,
                  ].filter(Boolean).join(", ")}
                </div>

                <ul className="list">
                  {order.items.map((item) => (
                    <li key={item.id} className="list-row">
                      <span>{item.product?.name}</span>
                      <span>Qty {item.quantity}</span>
                    </li>
                  ))}
                </ul>

                <div className="row space-between">
                  <span>Total</span>
                  <strong>${(order.totalCents / 100).toFixed(2)}</strong>
                </div>

                <div className="row admin-actions">
                  {order.status === "PENDING_PAYMENT" && (
                    <button className="button" type="button" onClick={() => handleMarkPaid(order.id)}>
                      Mark Paid
                    </button>
                  )}
                  <select
                    className="input"
                    value={order.status}
                    onChange={(e) => handleStatusChange(order.id, e.target.value)}
                  >
                    {ORDER_STATUSES.map((status) => (
                      <option key={status} value={status}>{status}</option>
                    ))}
                  </select>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      <section className="admin-section">
        <h3>Product Management</h3>
        <form className="admin-form card" onSubmit={handleCreateProduct}>
          <div className="row">
            <input
              className="input"
              placeholder="Name"
              value={newProduct.name}
              onChange={(e) => setNewProduct((p) => ({ ...p, name: e.target.value }))}
              required
            />
            <input
              className="input"
              placeholder="Price (cents)"
              type="number"
              value={newProduct.priceCents}
              onChange={(e) => setNewProduct((p) => ({ ...p, priceCents: e.target.value }))}
              required
            />
            <input
              className="input"
              placeholder="Inventory"
              type="number"
              value={newProduct.inventory}
              onChange={(e) => setNewProduct((p) => ({ ...p, inventory: e.target.value }))}
            />
          </div>
          <input
            className="input"
            placeholder="Image URL"
            value={newProduct.imageUrl}
            onChange={(e) => setNewProduct((p) => ({ ...p, imageUrl: e.target.value }))}
          />
          <textarea
            className="input"
            placeholder="Description"
            value={newProduct.description}
            onChange={(e) => setNewProduct((p) => ({ ...p, description: e.target.value }))}
            rows={3}
          />
          <label className="row">
            <input
              type="checkbox"
              checked={newProduct.isActive}
              onChange={(e) => setNewProduct((p) => ({ ...p, isActive: e.target.checked }))}
            />
            Active
          </label>
          <button className="button" type="submit">Create Product</button>
        </form>

        {productList.length === 0 ? (
          <p>No products yet.</p>
        ) : (
          <div className="admin-grid">
            {productList.map((product) => (
              <div key={product.id} className="card admin-card">
                <div className="row space-between">
                  <strong>{product.name}</strong>
                  <span className="badge">{product.isActive ? "Active" : "Hidden"}</span>
                </div>

                <div className="admin-fields">
                  <input
                    className="input"
                    value={productEdits[product.id]?.name ?? product.name}
                    onChange={(e) => setProductField(product.id, "name", e.target.value)}
                  />
                  <input
                    className="input"
                    type="number"
                    value={productEdits[product.id]?.priceCents ?? product.priceCents}
                    onChange={(e) => setProductField(product.id, "priceCents", e.target.value)}
                  />
                  <input
                    className="input"
                    type="number"
                    value={productEdits[product.id]?.inventory ?? product.inventory}
                    onChange={(e) => setProductField(product.id, "inventory", e.target.value)}
                  />
                  <input
                    className="input"
                    value={productEdits[product.id]?.imageUrl ?? product.imageUrl}
                    onChange={(e) => setProductField(product.id, "imageUrl", e.target.value)}
                  />
                  <textarea
                    className="input"
                    rows={3}
                    value={productEdits[product.id]?.description ?? product.description}
                    onChange={(e) => setProductField(product.id, "description", e.target.value)}
                  />
                  <label className="row">
                    <input
                      type="checkbox"
                      checked={productEdits[product.id]?.isActive ?? product.isActive}
                      onChange={(e) => setProductField(product.id, "isActive", e.target.checked)}
                    />
                    Active
                  </label>
                </div>

                <div className="row admin-actions">
                  <button className="button" type="button" onClick={() => handleUpdateProduct(product)}>
                    Save Changes
                  </button>
                  <button className="button-outline" type="button" onClick={() => handleDeleteProduct(product.id)}>
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
