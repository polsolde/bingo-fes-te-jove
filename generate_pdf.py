
import generate
import time
import random
from reportlab.lib.pagesizes import A4, letter, landscape
from reportlab.pdfgen import canvas
from reportlab.lib import colors, utils
from reportlab.lib.units import cm
from typing import List, Optional
import os


class BingoPDFGenerator:
    """
    Professional PDF generator for bingo cards using the new BingoCardManager system.
    Eliminates duplicates and provides efficient batch processing.
    
    🎯 EASY TUNING GUIDE:
    All layout parameters are in the generate_pdf() method under "EASY TUNING PARAMETERS"
    
    To adjust:
    - CARD_WIDTH: Makes cards wider/narrower
    - CARD_HEIGHT: Makes cards taller/shorter (ACTUALLY WORKS NOW!)
    - CARD_VERTICAL_SPACING: Space between cards vertically
    - CARD_HORIZONTAL_SPACING: Space between columns
    - PAGE_MARGIN_TOP: How far cards are from top of page
    - PAGE_MARGIN_LEFT: How far cards are from left of page
    - TEXT_DISTANCE_FROM_TOP: How close text is to card top
    - GRID_DISTANCE_FROM_TEXT: Space between text and bingo grid
    """
    
    def __init__(self, 
                 image_path: str = "Logo_FJ_imatge-invert.jpg",
                 cards_per_page: int = 6,  # 6 cards vertically per page
                 title: str = "GRAN BINGO DE FES-TE JOVE"):
        self.image_path = image_path
        self.cards_per_page = cards_per_page
        self.title = title
        
        # Layout configuration - fixed dimensions for consistency
        self.num_size = 18  # Font size for numbers
        self.photo_margin = 1
        
        # Card manager for unique card generation
        self.card_manager = generate.BingoCardManager()
        
    def _get_image_dimensions(self, path: str, width: float, height: float) -> tuple:
        """Calculate image dimensions maintaining aspect ratio."""
        try:
            img = utils.ImageReader(path)
            img_width, img_height = img.getSize()
            aspect = img_height / float(img_width)
            return (width, width * aspect)
        except Exception as e:
            print(f"Warning: Could not load image {path}: {e}")
            return (width, height)

    def _draw_single_card(self, c: canvas.Canvas, card_data: List[List[int]], 
                         x: float, y: float, width: float, height: float, 
                         card_number: int, round_number: int, text_distance: float, grid_distance: float):
        """Draw a single bingo card on the canvas."""
        rows = len(card_data)
        # Display only first 7 columns (like original format)
        display_cols = 7
        
        # Cell dimensions based on card size
        cell_width = width / display_cols  # Dynamic width based on card width
        # Calculate cell height based on available space (height - text area)
        available_height = height - text_distance - grid_distance - 10  # 10pt bottom margin
        cell_height = available_height / rows
        
        # Draw title using the tunable distance parameter
        c.setFont("Helvetica-Bold", 11)
        title_text = f"RONDA: {round_number}"
        c.drawString(x + 5, y - text_distance, title_text)  # Use TEXT_DISTANCE_FROM_TOP
        
        c.setFont("Helvetica-Bold", 11)
        title_width = c.stringWidth(self.title, "Helvetica-Bold", 11)
        c.drawString(x + width - title_width - 5, y - text_distance, self.title)  # Right aligned

        # Draw the card grid using the tunable distance parameter
        grid_start_y = y - text_distance - grid_distance  # Use GRID_DISTANCE_FROM_TEXT
        c.setFont("Helvetica-Bold", 16)  # Larger font for better readability
        c.setLineWidth(1.0)
        
        for i in range(rows):
            for j in range(display_cols):  # Only show first 7 columns
                cell_x = x + j * cell_width
                cell_y = grid_start_y - (i + 1) * cell_height
                
                # Get cell value (0 if beyond array bounds)
                cell_value = card_data[i][j] if j < len(card_data[i]) else 0
                
                if cell_value != 0:
                    # Draw number - centered in cell
                    text = str(cell_value)
                    text_width = c.stringWidth(text, "Helvetica-Bold", 16)
                    text_x = cell_x + (cell_width - text_width) / 2
                    text_y = cell_y + (cell_height - 16) / 2
                    c.drawString(text_x, text_y, text)
                else:
                    # Draw logo filling the entire cell
                    if os.path.exists(self.image_path):
                        # Fill the entire cell with the logo
                        c.drawImage(self.image_path, cell_x, cell_y, cell_width, cell_height)
                
                # Draw cell border
                c.rect(cell_x, cell_y, cell_width, cell_height)

    def generate_pdf(self, 
                    filename: str, 
                    total_cards: int, 
                    round_number: int = 1,
                    progress_callback: Optional[callable] = None) -> str:
        """
        Generate a PDF with the specified number of unique bingo cards.
        
        Args:
            filename: Output PDF filename
            total_cards: Total number of unique cards to generate
            round_number: Round number for labeling
            progress_callback: Optional callback for progress updates
            
        Returns:
            Path to generated PDF file
        """
        
        print(f"Generating PDF with {total_cards} unique bingo cards...")
        
        # Pre-generate all unique cards
        print("Preparing unique cards...")
        all_cards = self.card_manager.prepare_cards_for_event(total_cards)
        
        # Validate uniqueness
        if not self.card_manager.validate_cards_unique():
            raise RuntimeError("Generated cards are not unique!")
        
        print(f"All {len(all_cards)} cards are verified unique.")
        
        # Create PDF with landscape orientation
        c = canvas.Canvas(filename, pagesize=landscape(letter))
        width, height = landscape(letter)
        
        # ============================================================================
        # 🎯 EASY TUNING PARAMETERS - CHANGE THESE TO ADJUST YOUR LAYOUT
        # ============================================================================
        
        # Card dimensions
        CARD_WIDTH = 380          # Width of each bingo card
        CARD_HEIGHT = 200         # Height of each bingo card (THIS WILL ACTUALLY CHANGE HEIGHT!)
        
        # Spacing between cards
        CARD_VERTICAL_SPACING = 5    # Space between cards vertically
        CARD_HORIZONTAL_SPACING = 15  # Space between columns horizontally
        
        # Page margins (distance from page edges)
        PAGE_MARGIN_TOP = 5      # Distance from top of page to first cards
        PAGE_MARGIN_LEFT = 5     # Distance from left edge to cards
        
        # Text positioning on each card
        TEXT_DISTANCE_FROM_TOP = 5    # Distance of text from card top edge
        GRID_DISTANCE_FROM_TEXT = 5  # Distance from text to grid start
        
        # ============================================================================
        # Layout calculation (don't change unless you know what you're doing)
        # ============================================================================
        
        cards_per_page = 6
        cards_per_column = 3
        columns = 2
        
        # Calculate positions using fixed margins (not centering)
        start_x = PAGE_MARGIN_LEFT
        start_y = height - PAGE_MARGIN_TOP
        
        # Positions for cards in 2 columns
        x_positions = [start_x, start_x + CARD_WIDTH + CARD_HORIZONTAL_SPACING]
        y_positions = [start_y - i * (CARD_HEIGHT + CARD_VERTICAL_SPACING) for i in range(cards_per_column)]
        
        total_pages = (total_cards + cards_per_page - 1) // cards_per_page
        card_index = 0
        
        for page in range(total_pages):
            if progress_callback:
                progress_callback(page, total_pages)
                
            # Draw 6 cards in 2 columns (3 rows) on current page
            for card_position in range(cards_per_page):
                if card_index >= total_cards:
                    break
                    
                card_data = all_cards[card_index].tolist()
                
                # Calculate position: alternate columns, then move to next row
                column = card_position % columns  # 0,1,0,1,0,1
                row = card_position // columns    # 0,0,1,1,2,2
                
                x = x_positions[column]
                y = y_positions[row]
                
                self._draw_single_card(
                    c, card_data, x, y, CARD_WIDTH, CARD_HEIGHT,
                    card_index + 1, round_number, TEXT_DISTANCE_FROM_TOP, GRID_DISTANCE_FROM_TEXT
                )
                
                card_index += 1
            
            # Add page number
            c.setFont("Helvetica", 8)
            c.drawString(width - 50, 10, f"Page {page + 1}/{total_pages}")
            
            c.showPage()
        
        c.save()
        
        # Print statistics
        stats = self.card_manager.generator.get_stats()
        print(f"\nPDF Generation Complete!")
        print(f"- File: {filename}")
        print(f"- Total cards: {total_cards}")
        print(f"- Pages: {total_pages}")
        print(f"- Cards per page: 6 (2 columns × 3 rows layout)")
        print(f"- Memory usage: {stats['memory_usage_mb']:.2f} MB")
        print(f"- All cards verified unique: {self.card_manager.validate_cards_unique()}")
        
        return filename


