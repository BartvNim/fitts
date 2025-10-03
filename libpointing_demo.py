#!/usr/bin/env python3
"""
libpointing Raw HID Mouse Demo

This demo uses the actual libpointing C++ library (via Python bindings) to:
- Get raw HID events directly from pointing devices
- Bypass OS transfer functions
- Display real device parameters (resolution, frequency)
- Show raw counts (not pixels) from the device

Requirements:
- libpointing installed (brew install libpointing on macOS)
- Python bindings built (see README.md)
"""

import sys
import json
import threading
from pathlib import Path

# Add libpointing bindings to path
sys.path.insert(0, str(Path(__file__).parent / "libpointing/bindings/Python/cython"))

try:
    from libpointing.libpointing import PointingDevice, DisplayDevice, PointingDeviceManager
    import pygame
    print("✓ All dependencies loaded successfully")
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("\nPlease ensure:")
    print("1. libpointing is installed: brew install libpointing")
    print("2. Python bindings are built: see README.md")
    print("3. pygame is installed: pip install pygame")
    sys.exit(1)

# --- Configuration ---
CONFIG_FILE = "config.json"

DEFAULT_CONFIG = {
    "device": {
        "uri": "any:?debugLevel=2",
        "description": "Any connected pointing device"
    },
    "display": {
        "width": 1200,
        "height": 800,
        "target_size": 25,
        "background_color": [20, 20, 25],
        "target_color": [100, 200, 255],
        "text_color": [220, 220, 220]
    }
}


def load_config():
    """Load configuration from JSON file or use defaults."""
    config_path = Path(CONFIG_FILE)
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            print(f"✓ Loaded configuration from {CONFIG_FILE}")
            return config
        except Exception as e:
            print(f"⚠ Error loading config: {e}, using defaults")
    return DEFAULT_CONFIG


class RawPointer:
    """Manages raw pointer position and data from libpointing."""
    
    def __init__(self, width, height, target_size, target_color):
        self.width = width
        self.height = height
        self.target_size = target_size
        self.target_color = target_color
        
        # Position in screen space
        self.x = width // 2
        self.y = height // 2
        
        # Raw HID data
        self.raw_dx = 0
        self.raw_dy = 0
        self.total_counts_x = 0
        self.total_counts_y = 0
        self.event_count = 0
        self.last_timestamp = 0
        
        # Thread safety
        self.lock = threading.Lock()
    
    def update_from_raw_hid(self, timestamp, dx, dy, buttons):
        """
        Update from raw HID event.
        
        Args:
            timestamp: Event timestamp in microseconds
            dx, dy: Raw counts from device (NOT pixels!)
            buttons: Button state bitmask
        """
        with self.lock:
            self.raw_dx = dx
            self.raw_dy = dy
            self.total_counts_x += dx
            self.total_counts_y += dy
            self.event_count += 1
            self.last_timestamp = timestamp
            
            # Update screen position (simple 1:1 mapping for demo)
            self.x = max(0, min(self.width, self.x + dx))
            self.y = max(0, min(self.height, self.y + dy))
    
    def get_position(self):
        """Thread-safe position getter."""
        with self.lock:
            return int(self.x), int(self.y)
    
    def get_stats(self):
        """Thread-safe stats getter."""
        with self.lock:
            return {
                'raw_dx': self.raw_dx,
                'raw_dy': self.raw_dy,
                'total_x': self.total_counts_x,
                'total_y': self.total_counts_y,
                'events': self.event_count,
                'timestamp': self.last_timestamp
            }
    
    def reset(self):
        """Reset pointer to center."""
        with self.lock:
            self.x = self.width // 2
            self.y = self.height // 2
            self.total_counts_x = 0
            self.total_counts_y = 0
    
    def draw(self, surface):
        """Draw crosshair pointer."""
        x, y = self.get_position()
        
        # Outer circle
        pygame.draw.circle(surface, self.target_color, (x, y), self.target_size, 2)
        
        # Crosshair lines
        pygame.draw.line(surface, self.target_color,
                        (x - self.target_size, y),
                        (x + self.target_size, y), 2)
        pygame.draw.line(surface, self.target_color,
                        (x, y - self.target_size),
                        (x, y + self.target_size), 2)
        
        # Center dot
        pygame.draw.circle(surface, self.target_color, (x, y), 4)


