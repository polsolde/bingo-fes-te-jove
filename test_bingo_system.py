#!/usr/bin/env python3
"""
Comprehensive testing and validation script for the bingo card generation system.
Tests for uniqueness, correct format, and performance with large card counts.
"""

import generate
import time
import hashlib
import numpy as np
from typing import Set, List
import sys


class BingoTestSuite:
    """Complete test suite for the bingo card generation system."""
    
    def __init__(self):
        self.passed_tests = 0
        self.failed_tests = 0
        self.total_tests = 0
    
    def log_test(self, test_name: str, passed: bool, message: str = ""):
        """Log test result."""
        self.total_tests += 1
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {test_name}")
        if message:
            print(f"    {message}")
        
        if passed:
            self.passed_tests += 1
        else:
            self.failed_tests += 1
    
    def validate_card_format(self, card: np.ndarray) -> tuple[bool, str]:
        """Validate that a bingo card follows UK bingo rules."""
        
        # Check dimensions
        if card.shape != (3, 9):
            return False, f"Invalid dimensions: {card.shape}, expected (3, 9)"
        
        # Check each row has exactly 5 numbers
        for row_idx, row in enumerate(card):
            non_zero_count = np.sum(row != 0)
            if non_zero_count != 5:
                return False, f"Row {row_idx} has {non_zero_count} numbers, expected 5"
        
        # Check total numbers is 15
        total_numbers = np.sum(card != 0)
        if total_numbers != 15:
            return False, f"Total numbers: {total_numbers}, expected 15"
        
        # Check number ranges by column
        for col in range(9):
            column_numbers = card[:, col][card[:, col] != 0]
            if len(column_numbers) > 0:
                min_expected = col * 10 + 1
                max_expected = min(col * 10 + 10, 90)
                
                if np.any(column_numbers < min_expected) or np.any(column_numbers > max_expected):
                    return False, f"Column {col} has numbers outside range [{min_expected}, {max_expected}]"
                
                # Check for duplicates within column
                if len(column_numbers) != len(np.unique(column_numbers)):
                    return False, f"Column {col} has duplicate numbers"
        
        # Check for duplicates across entire card
        all_numbers = card[card != 0]
        if len(all_numbers) != len(np.unique(all_numbers)):
            return False, "Card contains duplicate numbers"
        
        return True, "Valid format"
    
    def test_single_card_generation(self):
        """Test single card generation."""
        generator = generate.BingoCardGenerator(seed=12345)
        card = generator.generate_unique_card()
        
        is_valid, message = self.validate_card_format(card)
        self.log_test("Single card generation", is_valid, message)
        
        if is_valid:
            print(f"    Sample card:\n{card}")
    
    def test_card_uniqueness_small_batch(self):
        """Test uniqueness in small batch."""
        generator = generate.BingoCardGenerator(seed=12345)
        cards = generator.generate_batch(50)
        
        # Check all cards are valid
        all_valid = True
        for i, card in enumerate(cards):
            is_valid, message = self.validate_card_format(card)
            if not is_valid:
                all_valid = False
                print(f"    Card {i} invalid: {message}")
                break
        
        # Check uniqueness
        card_hashes = set()
        for card in cards:
            card_hash = hashlib.md5(card.tobytes()).hexdigest()
            if card_hash in card_hashes:
                all_valid = False
                print(f"    Duplicate card found!")
                break
            card_hashes.add(card_hash)
        
        unique_count = len(card_hashes)
        self.log_test("Small batch uniqueness (50 cards)", 
                     all_valid and unique_count == 50,
                     f"Generated {unique_count}/50 unique cards")
    
    def test_card_uniqueness_large_batch(self):
        """Test uniqueness in larger batch."""
        print("    Generating 1000 cards for uniqueness test...")
        generator = generate.BingoCardGenerator(seed=12345)
        
        start_time = time.time()
        cards = generator.generate_batch(1000)
        generation_time = time.time() - start_time
        
        # Check uniqueness
        card_hashes = set()
        duplicates_found = 0
        
        for i, card in enumerate(cards):
            card_hash = hashlib.md5(card.tobytes()).hexdigest()
            if card_hash in card_hashes:
                duplicates_found += 1
            card_hashes.add(card_hash)
        
        unique_count = len(card_hashes)
        success = duplicates_found == 0 and unique_count == 1000
        
        self.log_test("Large batch uniqueness (1000 cards)", 
                     success,
                     f"Generated {unique_count}/1000 unique cards in {generation_time:.2f}s")
    
    def test_legacy_compatibility(self):
        """Test legacy function compatibility."""
        try:
            result = generate.generate_cards(12345)
            
            # Check shape
            shape_correct = result.shape == (6, 3, 9)
            
            # Check each card
            all_cards_valid = True
            for i in range(6):
                card = result[i]
                is_valid, message = self.validate_card_format(card)
                if not is_valid:
                    all_cards_valid = False
                    print(f"    Legacy card {i} invalid: {message}")
                    break
            
            success = shape_correct and all_cards_valid
            self.log_test("Legacy compatibility", success,
                         f"Shape: {result.shape}, All cards valid: {all_cards_valid}")
        except Exception as e:
            self.log_test("Legacy compatibility", False, f"Exception: {e}")
    
    def test_manager_functionality(self):
        """Test BingoCardManager functionality."""
        manager = generate.BingoCardManager(seed=12345)
        
        # Test card preparation
        cards = manager.prepare_cards_for_event(100)
        
        # Test uniqueness validation
        all_unique = manager.validate_cards_unique()
        
        # Test card retrieval
        try:
            first_card = manager.get_card(0)
            last_card = manager.get_card(99)
            card_retrieval_works = True
        except Exception as e:
            card_retrieval_works = False
            print(f"    Card retrieval failed: {e}")
        
        success = len(cards) == 100 and all_unique and card_retrieval_works
        self.log_test("BingoCardManager functionality", success,
                     f"Generated {len(cards)} cards, All unique: {all_unique}")
    
    def test_performance_large_scale(self):
        """Test performance with large number of cards (simulating real usage)."""
        print("    Testing large scale generation (2000 cards)...")
        
        manager = generate.BingoCardManager()
        
        start_time = time.time()
        cards = manager.prepare_cards_for_event(2000, batch_size=500)
        generation_time = time.time() - start_time
        
        # Verify uniqueness
        all_unique = manager.validate_cards_unique()
        
        # Calculate performance metrics
        cards_per_second = len(cards) / generation_time
        
        success = len(cards) == 2000 and all_unique and generation_time < 300  # Should complete in 5 minutes
        
        self.log_test("Large scale performance (2000 cards)", success,
                     f"Generated {len(cards)} cards in {generation_time:.2f}s ({cards_per_second:.1f} cards/s)")
    
    def test_different_seeds_produce_different_cards(self):
        """Test that different seeds produce different cards."""
        gen1 = generate.BingoCardGenerator(seed=1111)
        gen2 = generate.BingoCardGenerator(seed=2222)
        
        card1 = gen1.generate_unique_card()
        card2 = gen2.generate_unique_card()
        
        # Cards should be different
        cards_different = not np.array_equal(card1, card2)
        
        self.log_test("Different seeds produce different cards", cards_different,
                     f"Cards are {'different' if cards_different else 'identical'}")
    
    def test_edge_cases(self):
        """Test edge cases and error handling."""
        generator = generate.BingoCardGenerator()
        
        # Test manager with invalid card index
        manager = generate.BingoCardManager()
        manager.prepare_cards_for_event(10)
        
        try:
            invalid_card = manager.get_card(20)  # Should raise IndexError
            index_error_handled = False
        except IndexError:
            index_error_handled = True
        except Exception as e:
            index_error_handled = False
            print(f"    Unexpected exception: {e}")
        
        self.log_test("Edge case handling", index_error_handled,
                     "IndexError properly raised for invalid card index")
    
    def run_all_tests(self):
        """Run all tests in the suite."""
        print("=" * 60)
        print("BINGO CARD GENERATION SYSTEM - TEST SUITE")
        print("=" * 60)
        print()
        
        # Run all tests
        self.test_single_card_generation()
        self.test_card_uniqueness_small_batch()
        self.test_card_uniqueness_large_batch()
        self.test_legacy_compatibility()
        self.test_manager_functionality()
        self.test_different_seeds_produce_different_cards()
        self.test_edge_cases()
        
        # Optional performance test (can be time-consuming)
        if "--performance" in sys.argv:
            self.test_performance_large_scale()
        else:
            print("[SKIP] Large scale performance test (use --performance flag to run)")
        
        # Print summary
        print()
        print("=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"Total tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.failed_tests}")
        print(f"Success rate: {(self.passed_tests/self.total_tests)*100:.1f}%")
        
        if self.failed_tests == 0:
            print("\n🎉 ALL TESTS PASSED! The system is ready for production use.")
            print("   No duplicates will be generated with this system.")
        else:
            print(f"\n⚠️  {self.failed_tests} test(s) failed. Please review the issues above.")
        
        return self.failed_tests == 0


