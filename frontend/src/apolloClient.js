import { ApolloClient, InMemoryCache, HttpLink } from "@apollo/client";
import { setContext } from "@apollo/client/link/context";

const BACKEND_BASE_URL = process.env.REACT_APP_BACKEND_URL || "http://localhost:8000";

const httpLink = new HttpLink({
  uri: `${BACKEND_BASE_URL}/graphql/`,
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

export const client = new ApolloClient({
  link: authLink.concat(httpLink),
  cache: new InMemoryCache(),
});
