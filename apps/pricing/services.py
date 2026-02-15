import logging
from typing import Dict

logger = logging.getLogger(__name__)

class PricingEngine:
    """
    Pricing Engine for Smart Airport Pooling.
    Calculates dynamic pricing based on distance, occupancy, and detour impacts.
    """

    def __init__(
        self, 
        base_fare: float = 50.0, 
        rate_per_km: float = 12.0,
        detour_penalty_multiplier: float = 0.8  # Fraction of savings lost per km of detour
    ):
        self.base_fare = base_fare
        self.rate_per_km = rate_per_km
        self.detour_penalty_multiplier = detour_penalty_multiplier

    def calculate_price(
        self, 
        distance_km: float, 
        passenger_count: int, 
        demand_multiplier: float = 1.0,
        detour_km: float = 0.0
    ) -> Dict[str, float]:
        """
        Inputs:
        - distance_km: Direct distance for this specific rider.
        - passenger_count: Total passengers currently in the pool.
        - demand_multiplier: Surge factor (e.g., 1.5 during peak hours).
        - detour_km: Extra distance traveled due to other pooling stops.
        
        Returns:
        - Dict with 'total_price', 'base_price', 'pooling_discount', and 'surge_amount'.
        """
        
        # 1. Base price for the individual trip
        individual_base_price = self.base_fare + (distance_km * self.rate_per_km)
        
        # 2. Dynamic Surge
        surge_amount = individual_base_price * (demand_multiplier - 1.0)
        total_before_discount = individual_base_price + surge_amount
        
        # 3. Pooling Discount Logic
        # More passengers = higher discount percentage
        # 1 passenger: 0%
        # 2 passengers: 25%
        # 3+ passengers: 40%
        discount_percentage = 0.0
        if passenger_count == 2:
            discount_percentage = 0.25
        elif passenger_count >= 3:
            discount_percentage = 0.40
            
        discount_amount = total_before_discount * discount_percentage
        
        # 4. Detour Compensation (Penalty)
        # If the rider is detoured significantly, we reduce their price further
        detour_compensation = detour_km * self.rate_per_km * self.detour_penalty_multiplier
        
        # Final calculation
        final_price = max(self.base_fare, total_before_discount - discount_amount - detour_compensation)
        
        return {
            "final_price": round(final_price, 2),
            "base_individual_price": round(individual_base_price, 2),
            "pooling_discount": round(discount_amount, 2),
            "detour_compensation": round(detour_compensation, 2),
            "surge_amount": round(surge_amount, 2)
        }