def draw_info_panel(surface, pointer, device_info, config, font):
    """Draw information panel with device and pointer data."""
    stats = pointer.get_stats()
    x, y = pointer.get_position()
    
    info_lines = [
        "=== libpointing Raw HID Demo ===",
        "",
        f"Device: {device_info.get('vendor', 'Unknown')} {device_info.get('product', '')}",
        f"URI: {device_info.get('uri', 'N/A')}",
        f"VID:PID: {device_info.get('vendor_id', '?')}:{device_info.get('product_id', '?')}",
        f"Resolution: {device_info.get('resolution', '?')} counts/inch",
        f"Update Freq: {device_info.get('update_freq', '?')} Hz",
        "",
        "=== Raw HID Data ===",
        f"Position: ({x}, {y})",
        f"Last Delta: ({stats['raw_dx']}, {stats['raw_dy']}) counts",
        f"Total Counts: ({stats['total_x']}, {stats['total_y']})",
        f"Events Received: {stats['events']}",
        f"Last Timestamp: {stats['timestamp']} μs",
        "",
        "=== Controls ===",
        "R - Reset position",
        "ESC/Q - Quit",
    ]
    
    y_offset = 15
    text_color = tuple(config['display']['text_color'])
    
    for line in info_lines:
        text_surface = font.render(line, True, text_color)
        surface.blit(text_surface, (15, y_offset))
        y_offset += 28


def main():
    """Main application."""
    # Load configuration
    config = load_config()
    
    # Initialize Pygame
    pygame.init()
    width = config['display']['width']
    height = config['display']['height']
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("libpointing Raw HID Demo")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 22)
    
    print("\n" + "="*70)
    print("  libpointing Raw HID Mouse Demo")
    print("="*70)
    
    # Initialize libpointing device
    device_uri = config['device']['uri']
    print(f"\nInitializing device: {device_uri}")
    
    try:
        # Create pointing device (libpointing expects bytes)
        if isinstance(device_uri, str):
            device_uri_bytes = device_uri.encode('utf-8')
        else:
            device_uri_bytes = device_uri
        
        pointing_device = PointingDevice(device_uri_bytes)
        
        # Get device information
        # Note: getURI() might fail on some bindings, use fallback
        try:
            uri_str = pointing_device.getURI()
            if isinstance(uri_str, bytes):
                uri_str = uri_str.decode('utf-8')
        except:
            uri_str = device_uri
        
        device_info = {
            'uri': uri_str,
            'vendor_id': f"0x{pointing_device.getVendorID():04x}",
            'product_id': f"0x{pointing_device.getProductID():04x}",
            'vendor': pointing_device.getVendor().decode('utf-8') if isinstance(pointing_device.getVendor(), bytes) else pointing_device.getVendor(),
            'product': pointing_device.getProduct().decode('utf-8') if isinstance(pointing_device.getProduct(), bytes) else pointing_device.getProduct(),
            'resolution': pointing_device.getResolution(),
            'update_freq': pointing_device.getUpdateFrequency()
        }
        
        print(f"✓ Device initialized successfully!")
        print(f"  Vendor: {device_info['vendor']}")
        print(f"  Product: {device_info['product']}")
        print(f"  VID:PID: {device_info['vendor_id']}:{device_info['product_id']}")
        print(f"  Resolution: {device_info['resolution']} counts/inch")
        print(f"  Update Frequency: {device_info['update_freq']} Hz")
        print(f"  URI: {device_info['uri']}")
        
    except Exception as e:
        import traceback
        print(f"✗ Failed to initialize libpointing device: {e}")
        print("\nFull traceback:")
        traceback.print_exc()
        print("\nTroubleshooting:")
        print("  - Check that libpointing is installed: brew list libpointing")
        print("  - Try different URI: 'any:', 'usb:', 'usb:046d:c52b'")
        print("  - Check device permissions")
        sys.exit(1)
    
    # Create pointer
    pointer = RawPointer(
        width, height,
        config['display']['target_size'],
        tuple(config['display']['target_color'])
    )
    
    # Set up callback for raw HID events
    def pointing_callback(timestamp, dx, dy, buttons):
        """Callback receives raw HID events directly from device."""
        pointer.update_from_raw_hid(timestamp, dx, dy, buttons)
    
    pointing_device.setCallback(pointing_callback)
    
    print("\n✓ Ready! Move your mouse to see raw HID data.")
    print("  Controls: R=Reset, ESC/Q=Quit")
    print("="*70 + "\n")
    
    # Hide system cursor
    pygame.mouse.set_visible(False)
    
    # Main loop
    running = True
    try:
        while running:
            # Process libpointing events (non-blocking)
            PointingDevice.idle(1)  # 1ms idle
            
            # Handle pygame events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_ESCAPE, pygame.K_q):
                        running = False
                    elif event.key == pygame.K_r:
                        pointer.reset()
                        print("Position reset to center")
            
            # Render
            screen.fill(tuple(config['display']['background_color']))
            pointer.draw(screen)
            draw_info_panel(screen, pointer, device_info, config, font)
            pygame.display.flip()
            
            clock.tick(60)  # 60 FPS
    
    finally:
        # Cleanup
        del pointing_device
        pygame.quit()
        print("\nDemo closed. Thank you for using libpointing!")


if __name__ == "__main__":
    main()