def create_bingo_pdf_for_event(round_number: int, 
                             total_cards: int = 8000,
                             output_dir: str = "bingo_cards",
                             image_path: str = "Logo_FJ_imatge-invert.jpg") -> str:
    """
    Convenience function to create a bingo PDF for an event.
    
    Args:
        round_number: Round number for the event
        total_cards: Total number of unique cards needed
        output_dir: Directory to save the PDF
        image_path: Path to the logo image
        
    Returns:
        Path to the generated PDF
    """
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate filename with timestamp for uniqueness
    timestamp = int(time.time())
    filename = os.path.join(output_dir, f"ronda_{round_number}_{timestamp}.pdf")
    
    # Create generator and generate PDF
    generator = BingoPDFGenerator(image_path=image_path)
    
    def progress_callback(current_page: int, total_pages: int):
        if current_page % 10 == 0 or current_page == total_pages - 1:
            print(f"Processing page {current_page + 1}/{total_pages}...")
    
    return generator.generate_pdf(filename, total_cards, round_number, progress_callback)


# Legacy function for backwards compatibility (DEPRECATED)
def create_pdf(filename: str, image_path: str):
    """
    DEPRECATED: Use create_bingo_pdf_for_event() instead.
    This function is kept for backwards compatibility but may generate duplicates.
    """
    print("WARNING: Using deprecated create_pdf function. Consider using create_bingo_pdf_for_event().")
    
    # Use minimal card count for legacy compatibility
    generator = BingoPDFGenerator(image_path=image_path)
    return generator.generate_pdf(filename, 100, 1)  # Generate only 100 cards


if __name__ == "__main__":
    # Example usage for generating 8000 unique cards
    try:
        round_number = 9
        total_cards = 8000
        
        print(f"Generating {total_cards} unique bingo cards for round {round_number}...")
        
        pdf_path = create_bingo_pdf_for_event(
            round_number=round_number,
            total_cards=total_cards,
            output_dir="bingo_cards/final",
            image_path="Logo_FJ_imatge-invert.jpg"
        )
        
        print(f"\nSUCCESS: Generated {pdf_path}")
        print("No duplicates guaranteed!")
        
    except Exception as e:
        print(f"ERROR: {e}")
        raise