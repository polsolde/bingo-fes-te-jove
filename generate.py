
import numpy as np
import hashlib
import time
from typing import List, Set, Tuple, Optional
import random

class BingoCardGenerator:
    """
    UK-style bingo card generator (1-90 numbers, 3 rows x 9 columns, 5 numbers per row)
    Ensures unique cards and provides efficient batch generation.
    """
    
    def __init__(self, seed: Optional[int] = None):
        """Initialize the generator with optional seed for reproducibility."""
        if seed is None:
            seed = int(time.time() * 1000000) % (2**32)  # More precise seeding
        
        self.rng = np.random.RandomState(seed)
        self.generated_cards: Set[str] = set()
        
        # Column ranges for UK bingo: 1-9, 10-19, 20-29, ..., 80-90
        self.column_ranges = [(i*10 + 1, min(i*10 + 10, 90)) for i in range(9)]
        
    def _generate_single_card(self) -> np.ndarray:
        """Generate a single bingo card following UK rules."""
        max_attempts = 1000
        
        for attempt in range(max_attempts):
            card = np.zeros((3, 9), dtype=int)
            
            # Step 1: Distribute numbers across columns to ensure 15 total
            # Each column gets 1-3 numbers, totaling 15
            column_counts = self._generate_column_distribution()
            
            # Step 2: Fill each column with random numbers from its range
            for col in range(9):
                start, end = self.column_ranges[col]
                available_numbers = list(range(start, end + 1))
                num_count = column_counts[col]
                
                if num_count == 0:
                    continue
                    
                # Select random numbers for this column
                selected_numbers = sorted(self.rng.choice(
                    available_numbers, num_count, replace=False
                ))
                
                # Place numbers in random rows within this column
                available_rows = list(range(3))
                selected_rows = sorted(self.rng.choice(
                    available_rows, num_count, replace=False
                ))
                
                for i, row in enumerate(selected_rows):
                    card[row, col] = selected_numbers[i]
            
            # Step 3: Redistribute numbers to ensure exactly 5 per row
            if self._adjust_card_to_five_per_row(card):
                return card
                
        raise RuntimeError(f"Failed to generate valid card after {max_attempts} attempts")
    
    def _generate_column_distribution(self) -> List[int]:
        """Generate a distribution of numbers across 9 columns totaling 15."""
        # Start with at least 1 number per column (9 total)
        counts = [1] * 9
        remaining = 15 - 9  # 6 more numbers to distribute
        
        # Randomly distribute the remaining 6 numbers
        for _ in range(remaining):
            col = self.rng.randint(0, 9)
            if counts[col] < 3:  # Max 3 per column
                counts[col] += 1
            else:
                # Find a column with space
                available_cols = [i for i in range(9) if counts[i] < 3]
                if available_cols:
                    col = self.rng.choice(available_cols)
                    counts[col] += 1
        
        return counts
    
    def _adjust_card_to_five_per_row(self, card: np.ndarray) -> bool:
        """Adjust card by moving numbers between rows to achieve exactly 5 per row."""
        max_attempts = 100
        
        for attempt in range(max_attempts):
            row_counts = np.sum(card != 0, axis=1)
            
            # If all rows have exactly 5 numbers, we're done
            if np.all(row_counts == 5):
                return True
            
            # Find rows with too many or too few numbers
            excess_rows = np.where(row_counts > 5)[0]
            deficit_rows = np.where(row_counts < 5)[0]
            
            if len(excess_rows) == 0 or len(deficit_rows) == 0:
                break
            
            # Move a number from an excess row to a deficit row
            excess_row = self.rng.choice(excess_rows)
            deficit_row = self.rng.choice(deficit_rows)
            
            # Find a column where we can move a number
            for col in range(9):
                if card[excess_row, col] != 0 and card[deficit_row, col] == 0:
                    # Move the number
                    card[deficit_row, col] = card[excess_row, col]
                    card[excess_row, col] = 0
                    break
        
        # Final validation
        row_counts = np.sum(card != 0, axis=1)
        return np.all(row_counts == 5)
    
    def _card_to_hash(self, card: np.ndarray) -> str:
        """Convert card to a hash string for duplicate detection."""
        return hashlib.md5(card.tobytes()).hexdigest()
    
    def generate_unique_card(self) -> np.ndarray:
        """Generate a single unique bingo card."""
        max_attempts = 10000
        
        for attempt in range(max_attempts):
            card = self._generate_single_card()
            card_hash = self._card_to_hash(card)
            
            if card_hash not in self.generated_cards:
                self.generated_cards.add(card_hash)
                return card
                
        raise RuntimeError(f"Failed to generate unique card after {max_attempts} attempts")
    
    def generate_batch(self, num_cards: int) -> List[np.ndarray]:
        """Generate a batch of unique bingo cards."""
        cards = []
        
        print(f"Generating {num_cards} unique bingo cards...")
        for i in range(num_cards):
            if i > 0 and i % 100 == 0:
                print(f"Generated {i}/{num_cards} cards ({len(self.generated_cards)} unique so far)")
            
            card = self.generate_unique_card()
            cards.append(card)
            
        print(f"Successfully generated {len(cards)} unique cards")
        return cards
    
    def get_stats(self) -> dict:
        """Get statistics about generated cards."""
        return {
            'total_generated': len(self.generated_cards),
            'memory_usage_mb': len(self.generated_cards) * 32 / (1024 * 1024)  # Rough estimate
        }