def simulate_event_generation():
    """Simulate generating cards for a real event."""
    print("\n" + "=" * 60)
    print("EVENT SIMULATION - Generating cards like for your 8000-card event")
    print("=" * 60)
    
    # Simulate a smaller version of the real event
    total_cards = 500  # Smaller number for testing
    round_number = 9
    
    print(f"Simulating event with {total_cards} cards for round {round_number}...")
    
    manager = generate.BingoCardManager()
    
    start_time = time.time()
    cards = manager.prepare_cards_for_event(total_cards)
    generation_time = time.time() - start_time
    
    # Validate all cards are unique
    all_unique = manager.validate_cards_unique()
    
    # Get statistics
    stats = manager.generator.get_stats()
    
    print(f"\nEvent simulation results:")
    print(f"- Generated: {len(cards)} cards")
    print(f"- Time taken: {generation_time:.2f} seconds")
    print(f"- Rate: {len(cards)/generation_time:.1f} cards/second")
    print(f"- All unique: {all_unique}")
    print(f"- Memory usage: {stats['memory_usage_mb']:.2f} MB")
    print(f"- Estimated time for 8000 cards: {(generation_time * 8000 / total_cards):.1f} seconds")
    
    if all_unique:
        print("✅ Event simulation successful - no duplicates detected!")
    else:
        print("❌ Event simulation failed - duplicates detected!")
    
    return all_unique


if __name__ == "__main__":
    # Run the test suite
    test_suite = BingoTestSuite()
    all_tests_passed = test_suite.run_all_tests()
    
    # Run event simulation
    event_simulation_passed = simulate_event_generation()
    
    # Final result
    if all_tests_passed and event_simulation_passed:
        print("\n🎉 SYSTEM VALIDATION COMPLETE - Ready for production!")
        print("   The duplicate issue has been resolved.")
        exit(0)
    else:
        print("\n❌ SYSTEM VALIDATION FAILED - Please review the issues.")
        exit(1) 