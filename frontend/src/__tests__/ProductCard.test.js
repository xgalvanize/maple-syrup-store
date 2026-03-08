import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import userEvent from '@testing-library/user-event';
import ProductCard from '../components/ProductCard';

describe('ProductCard Component', () => {
  const mockProduct = {
    id: '1',
    name: 'Light Maple Syrup',
    description: 'Delicious light amber syrup',
    priceCents: 1999,
    imageUrl: 'https://example.com/light.jpg',
  };

  const mockOnAdd = jest.fn();

  beforeEach(() => {
    mockOnAdd.mockClear();
  });

  test('renders product information correctly', () => {
    render(<ProductCard product={mockProduct} onAdd={mockOnAdd} />);
    
    expect(screen.getByText('Light Maple Syrup')).toBeInTheDocument();
    expect(screen.getByText('Delicious light amber syrup')).toBeInTheDocument();
    expect(screen.getByText('$19.99')).toBeInTheDocument();
  });

  test('displays product image when imageUrl is provided', () => {
    render(<ProductCard product={mockProduct} onAdd={mockOnAdd} />);
    
    const image = screen.getByAltText('Light Maple Syrup');
    expect(image).toBeInTheDocument();
    expect(image).toHaveAttribute('src', 'https://example.com/light.jpg');
  });

  test('does not display image when imageUrl is empty', () => {
    const productNoImage = { ...mockProduct, imageUrl: '' };
    render(<ProductCard product={productNoImage} onAdd={mockOnAdd} />);
    
    expect(screen.queryByAltText('Light Maple Syrup')).not.toBeInTheDocument();
  });

  test('calls onAdd with product id when Add to Cart button is clicked', async () => {
    const user = userEvent.setup();
    render(<ProductCard product={mockProduct} onAdd={mockOnAdd} />);
    
    const addButton = screen.getByRole('button', { name: /add to cart/i });
    await user.click(addButton);
    
    expect(mockOnAdd).toHaveBeenCalledTimes(1);
    expect(mockOnAdd).toHaveBeenCalledWith('1');
  });

  test('formats price correctly for different amounts', () => {
    const products = [
      { ...mockProduct, priceCents: 500 },
      { ...mockProduct, priceCents: 2999 },
      { ...mockProduct, priceCents: 10000 },
    ];
    const expectedPrices = ['$5.00', '$29.99', '$100.00'];

    const { rerender } = render(<ProductCard product={products[0]} onAdd={mockOnAdd} />);

    expectedPrices.forEach((expectedPrice, index) => {
      if (index > 0) {
        rerender(<ProductCard product={products[index]} onAdd={mockOnAdd} />);
      }
      expect(screen.getByText(expectedPrice)).toBeInTheDocument();
    });
  });

  test('has accessible title attributes', () => {
    const { container } = render(<ProductCard product={mockProduct} onAdd={mockOnAdd} />);
    
    const cardDiv = container.querySelector('.card');
    expect(cardDiv).toHaveAttribute('title');
    
    const addButton = screen.getByRole('button', { name: /add to cart/i });
    expect(addButton).toHaveAttribute('title');
  });
});
