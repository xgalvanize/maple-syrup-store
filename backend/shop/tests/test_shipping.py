"""
Unit tests for shipping logic
"""
import pytest
from shop.shipping import estimate_shipping, calculate_shipping_cents


@pytest.mark.unit
class TestEstimateShipping:
    """Test shipping estimation with (country, region, postal)"""

    def test_local_radius_shipping(self):
        """Test shipping for local radius (P0R postal code)"""
        cents, zone = estimate_shipping("Canada", "Ontario", "P0R 1B0")
        assert cents == 499
        assert zone == "LOCAL_RADIUS"

    def test_local_radius_lowercase(self):
        """Test local radius with lowercase postal code"""
        cents, zone = estimate_shipping("Canada", "Ontario", "p0r 2a1")
        assert cents == 499
        assert zone == "LOCAL_RADIUS"

    def test_local_radius_with_space(self):
        """Test local radius with space in postal code"""
        cents, zone = estimate_shipping("Canada", "Ontario", "P0R 1C2")
        assert cents == 499
        assert zone == "LOCAL_RADIUS"

    def test_ontario_shipping(self):
        """Test shipping within Ontario (non-local)"""
        cents, zone = estimate_shipping("Canada", "Ontario", "M5H 2N2")
        assert cents == 799
        assert zone == "ONTARIO"

    def test_ontario_different_postal_codes(self):
        """Test various Ontario postal codes"""
        ontario_codes = ["M5H 2N2", "K1A 0B1", "L5B 4M6", "N2L 3G1"]
        for postal in ontario_codes:
            cents, zone = estimate_shipping("Canada", "Ontario", postal)
            assert cents == 799
            assert zone == "ONTARIO"

    def test_canada_shipping_quebec(self):
        """Test shipping to Quebec"""
        cents, zone = estimate_shipping("Canada", "Quebec", "H2X 3A2")
        assert cents == 1299
        assert zone == "CANADA"

    def test_canada_shipping_bc(self):
        """Test shipping to British Columbia"""
        cents, zone = estimate_shipping("Canada", "British Columbia", "V6B 2W9")
        assert cents == 1299
        assert zone == "CANADA"

    def test_canada_shipping_all_provinces(self):
        """Test shipping to various Canadian provinces"""
        provinces = [
            ("Quebec", "H3A 1A1"),
            ("British Columbia", "V5K 0A1"),
            ("Alberta", "T2P 2M5"),
            ("Manitoba", "R3C 0V8"),
            ("Saskatchewan", "S7K 0J5"),
            ("Nova Scotia", "B3H 4R2"),
            ("New Brunswick", "E1C 4Z6"),
            ("Newfoundland and Labrador", "A1C 5T7"),
            ("Prince Edward Island", "C1A 7N8"),
        ]
        
        for region, postal in provinces:
            cents, zone = estimate_shipping("Canada", region, postal)
            assert cents == 1299, f"Failed for {region}"
            assert zone == "CANADA", f"Failed for {region}"

    def test_international_shipping_usa(self):
        """Test international shipping to USA"""
        cents, zone = estimate_shipping("USA", "California", "90210")
        assert cents == 2999
        assert zone == "INTERNATIONAL"

    def test_international_shipping_uk(self):
        """Test international shipping to UK"""
        cents, zone = estimate_shipping("United Kingdom", "England", "SW1A 1AA")
        assert cents == 2999
        assert zone == "INTERNATIONAL"

    def test_international_various_countries(self):
        """Test international shipping to various countries"""
        countries = [
            ("United States", "New York", "10001"),
            ("United Kingdom", "London", "SW1A 1AA"),
            ("France", "Paris", "75001"),
            ("Germany", "Berlin", "10115"),
            ("Australia", "Sydney", "2000"),
            ("Japan", "Tokyo", "100-0001"),
        ]
        
        for country, region, postal in countries:
            cents, zone = estimate_shipping(country, region, postal)
            assert cents == 2999, f"Failed for {country}"
            assert zone == "INTERNATIONAL", f"Failed for {country}"

    def test_empty_postal_code(self):
        """Test with empty postal code"""
        cents, zone = estimate_shipping("Canada", "Ontario", "")
        assert cents == 799
        assert zone == "ONTARIO"

    def test_malformed_postal_code(self):
        """Test with malformed postal code"""
        cents, zone = estimate_shipping("Canada", "Ontario", "INVALID")
        assert cents == 799
        assert zone == "ONTARIO"

    def test_case_insensitive_country(self):
        """Test case insensitivity for country name"""
        cents1, zone1 = estimate_shipping("canada", "Ontario", "M5H 2N2")
        cents2, zone2 = estimate_shipping("CANADA", "Ontario", "M5H 2N2")
        cents3, zone3 = estimate_shipping("Canada", "Ontario", "M5H 2N2")
        
        assert cents1 == cents2 == cents3 == 799
        assert zone1 == zone2 == zone3 == "ONTARIO"

    def test_case_insensitive_region(self):
        """Test case insensitivity for region name"""
        cents1, zone1 = estimate_shipping("Canada", "ontario", "M5H 2N2")
        cents2, zone2 = estimate_shipping("Canada", "ONTARIO", "M5H 2N2")
        
        assert cents1 == cents2 == 799
        assert zone1 == zone2 == "ONTARIO"


@pytest.mark.unit
class TestCalculateShippingCents:
    """Test the calculate_shipping_cents convenience function"""

    def test_local_radius_zone(self):
        """Test LOCAL_RADIUS zone calculation"""
        cents = calculate_shipping_cents("Canada", "Ontario", "P0R 1B0")
        assert cents == 499

    def test_ontario_zone(self):
        """Test ONTARIO zone calculation"""
        cents = calculate_shipping_cents("Canada", "Ontario", "M5H 2N2")
        assert cents == 799

    def test_canada_zone(self):
        """Test CANADA zone calculation"""
        cents = calculate_shipping_cents("Canada", "Quebec", "H2X 3A2")
        assert cents == 1299

    def test_international_zone(self):
        """Test INTERNATIONAL zone calculation"""
        cents = calculate_shipping_cents("USA", "California", "90210")
        assert cents == 2999

