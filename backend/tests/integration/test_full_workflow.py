"""
Integration Tests for Complete Property Analysis Workflow

Tests the full pipeline:
1. Floor plan upload
2. Measurement extraction (Agent #1 + enhanced measurements)
3. Market insights generation (Agent #2 + ATTOM API)
4. Statistical pricing model
5. Database storage

These tests require:
- Supabase connection
- ATTOM API key
- Google Gemini API key
- Test floor plan images
"""

import pytest
import os
import asyncio
from pathlib import Path
from typing import Dict, Any
import json

# Services
from app.services.floor_plan_measurements import FloorPlanMeasurementEstimator
from app.services.pricing_model import PropertyPricingModel, PropertyFeatures, ComparableProperty
from app.clients.attom_client import AttomAPIClient
from app.agents.market_insights_analyst import MarketInsightsAnalyst

# Skip if integration test flag not set
pytestmark = pytest.mark.skipif(
    not os.getenv('RUN_INTEGRATION_TESTS'),
    reason="Integration tests disabled. Set RUN_INTEGRATION_TESTS=1 to run"
)


class TestFullPropertyAnalysisWorkflow:
    """Integration tests for complete property analysis workflow"""
    
    @pytest.fixture
    def test_property_data(self):
        """Sample property data for testing"""
        return {
            'address': '4529 Winona Ct',
            'city': 'Denver',
            'state': 'CO',
            'zip_code': '80212',
            'bedrooms': 2,
            'bathrooms': 1.0,
            'square_footage': 934,
            'property_type': 'Single Family Residence',
            'year_built': 1900
        }
    
    @pytest.fixture
    def test_floor_plan_path(self):
        """Path to test floor plan image"""
        # In a real test, you'd have a test image
        test_dir = Path(__file__).parent.parent.parent / 'tests' / 'fixtures'
        return test_dir / 'sample_floor_plan.png'
    
    def test_1_floor_plan_measurement_extraction(self, test_property_data, test_floor_plan_path):
        """Test: Extract measurements from floor plan"""
        
        # Skip if no test image
        if not test_floor_plan_path.exists():
            pytest.skip("Test floor plan image not found")
        
        estimator = FloorPlanMeasurementEstimator()
        
        # Extract measurements
        measurements = estimator.estimate_measurements(
            image_path=str(test_floor_plan_path),
            property_type=test_property_data['property_type'],
            known_total_sqft=test_property_data['square_footage']
        )
        
        # Assertions
        assert measurements is not None
        assert measurements.total_square_feet > 0
        assert 0 <= measurements.total_square_feet_confidence <= 1.0
        assert len(measurements.rooms) > 0
        assert measurements.quality.overall_score > 0
        assert measurements.processing_time_seconds > 0
        
        # Verify room structure
        for room in measurements.rooms:
            assert room.type in ['bedroom', 'living_room', 'kitchen', 'bathroom', 'dining_room', 'unknown']
            assert room.name
            assert 0 <= room.confidence <= 1.0
        
        # Convert to database format
        db_data = estimator.to_database_format(measurements)
        assert 'total_square_feet' in db_data
        assert 'rooms' in db_data
        assert 'quality_score' in db_data
        
        print(f"\n✅ Floor plan measurements extracted:")
        print(f"   Total: {measurements.total_square_feet} sqft")
        print(f"   Rooms: {len(measurements.rooms)}")
        print(f"   Quality: {measurements.quality.overall_score}/100")
    
    def test_2_attom_api_property_search(self, test_property_data):
        """Test: Search for property in ATTOM API"""
        
        client = AttomAPIClient()
        
        # Search property
        result = client.search_property_data(
            address=test_property_data['address'],
            city=test_property_data['city'],
            state=test_property_data['state'],
            zip_code=test_property_data['zip_code']
        )
        
        # Assertions
        assert result is not None
        assert 'attomId' in result or 'property' in result
        
        # Verify key fields
        if 'address' in result:
            assert test_property_data['city'].upper() in result['address'].get('locality', '').upper()
        
        print(f"\n✅ ATTOM API property found:")
        print(f"   Address: {result.get('address', {}).get('line1', 'N/A')}")
        print(f"   ATTOM ID: {result.get('attomId', 'N/A')}")
    
    def test_3_attom_api_avm_estimate(self, test_property_data):
        """Test: Get AVM (valuation) from ATTOM API"""
        
        client = AttomAPIClient()
        
        # Get AVM
        result = client.get_avm_estimate(
            address=test_property_data['address'],
            city=test_property_data['city'],
            state=test_property_data['state'],
            zip_code=test_property_data['zip_code']
        )
        
        # Assertions
        assert result is not None
        
        # AVM may not always be available, but response should be valid
        if 'avm' in result:
            assert 'amount' in result['avm'] or 'value' in result['avm']
        
        print(f"\n✅ ATTOM AVM retrieved")
    
    def test_4_statistical_pricing_model(self, test_property_data):
        """Test: Generate price estimate using statistical model"""
        
        # Create subject property
        subject = PropertyFeatures(
            bedrooms=test_property_data['bedrooms'],
            bathrooms=test_property_data['bathrooms'],
            square_feet=test_property_data['square_footage'],
            lot_size_sqft=4000,
            year_built=test_property_data['year_built'],
            property_type=test_property_data['property_type'],
            location_quality=0.75,
            condition_score=0.70
        )
        
        # Create mock comparables
        comparables = [
            ComparableProperty(
                address='4525 Winona Ct',
                sale_price=455000,
                sale_date='2024-09-15',
                bedrooms=2,
                bathrooms=1.0,
                square_feet=950,
                lot_size_sqft=4200,
                year_built=1905,
                property_type='Single Family',
                distance_miles=0.1,
                days_since_sale=30
            ),
            ComparableProperty(
                address='4533 Winona Ct',
                sale_price=440000,
                sale_date='2024-08-01',
                bedrooms=2,
                bathrooms=1.0,
                square_feet=920,
                lot_size_sqft=3800,
                year_built=1898,
                property_type='Single Family',
                distance_miles=0.15,
                days_since_sale=75
            ),
            ComparableProperty(
                address='1234 Main St',
                sale_price=475000,
                sale_date='2024-10-01',
                bedrooms=3,
                bathrooms=2.0,
                square_feet=1100,
                lot_size_sqft=4500,
                year_built=1910,
                property_type='Single Family',
                distance_miles=0.3,
                days_since_sale=15
            )
        ]
        
        # Generate estimate
        model = PropertyPricingModel()
        estimate = model.estimate_price(subject, comparables)
        
        # Assertions
        assert estimate is not None
        assert estimate.estimated_value > 0
        assert estimate.value_range_low < estimate.estimated_value
        assert estimate.value_range_high > estimate.estimated_value
        assert estimate.confidence_level in ['High', 'Medium', 'Low']
        assert 0 <= estimate.confidence_score <= 1.0
        assert estimate.price_per_sqft > 0
        assert estimate.comparables_used == len(comparables)
        assert len(estimate.reasoning) > 0
        
        print(f"\n✅ Statistical price estimate:")
        print(f"   Estimated: ${estimate.estimated_value:,}")
        print(f"   Range: ${estimate.value_range_low:,} - ${estimate.value_range_high:,}")
        print(f"   Confidence: {estimate.confidence_level} ({estimate.confidence_score:.2%})")
        print(f"   Price/sqft: ${estimate.price_per_sqft:.2f}")
    
    def test_5_agent_2_full_analysis(self, test_property_data):
        """Test: Complete market insights analysis with Agent #2"""
        
        analyst = MarketInsightsAnalyst()
        
        # Run analysis
        result = analyst.analyze_property(
            address=f"{test_property_data['address']}, {test_property_data['city']}, {test_property_data['state']} {test_property_data['zip_code']}",
            property_data=test_property_data
        )
        
        # Assertions
        assert result is not None
        assert 'price_estimate' in result
        assert 'market_trend' in result
        assert 'investment_analysis' in result
        
        # Verify price estimate structure
        price_est = result['price_estimate']
        assert 'estimated_value' in price_est
        assert 'confidence' in price_est
        assert price_est['estimated_value'] > 0
        
        # Verify investment analysis
        investment = result['investment_analysis']
        assert 'investment_score' in investment
        assert 0 <= investment['investment_score'] <= 100
        
        print(f"\n✅ Agent #2 analysis complete:")
        print(f"   Price: ${price_est['estimated_value']:,}")
        print(f"   Investment Score: {investment['investment_score']}/100")
        print(f"   Rental Income: ${investment.get('estimated_rental_income', 0):,}/mo")
    
    def test_6_end_to_end_workflow(self, test_property_data):
        """Test: Complete end-to-end workflow"""
        
        print("\n" + "="*70)
        print("END-TO-END WORKFLOW TEST")
        print("="*70)
        
        # Step 1: ATTOM API - Get property data
        print("\n[1/4] Fetching property data from ATTOM API...")
        attom_client = AttomAPIClient()
        attom_data = attom_client.search_property_data(
            address=test_property_data['address'],
            city=test_property_data['city'],
            state=test_property_data['state'],
            zip_code=test_property_data['zip_code']
        )
        assert attom_data is not None
        print("✅ Property data retrieved")
        
        # Step 2: Get comparables
        print("\n[2/4] Finding comparable properties...")
        comparables = attom_client.get_comparable_properties(
            address=test_property_data['address'],
            city=test_property_data['city'],
            state=test_property_data['state']
        )
        print(f"✅ Found {len(comparables) if comparables else 0} comparables")
        
        # Step 3: Statistical pricing
        print("\n[3/4] Running statistical pricing model...")
        if comparables and len(comparables) >= 2:
            subject = PropertyFeatures(
                bedrooms=test_property_data['bedrooms'],
                bathrooms=test_property_data['bathrooms'],
                square_feet=test_property_data['square_footage'],
                lot_size_sqft=4000,
                year_built=test_property_data['year_built'],
                property_type=test_property_data['property_type'],
                location_quality=0.75,
                condition_score=0.70
            )
            
            # Convert comparables to objects
            comp_objects = []
            for comp in comparables[:5]:  # Use top 5
                comp_objects.append(ComparableProperty(
                    address=comp.get('address', 'Unknown'),
                    sale_price=comp.get('sale_price', 450000),
                    sale_date=comp.get('sale_date', '2024-01-01'),
                    bedrooms=comp.get('bedrooms', 2),
                    bathrooms=comp.get('bathrooms', 1.0),
                    square_feet=comp.get('square_feet', 900),
                    lot_size_sqft=comp.get('lot_size_sqft', 4000),
                    year_built=comp.get('year_built', 1900),
                    property_type=comp.get('property_type', 'Single Family'),
                    distance_miles=comp.get('distance_miles', 0.5),
                    days_since_sale=90
                ))
            
            model = PropertyPricingModel()
            price_estimate = model.estimate_price(subject, comp_objects)
            print(f"✅ Price estimate: ${price_estimate.estimated_value:,}")
        else:
            print("⚠️ Not enough comparables for statistical model")
        
        # Step 4: Agent #2 analysis
        print("\n[4/4] Running AI market insights analysis...")
        analyst = MarketInsightsAnalyst()
        insights = analyst.analyze_property(
            address=f"{test_property_data['address']}, {test_property_data['city']}, {test_property_data['state']} {test_property_data['zip_code']}",
            property_data=test_property_data
        )
        assert insights is not None
        print("✅ Market insights generated")
        
        # Final summary
        print("\n" + "="*70)
        print("WORKFLOW COMPLETE")
        print("="*70)
        print(f"Property: {test_property_data['address']}, {test_property_data['city']}, {test_property_data['state']}")
        print(f"Price Estimate: ${insights['price_estimate']['estimated_value']:,}")
        print(f"Investment Score: {insights['investment_analysis']['investment_score']}/100")
        print(f"Status: ✅ ALL SYSTEMS OPERATIONAL")
        print("="*70)


