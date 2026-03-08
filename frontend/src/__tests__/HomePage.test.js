import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { BrowserRouter } from 'react-router-dom';
import { MockedProvider } from '@apollo/client/testing';
import HomePage, { GET_PRODUCTS } from '../pages/HomePage';
import { AuthProvider } from '../state/AuthContext';
import { NotificationProvider } from '../state/NotificationContext';

const mockProducts = [
  {
    id: '1',
    name: 'Light Maple Syrup',
    description: 'Light amber syrup',
    priceCents: 1999,
    imageUrl: 'https://example.com/light.jpg',
    isActive: true,
  },
  {
    id: '2',
    name: 'Dark Maple Syrup',
    description: 'Rich dark syrup',
    priceCents: 2199,
    imageUrl: 'https://example.com/dark.jpg',
    isActive: true,
  },
];

const renderHomePage = (mocks) => {
  return render(
    <MockedProvider mocks={mocks}>
      <AuthProvider>
        <NotificationProvider>
          <BrowserRouter future={{ v7_startTransition: true }}>
            <HomePage />
          </BrowserRouter>
        </NotificationProvider>
      </AuthProvider>
    </MockedProvider>
  );
};

describe('HomePage Component', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  test('displays loading state initially', () => {
    const mocks = [];
    renderHomePage(mocks);
    
    // Component shows loading text while fetching
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  test('renders when products load', async () => {
    const mocks = [
      {
        request: {
          query: GET_PRODUCTS,
        },
        result: {
          data: {
            products: mockProducts,
          },
        },
      },
    ];

    renderHomePage(mocks);

    // Verify loading disappears
    await waitFor(() => {
      expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
    }, { timeout: 3000 });

    // Verify products are actually rendered
    expect(screen.getByText('Light Maple Syrup')).toBeInTheDocument();
    expect(screen.getByText('Dark Maple Syrup')).toBeInTheDocument();
    expect(screen.getByText('$19.99')).toBeInTheDocument();
    expect(screen.getByText('$21.99')).toBeInTheDocument();
  });

  test('handles network errors gracefully', async () => {
    const mocks = [
      {
        request: {
          query: GET_PRODUCTS,
        },
        error: new Error('Network error'),
      },
    ];

    renderHomePage(mocks);

    await waitFor(() => {
      // Should show error state
      expect(screen.getByText(/couldn’t load products/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument();
    }, { timeout: 3000 });
  });
});
