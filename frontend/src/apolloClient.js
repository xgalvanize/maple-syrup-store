import { ApolloClient, InMemoryCache, HttpLink } from "@apollo/client";
import { setContext } from "@apollo/client/link/context";
import { onError } from "@apollo/client/link/error";

let notificationContext = null;
let authContext = null;

// Global setters to inject context without circular imports
export function setNotificationContext(showNotification) {
  notificationContext = { showNotification };
}

export function setAuthContext(ctx) {
  authContext = ctx;
}

function handleAuthFailure() {
  if (authContext) {
    authContext.logout();
  } else {
    localStorage.removeItem("token");
  }

  if (notificationContext) {
    notificationContext.showNotification(
      "Your session is invalid or expired. Please log in again.",
      "error",
      5000
    );
  }

  if (window.location.pathname !== "/login") {
    window.location.href = "/login";
  }
}

const httpLink = new HttpLink({
  uri: process.env.REACT_APP_GRAPHQL_URL || "/graphql/",
});

const authLink = setContext((_, { headers }) => {
  const token = localStorage.getItem("token");
  return {
    headers: {
      ...headers,
      Authorization: token ? `JWT ${token}` : "",
    },
  };
});

const errorLink = onError(({ graphQLErrors, networkError }) => {
  if (graphQLErrors) {
    graphQLErrors.forEach(({ message, extensions }) => {
      const status = extensions?.status || extensions?.exception?.status;

      const isAuthError =
        status === 401 ||
        message?.includes("Signature has expired") ||
        message?.includes("Error decoding signature") ||
        message?.toLowerCase().includes("invalid token");

      if (isAuthError) {
        handleAuthFailure();
      }

      // Handle 403 Forbidden
      if (status === 403) {
        if (notificationContext) {
          notificationContext.showNotification(
            "You don't have permission to access this.",
            "error",
            5000
          );
        }
      }
    });
  }

  if (networkError) {
    if (networkError.status === 401) {
      handleAuthFailure();
    }
  }
});

export const client = new ApolloClient({
  link: errorLink.concat(authLink).concat(httpLink),
  cache: new InMemoryCache(),
});