class BingoCardManager:
    """
    High-level manager for bingo card operations.
    Handles large-scale generation, persistence, and validation.
    """
    
    def __init__(self, seed: Optional[int] = None):
        self.generator = BingoCardGenerator(seed)
        self.cards_cache: List[np.ndarray] = []
    
    def prepare_cards_for_event(self, total_cards_needed: int, batch_size: int = 1000) -> List[np.ndarray]:
        """
        Prepare cards for a large event, generating in batches to manage memory.
        """
        all_cards = []
        remaining = total_cards_needed
        
        while remaining > 0:
            current_batch_size = min(batch_size, remaining)
            batch = self.generator.generate_batch(current_batch_size)
            all_cards.extend(batch)
            remaining -= current_batch_size
            
            if remaining > 0:
                print(f"Batch complete. {remaining} cards remaining...")
        
        self.cards_cache = all_cards
        return all_cards
    
    def get_card(self, index: int) -> np.ndarray:
        """Get a specific card by index from the cache."""
        if index >= len(self.cards_cache):
            raise IndexError(f"Card index {index} out of range (have {len(self.cards_cache)} cards)")
        return self.cards_cache[index]
    
    def validate_cards_unique(self) -> bool:
        """Validate that all cached cards are unique."""
        if not self.cards_cache:
            return True
            
        hashes = set()
        for card in self.cards_cache:
            card_hash = hashlib.md5(card.tobytes()).hexdigest()
            if card_hash in hashes:
                return False
            hashes.add(card_hash)
        return True


# Legacy compatibility function
def generate_cards(seed_value):
    """
    Legacy function for backwards compatibility.
    Returns 6 cards as a 3D array like the original.
    """
    generator = BingoCardGenerator(seed_value)
    cards = generator.generate_batch(6)
    
    # Convert to original format: (6, 3, 9) array
    result = np.zeros((6, 3, 9), dtype=int)
    for i, card in enumerate(cards):
        result[i] = card
    
    return result


if __name__ == "__main__":
    # Test the new system
    print("Testing new bingo card generation system...")
    
    # Test single card generation
    generator = BingoCardGenerator()
    card = generator.generate_unique_card()
    print(f"Sample card:\n{card}")
    
    # Test batch generation
    manager = BingoCardManager()
    test_cards = manager.prepare_cards_for_event(100)
    
    print(f"\nGenerated {len(test_cards)} cards")
    print(f"All cards unique: {manager.validate_cards_unique()}")
    print(f"Generator stats: {manager.generator.get_stats()}")