class TestDatabaseIntegration:
    """Test database operations with Supabase"""
    
    @pytest.mark.skipif(
        not os.getenv('SUPABASE_URL'),
        reason="Supabase not configured"
    )
    def test_store_floor_plan_measurements(self):
        """Test: Store floor plan measurements in database"""
        # This would require Supabase client
        # Implementation depends on your database access layer
        pytest.skip("Supabase integration test - implement when DB layer ready")
    
    @pytest.mark.skipif(
        not os.getenv('SUPABASE_URL'),
        reason="Supabase not configured"
    )
    def test_store_market_insights(self):
        """Test: Store market insights in database"""
        pytest.skip("Supabase integration test - implement when DB layer ready")
    
    @pytest.mark.skipif(
        not os.getenv('SUPABASE_URL'),
        reason="Supabase not configured"
    )
    def test_cache_attom_data(self):
        """Test: Cache ATTOM API response in database"""
        pytest.skip("Supabase integration test - implement when DB layer ready")


# Performance tests
class TestPerformance:
    """Performance benchmarks for the workflow"""
    
    def test_agent_2_response_time(self, test_property_data):
        """Test: Agent #2 completes analysis within acceptable time"""
        import time
        
        analyst = MarketInsightsAnalyst()
        
        start = time.time()
        result = analyst.analyze_property(
            address=f"{test_property_data['address']}, {test_property_data['city']}, {test_property_data['state']}",
            property_data=test_property_data
        )
        elapsed = time.time() - start
        
        # Should complete within 90 seconds
        assert elapsed < 90, f"Analysis took {elapsed:.1f}s (limit: 90s)"
        print(f"\n✅ Agent #2 completed in {elapsed:.1f}s")
    
    def test_attom_api_response_time(self, test_property_data):
        """Test: ATTOM API responds within acceptable time"""
        import time
        
        client = AttomAPIClient()
        
        start = time.time()
        result = client.search_property_data(
            address=test_property_data['address'],
            city=test_property_data['city'],
            state=test_property_data['state']
        )
        elapsed = time.time() - start
        
        # Should complete within 5 seconds
        assert elapsed < 5, f"API call took {elapsed:.1f}s (limit: 5s)"
        print(f"\n✅ ATTOM API responded in {elapsed:.1f}s")


if __name__ == '__main__':
    # Run tests
    pytest.main([__file__, '-v', '-s'])
