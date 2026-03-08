import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { MockedProvider } from '@apollo/client/testing';
import Navbar from '../components/Navbar';
import { AuthProvider } from '../state/AuthContext';

// Helper to render with providers
const renderNavbar = (mocks = []) => {
  return render(
    <MockedProvider mocks={mocks}>
      <AuthProvider>
        <BrowserRouter future={{ v7_startTransition: true }}>
          <Navbar />
        </BrowserRouter>
      </AuthProvider>
    </MockedProvider>
  );
};

describe('Navbar Component', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  test('renders basic navigation links', () => {
    renderNavbar();

    expect(screen.getByText('🍁')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /maple syrup/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /shop/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /cart/i })).toBeInTheDocument();
  });

  test('shows login and register links when not logged in', () => {
    renderNavbar();

    expect(screen.getByRole('link', { name: /login/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /register/i })).toBeInTheDocument();
    expect(screen.queryByRole('link', { name: /orders/i })).not.toBeInTheDocument();
  });

  test('navigation links have correct href attributes', () => {
    renderNavbar();

    expect(screen.getByRole('link', { name: /maple syrup/i })).toHaveAttribute('href', '/');
    expect(screen.getByRole('link', { name: /shop/i })).toHaveAttribute('href', '/');
    expect(screen.getByRole('link', { name: /cart/i })).toHaveAttribute('href', '/cart');
    expect(screen.getByRole('link', { name: /login/i })).toHaveAttribute('href', '/login');
    expect(screen.getByRole('link', { name: /register/i })).toHaveAttribute('href', '/register');
  });
});
