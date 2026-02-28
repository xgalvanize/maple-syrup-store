import React from "react";
import { useNotification } from "../state/NotificationContext";

export default function Notification() {
  const { notification } = useNotification();

  if (!notification) return null;

  return (
    <div className={`notification notification-${notification.type}`}>
      {notification.message}
    </div>
  );
}
