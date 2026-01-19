import pygame
import sys
import os
import win32gui
import win32con
import win32api
from ctypes import windll, wintypes, byref, sizeof
import importlib.resources
from typing import Optional, Tuple, List, Dict, Callable, Union

TITLEBAR_HEIGHT = 40
BUTTON_WIDTH = 55
BUTTON_HEIGHT = TITLEBAR_HEIGHT
PADDING = 8
TITLE_Y_OFFSET = 5
BG_COLOR = (30, 30, 30)
TITLE_CLIENT_BG = (25, 25, 25)
TITLE_CLIENT_TEXT = (230, 230, 230)
BUTTON_HOVER_BG = (150, 150, 150)

# Minimum window dimensions
MIN_WINDOW_WIDTH = 400
MIN_WINDOW_HEIGHT = 300

# Helper to get resource path for package data
def resource_path(filename: str) -> str:
	"""
	Get the absolute path to a resource file in the package assets folder.
	
	Args:
		filename: Name of the file in the assets folder
		
	Returns:
		Absolute path to the resource file
	"""
	try:
		with importlib.resources.path("easy_custom_titlebar.assets", filename) as p:
			return str(p)
	except (ModuleNotFoundError, FileNotFoundError, TypeError) as e:
		# Fallback to relative path if package resources aren't available
		fallback_path = os.path.join(os.path.dirname(__file__), "assets", filename)
		if os.path.exists(fallback_path):
			return fallback_path
		# If still not found, return the path anyway (caller should handle the error)
		return fallback_path

class CustomTitleBarWindow:
	"""
	A custom titlebar window manager for Pygame on Windows.
	
	Provides a borderless window with custom titlebar, drag-to-move,
	resize support, and customizable buttons.
	"""
	
	def __init__(
		self,
		width: int = 1200,
		height: int = 700,
		title: str = "",
		enable_scroll: bool = False,
		titlebar_color: Optional[Union[Tuple[int, int, int], str]] = None,
		button_color: Optional[Union[Tuple[int, int, int], str]] = None,
		button_hover_color: Optional[Union[Tuple[int, int, int], str]] = None,
		button_icon_color: str = "white",
		titlebar_border: bool = False,
		titlebar_border_color: Tuple[int, int, int] = (0, 0, 0),
		titlebar_border_thickness: int = 1,
		titlebar_font_family: str = "Consolas",
		titlebar_font_size: int = 28,
		titlebar_font_bold: bool = True,
		left_notch_width: int = 0,
		titlebar_height: int = 40,
		close_button_color: Tuple[int, int, int] = (200, 0, 0),
		close_button_hover_color: Tuple[int, int, int] = (255, 0, 0),
		minmax_button_hover_color: Optional[Tuple[int, int, int]] = None,
		window_icon: Optional[str] = None,
		minimize_icon: Optional[str] = None,
		maximize_icon: Optional[str] = None,
		restore_icon: Optional[str] = None,
		close_icon: Optional[str] = None,
		custom_buttons: Optional[List[Dict]] = None
	):
		"""
		Initialize the custom titlebar window.
		
		Args:
			width: Window width in pixels (minimum 400)
			height: Window height in pixels (minimum 300)
			title: Title text displayed in the titlebar
			enable_scroll: Enable vertical scrolling support
			titlebar_color: Background color (RGB tuple or hex string)
			button_color: Button background color (RGB tuple or hex string)
			button_hover_color: Button hover color (RGB tuple or hex string)
			button_icon_color: Icon color ("white" or "black")
			titlebar_border: Draw border at bottom of titlebar
			titlebar_border_color: Border color (RGB tuple)
			titlebar_border_thickness: Border thickness in pixels
			titlebar_font_family: Font family name
			titlebar_font_size: Font size in pixels
			titlebar_font_bold: Use bold font
			left_notch_width: Width of left notch area
			titlebar_height: Height of titlebar in pixels
			close_button_color: Close button color (RGB tuple)
			close_button_hover_color: Close button hover color (RGB tuple)
			minmax_button_hover_color: Min/max button hover color (RGB tuple)
			window_icon: Path to window icon file
			minimize_icon: Path to custom minimize icon
			maximize_icon: Path to custom maximize icon
			restore_icon: Path to custom restore icon
			close_icon: Path to custom close icon
			custom_buttons: List of custom button dictionaries
		"""
		# Validate inputs
		width = max(MIN_WINDOW_WIDTH, int(width))
		height = max(MIN_WINDOW_HEIGHT, int(height))
		titlebar_height = max(20, int(titlebar_height))
		left_notch_width = max(0, int(left_notch_width))
		titlebar_border_thickness = max(1, int(titlebar_border_thickness))
		titlebar_font_size = max(8, int(titlebar_font_size))
		
		# Initialize pygame
		if not pygame.get_init():
			pygame.init()
		
		self.width = width
		self.height = height
		self.title = str(title) if title else ""
		self.enable_scroll = bool(enable_scroll)
		self.titlebar_border = bool(titlebar_border)
		self.titlebar_border_color = tuple(titlebar_border_color)
		self.titlebar_border_thickness = titlebar_border_thickness
		self.titlebar_font_family = str(titlebar_font_family)
		self.titlebar_font_size = titlebar_font_size
		self.titlebar_font_bold = bool(titlebar_font_bold)
		self.left_notch_width = left_notch_width
		self._titlebar_height = titlebar_height
		self.custom_buttons = list(custom_buttons) if custom_buttons else []
		
		# Validate custom buttons structure
		for i, btn in enumerate(self.custom_buttons):
			if not isinstance(btn, dict):
				raise TypeError(f"Custom button at index {i} must be a dictionary")
		
		# Set window/taskbar icon if provided
		if window_icon is not None:
			try:
				if os.path.exists(window_icon):
					icon_surface = pygame.image.load(window_icon)
					pygame.display.set_icon(icon_surface)
				else:
					print(f"[easy_custom_titlebar] Warning: Window icon file not found: {window_icon}")
			except (pygame.error, FileNotFoundError, OSError) as e:
				print(f"[easy_custom_titlebar] Failed to set window icon: {e}")
		# Handle titlebar color (accept hex or tuple)
		self.titlebar_color = self._parse_color(titlebar_color, TITLE_CLIENT_BG)
		# Handle button color
		self.button_color = self._parse_color(button_color, self.titlebar_color)
		# Handle button hover color
		self.button_hover_color = self._parse_color(button_hover_color, BUTTON_HOVER_BG)
		# Handle icon color
		icon_color_lower = str(button_icon_color).lower() if button_icon_color else "white"
		self.button_icon_color = "white" if icon_color_lower == "white" else "black"
		
		# Create window
		try:
			self.screen = pygame.display.set_mode((self.width, self.height), pygame.NOFRAME)
			pygame.display.set_caption(self.title)
		except pygame.error as e:
			raise RuntimeError(f"Failed to create window: {e}")
		
		# Get window handle - more reliable method
		self.hwnd = self._get_window_handle()
		if not self.hwnd:
			raise RuntimeError("Failed to acquire window handle")
		
		self._init_window_styles()
		self._center_window()
		# Window state
		self.dragging = False
		self.drag_offset = (0, 0)
		self.resizing = False
		self.resize_edge: Optional[str] = None
		self.is_maximized = False
		self.original_size = (self.width, self.height)
		self.original_pos = (0, 0)
		self.RESIZE_BORDER = 5
		self.resize_start_size: Optional[Tuple[int, int]] = None
		self.resize_start_pos: Optional[Tuple[int, int]] = None
		self.resize_mouse_start: Optional[Tuple[int, int]] = None
		self.scroll_y = 0.0
		self.running = True
		
		# Initialize fonts
		try:
			self.FONT = pygame.font.SysFont("Consolas", 18)
			self.HEADER_FONT = pygame.font.SysFont(
				self.titlebar_font_family,
				self.titlebar_font_size,
				bold=self.titlebar_font_bold
			)
		except Exception as e:
			print(f"[easy_custom_titlebar] Warning: Failed to load font, using default: {e}")
			self.FONT = pygame.font.Font(None, 18)
			self.HEADER_FONT = pygame.font.Font(None, self.titlebar_font_size)
		
		# Load button images (allow custom overrides)
		self.btn_imgs = self._load_button_images(
			minimize_icon, maximize_icon, restore_icon, close_icon
		)
		
		self.close_button_color = tuple(close_button_color)
		self.close_button_hover_color = tuple(close_button_hover_color)
		self.minmax_button_hover_color = (
			tuple(minmax_button_hover_color) if minmax_button_hover_color is not None
			else BUTTON_HOVER_BG
		)
	
	def _parse_color(self, color: Optional[Union[Tuple[int, int, int], str]], default: Tuple[int, int, int]) -> Tuple[int, int, int]:
		"""Parse color from hex string or tuple, return RGB tuple."""
		if color is None:
			return default
		if isinstance(color, str) and color.startswith("#"):
			try:
				hex_color = color.lstrip("#")
				if len(hex_color) == 6:
					return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
			except (ValueError, IndexError):
				pass
		if isinstance(color, (tuple, list)) and len(color) >= 3:
			return tuple(int(c) for c in color[:3])
		return default
	
	def _get_window_handle(self) -> Optional[int]:
		"""Get the window handle more reliably."""
		try:
			# Try to get handle from pygame window
			hwnd_str = pygame.display.get_wm_info().get('window')
			if hwnd_str:
				return int(hwnd_str)
		except (AttributeError, KeyError, ValueError):
			pass
		
		# Fallback to foreground window
		try:
			return win32gui.GetForegroundWindow()
		except Exception:
			pass
		
		# Last resort: find window by title
		try:
			def enum_handler(hwnd, ctx):
				if win32gui.IsWindowVisible(hwnd):
					window_text = win32gui.GetWindowText(hwnd)
					if self.title and self.title in window_text:
						ctx.append(hwnd)
			
			handles = []
			win32gui.EnumWindows(enum_handler, handles)
			if handles:
				return handles[0]
		except Exception:
			pass
		
		return None
	
	def _load_button_images(self, minimize_icon, maximize_icon, restore_icon, close_icon) -> Dict[str, pygame.Surface]:
		"""Load all button icon images with fallback handling."""
		def load_icon(path: Optional[str], fallback: str) -> pygame.Surface:
			if path is not None:
				try:
					if os.path.exists(path):
						return pygame.image.load(path).convert_alpha()
					else:
						print(f"[easy_custom_titlebar] Warning: Custom icon file not found: {path}")
				except (pygame.error, FileNotFoundError, OSError) as e:
					print(f"[easy_custom_titlebar] Failed to load custom icon {path}: {e}")
			
			# Load default icon
			try:
				icon_path = resource_path(fallback)
				if os.path.exists(icon_path):
					return pygame.image.load(icon_path).convert_alpha()
				else:
					raise FileNotFoundError(f"Default icon not found: {icon_path}")
			except Exception as e:
				print(f"[easy_custom_titlebar] Error loading default icon {fallback}: {e}")
				# Create a placeholder surface if all else fails
				surf = pygame.Surface((16, 16), pygame.SRCALPHA)
				pygame.draw.rect(surf, (255, 255, 255), (0, 0, 16, 16))
				return surf
		
		return {
			'minimize_white': load_icon(minimize_icon, 'minimize_white.png'),
			'maximize_white': load_icon(maximize_icon, 'maximize_white.png'),
			'restore_white': load_icon(restore_icon, 'restore_white.png'),
			'close_white': load_icon(close_icon, 'close_white.png'),
			'minimize_black': load_icon(minimize_icon, 'minimize_black.png'),
			'maximize_black': load_icon(maximize_icon, 'maximize_black.png'),
			'restore_black': load_icon(restore_icon, 'restore_black.png'),
			'close_black': load_icon(close_icon, 'close_black.png'),
		}

	@property
	def titlebar_height(self) -> int:
		"""Get the titlebar height."""
		return self._titlebar_height

	def _init_window_styles(self) -> None:
		"""Initialize and apply window styles."""
		try:
			style = win32gui.GetWindowLong(self.hwnd, win32con.GWL_STYLE)
			style = style & ~win32con.WS_CAPTION & ~win32con.WS_THICKFRAME
			style = style | win32con.WS_MAXIMIZEBOX | win32con.WS_MINIMIZEBOX | win32con.WS_SYSMENU
			win32gui.SetWindowLong(self.hwnd, win32con.GWL_STYLE, style)
			
			ex_style = win32gui.GetWindowLong(self.hwnd, win32con.GWL_EXSTYLE)
			ex_style = ex_style | win32con.WS_EX_LAYERED
			win32gui.SetWindowLong(self.hwnd, win32con.GWL_EXSTYLE, ex_style)
		except Exception as e:
			print(f"[easy_custom_titlebar] Warning: Failed to set window styles: {e}")
		
		# Set rounded corners (Windows 11+)
		try:
			DWMWA_WINDOW_CORNER_PREFERENCE = 33
			DWMWCP_ROUND = 2
			windll.dwmapi.DwmSetWindowAttribute(
				wintypes.HWND(self.hwnd),
				DWMWA_WINDOW_CORNER_PREFERENCE,
				byref(wintypes.INT(DWMWCP_ROUND)),
				sizeof(wintypes.INT)
			)
		except (AttributeError, OSError, Exception):
			# Rounded corners only work on Windows 11+, ignore errors
			pass

	def _center_window(self) -> None:
		"""Center the window on the screen."""
		try:
			screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
			screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
			x = max(0, (screen_width - self.width) // 2)
			y = max(0, (screen_height - self.height) // 2)
			win32gui.SetWindowPos(self.hwnd, 0, x, y, self.width, self.height, 0)
		except Exception as e:
			print(f"[easy_custom_titlebar] Warning: Failed to center window: {e}")

	def set_title(self, title: str) -> None:
		"""
		Set the window title.
		
		Args:
			title: New title text
		"""
		self.title = str(title)
		try:
			pygame.display.set_caption(self.title)
		except Exception as e:
			print(f"[easy_custom_titlebar] Warning: Failed to set title: {e}")

	def handle_event(self, event: pygame.event.Event) -> bool:
		"""
		Handle pygame events for window interaction.
		
		Args:
			event: Pygame event object
			
		Returns:
			True if event was handled, False otherwise
		"""
		try:
			if event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 1:
					mouse_pos = pygame.mouse.get_pos()
					
					# Check for resize area
					if self.is_resize_area(mouse_pos):
						self.resizing = True
						self.resize_edge = self.get_resize_edge(mouse_pos)
						if self.hwnd and self.resize_edge:
							try:
								rect = win32gui.GetWindowRect(self.hwnd)
								if rect:
									self.resize_start_size = (rect[2] - rect[0], rect[3] - rect[1])
									self.resize_start_pos = (rect[0], rect[1])
									self.resize_mouse_start = mouse_pos
									return True
							except Exception as e:
								print(f"[easy_custom_titlebar] Warning: Resize init failed: {e}")
								self.resizing = False
								self.resize_edge = None
					
					# Check titlebar area for dragging or button clicks
					try:
						w = self.screen.get_size()[0]
					except (AttributeError, pygame.error):
						return False
					
					if self.left_notch_width > 0:
						custom_rects, min_rect, max_rect, close_rect = self.get_button_rects(
							w - self.left_notch_width, x_offset=self.left_notch_width
						)
					else:
						custom_rects, min_rect, max_rect, close_rect = self.get_button_rects(w)
					
					if mouse_pos[1] < self.titlebar_height:
						# Custom button clicks
						for i, rect in enumerate(custom_rects):
							if i < len(self.custom_buttons) and rect.collidepoint(mouse_pos):
								btn = self.custom_buttons[i]
								if isinstance(btn, dict) and 'callback' in btn and callable(btn['callback']):
									try:
										btn['callback']()
									except Exception as e:
										print(f"[easy_custom_titlebar] Warning: Custom button callback error: {e}")
									return True
						
						# Start dragging if not clicking on standard buttons
						if not (min_rect.collidepoint(mouse_pos) or
						        max_rect.collidepoint(mouse_pos) or
						        close_rect.collidepoint(mouse_pos)):
							self.dragging = True
							self.drag_offset = (mouse_pos[0], mouse_pos[1])
							return True
			
			elif event.type == pygame.MOUSEBUTTONUP:
				if event.button == 1:
					self.dragging = False
					self.resizing = False
					self.resize_edge = None
					self.resize_start_size = None
					self.resize_start_pos = None
					self.resize_mouse_start = None
			
			elif event.type == pygame.MOUSEMOTION:
				if self.dragging:
					self.handle_drag(event.pos)
				elif self.resizing:
					self.handle_resize(event.pos)
				else:
					self.update_cursor(event.pos)
		except Exception as e:
			print(f"[easy_custom_titlebar] Warning: Event handling error: {e}")
		
		return False

	def update_cursor(self, pos: Tuple[int, int]) -> None:
		"""Update mouse cursor based on position."""
		try:
			if self.is_resize_area(pos):
				edge = self.get_resize_edge(pos)
				if edge in ['left', 'right']:
					pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZEWE)
				elif edge in ['top', 'bottom']:
					pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZENS)
				elif edge in ['topleft', 'bottomright']:
					pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZENWSE)
				elif edge in ['topright', 'bottomleft']:
					pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZENESW)
			else:
				pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
		except Exception as e:
			# Silently fail cursor updates
			pass

	def is_resize_area(self, pos: Tuple[int, int]) -> bool:
		"""Check if position is in window resize border area."""
		try:
			x, y = pos
			w, h = self.screen.get_size()
			return (x < self.RESIZE_BORDER or x > w - self.RESIZE_BORDER or
			        y < self.RESIZE_BORDER or y > h - self.RESIZE_BORDER)
		except (AttributeError, pygame.error, TypeError):
			return False

	def get_resize_edge(self, pos: Tuple[int, int]) -> Optional[str]:
		"""Get which edge the resize position is on."""
		try:
			x, y = pos
			w, h = self.screen.get_size()
			
			if x < self.RESIZE_BORDER:
				if y < self.RESIZE_BORDER:
					return 'topleft'
				elif y > h - self.RESIZE_BORDER:
					return 'bottomleft'
				return 'left'
			elif x > w - self.RESIZE_BORDER:
				if y < self.RESIZE_BORDER:
					return 'topright'
				elif y > h - self.RESIZE_BORDER:
					return 'bottomright'
				return 'right'
			elif y < self.RESIZE_BORDER:
				return 'top'
			elif y > h - self.RESIZE_BORDER:
				return 'bottom'
		except (AttributeError, pygame.error, TypeError):
			pass
		return None

	def handle_drag(self, pos: Tuple[int, int]) -> None:
		"""Handle window dragging."""
		if not self.is_maximized and self.hwnd:
			try:
				rect = win32gui.GetWindowRect(self.hwnd)
				if rect:
					x = rect[0] + (pos[0] - self.drag_offset[0])
					y = rect[1] + (pos[1] - self.drag_offset[1])
					# Ensure window stays on screen
					screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
					screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
					window_width = rect[2] - rect[0]
					window_height = rect[3] - rect[1]
					x = max(-window_width + 50, min(x, screen_width - 50))
					y = max(0, min(y, screen_height - 50))
					win32gui.SetWindowPos(self.hwnd, 0, x, y, 0, 0, win32con.SWP_NOSIZE)
			except Exception as e:
				print(f"[easy_custom_titlebar] Warning: Drag failed: {e}")

	def handle_resize(self, pos: Tuple[int, int]) -> None:
		"""Handle window resizing."""
		if (self.is_maximized or not self.hwnd or not self.resize_start_size or
		    not self.resize_start_pos or not self.resize_mouse_start or not self.resize_edge):
			return
		
		try:
			start_x, start_y = self.resize_start_pos
			start_w, start_h = self.resize_start_size
			mouse_start_x, mouse_start_y = self.resize_mouse_start
			dx = pos[0] - mouse_start_x
			dy = pos[1] - mouse_start_y
			x, y = start_x, start_y
			w, h = start_w, start_h
			
			# Get screen bounds
			screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
			screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
			
			if self.resize_edge in ['left', 'topleft', 'bottomleft']:
				new_width = start_w - dx
				if new_width >= MIN_WINDOW_WIDTH and x + dx >= 0:
					x = start_x + dx
					w = new_width
			if self.resize_edge in ['right', 'topright', 'bottomright']:
				new_width = start_w + dx
				if new_width >= MIN_WINDOW_WIDTH and x + new_width <= screen_width:
					w = new_width
			if self.resize_edge in ['top', 'topleft', 'topright']:
				new_height = start_h - dy
				if new_height >= MIN_WINDOW_HEIGHT and y + dy >= 0:
					y = start_y + dy
					h = new_height
			if self.resize_edge in ['bottom', 'bottomleft', 'bottomright']:
				new_height = start_h + dy
				if new_height >= MIN_WINDOW_HEIGHT and y + new_height <= screen_height:
					h = new_height
			
			# Ensure minimum size
			w = max(MIN_WINDOW_WIDTH, w)
			h = max(MIN_WINDOW_HEIGHT, h)
			
			# Update window
			win32gui.SetWindowPos(self.hwnd, 0, x, y, w, h, 0)
			self.width = w
			self.height = h
			try:
				pygame.display.set_mode((w, h), pygame.NOFRAME)
			except pygame.error as e:
				print(f"[easy_custom_titlebar] Warning: Failed to resize display: {e}")
		except Exception as e:
			print(f"[easy_custom_titlebar] Warning: Resize failed: {e}")

	def maximize_window(self) -> None:
		"""Maximize or restore the window."""
		if not self.hwnd:
			return
		
		try:
			if not self.is_maximized:
				rect = win32gui.GetWindowRect(self.hwnd)
				if rect:
					self.original_size = (rect[2] - rect[0], rect[3] - rect[1])
					self.original_pos = (rect[0], rect[1])
				x, y = 0, 0
				w = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
				h = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
				win32gui.SetWindowPos(self.hwnd, win32con.HWND_TOP, x, y, w, h, win32con.SWP_SHOWWINDOW)
				self.width = w
				self.height = h
				try:
					pygame.display.set_mode((w, h), pygame.NOFRAME)
				except pygame.error as e:
					print(f"[easy_custom_titlebar] Warning: Failed to maximize display: {e}")
			else:
				win32gui.SetWindowPos(
					self.hwnd, win32con.HWND_TOP,
					self.original_pos[0], self.original_pos[1],
					self.original_size[0], self.original_size[1],
					win32con.SWP_SHOWWINDOW
				)
				self.width = self.original_size[0]
				self.height = self.original_size[1]
				try:
					pygame.display.set_mode(self.original_size, pygame.NOFRAME)
				except pygame.error as e:
					print(f"[easy_custom_titlebar] Warning: Failed to restore display: {e}")
			self.is_maximized = not self.is_maximized
		except Exception as e:
			print(f"[easy_custom_titlebar] Warning: Maximize/restore failed: {e}")

	def minimize_window(self) -> None:
		"""Minimize the window."""
		if self.hwnd:
			try:
				win32gui.ShowWindow(self.hwnd, win32con.SW_MINIMIZE)
			except Exception as e:
				print(f"[easy_custom_titlebar] Warning: Minimize failed: {e}")

	def close_window(self) -> None:
		"""Close the window and clean up resources."""
		self.running = False
		if self.hwnd:
			try:
				win32gui.DestroyWindow(self.hwnd)
			except Exception:
				pass

	def get_button_rects(self, window_width: int, x_offset: int = 0) -> Tuple[List[pygame.Rect], pygame.Rect, pygame.Rect, pygame.Rect]:
		"""
		Calculate button rectangle positions.
		
		Args:
			window_width: Width of the window area
			x_offset: Horizontal offset for buttons
			
		Returns:
			Tuple of (custom_rects, min_rect, max_rect, close_rect)
		"""
		top_y = 0
		window_width = max(BUTTON_WIDTH * 3, int(window_width))
		x_offset = int(x_offset)
		
		# Standard buttons (always locked to the right)
		close_x = window_width - BUTTON_WIDTH
		close_rect = pygame.Rect(close_x + x_offset, top_y, BUTTON_WIDTH, self.titlebar_height)
		
		max_x = close_x - PADDING - BUTTON_WIDTH
		max_rect = pygame.Rect(max_x + x_offset, top_y, BUTTON_WIDTH, self.titlebar_height)
		
		min_x = max_x - PADDING - BUTTON_WIDTH
		min_rect = pygame.Rect(min_x + x_offset, top_y, BUTTON_WIDTH, self.titlebar_height)
		
		# Custom buttons
		custom_rects = []
		packed_index = 0
		for btn in self.custom_buttons:
			if not isinstance(btn, dict):
				continue
			if 'left' in btn and btn['left'] is not None:
				try:
					custom_x = x_offset + int(btn['left'])
				except (ValueError, TypeError):
					custom_x = min_x - (packed_index + 1) * (BUTTON_WIDTH + PADDING) + x_offset
					packed_index += 1
			else:
				custom_x = min_x - (packed_index + 1) * (BUTTON_WIDTH + PADDING) + x_offset
				packed_index += 1
			custom_rects.append(pygame.Rect(custom_x, top_y, BUTTON_WIDTH, self.titlebar_height))
		
		return custom_rects, min_rect, max_rect, close_rect

	def draw_titlebar(self) -> Tuple[List[pygame.Rect], pygame.Rect, pygame.Rect, pygame.Rect]:
		"""
		Draw the titlebar and all buttons.
		
		Returns:
			Tuple of (custom_rects, min_rect, max_rect, close_rect)
		"""
		try:
			w, h = self.screen.get_size()
		except (AttributeError, pygame.error):
			return [], pygame.Rect(0, 0, 0, 0), pygame.Rect(0, 0, 0, 0), pygame.Rect(0, 0, 0, 0)
		
		self.screen.fill(BG_COLOR)
		
		# Draw left notch (transparent or BG_COLOR)
		if self.left_notch_width > 0:
			pygame.draw.rect(self.screen, BG_COLOR, (0, 0, self.left_notch_width, self.titlebar_height))
			pygame.draw.rect(
				self.screen, self.titlebar_color,
				(self.left_notch_width, 0, w - self.left_notch_width, self.titlebar_height)
			)
			custom_rects, min_rect, max_rect, close_rect = self.get_button_rects(
				w - self.left_notch_width, x_offset=self.left_notch_width
			)
		else:
			pygame.draw.rect(self.screen, self.titlebar_color, (0, 0, w, self.titlebar_height))
			custom_rects, min_rect, max_rect, close_rect = self.get_button_rects(w)
		
		# Draw title text
		try:
			title_surf = self.HEADER_FONT.render(self.title, True, TITLE_CLIENT_TEXT)
			title_y = self.titlebar_height // 2 - title_surf.get_height() // 2 + TITLE_Y_OFFSET
			title_x = PADDING * 2 + self.left_notch_width
			# Ensure title doesn't overlap buttons
			max_title_width = close_rect.x - title_x - PADDING
			if title_surf.get_width() > max_title_width:
				# Truncate title if too long
				title_surf = self.HEADER_FONT.render(
					self.title[:max(0, int(len(self.title) * max_title_width / title_surf.get_width()))] + "...",
					True, TITLE_CLIENT_TEXT
				)
			self.screen.blit(title_surf, (title_x, title_y))
		except Exception as e:
			print(f"[easy_custom_titlebar] Warning: Failed to render title: {e}")
		
		mouse_pos = pygame.mouse.get_pos()
		mouse_pressed = pygame.mouse.get_pressed()[0] if pygame.mouse.get_pressed() else False
		
		def btn_bg(rect: pygame.Rect, kind: str) -> Tuple[int, int, int]:
			"""Get button background color based on state."""
			if not rect.collidepoint(mouse_pos):
				return self.button_color if kind != 'close' else self.button_color
			
			if kind == 'close':
				return self.close_button_hover_color if not mouse_pressed else self.close_button_color
			elif kind == 'custom':
				return self.button_hover_color
			else:
				return (80, 80, 80) if mouse_pressed else self.minmax_button_hover_color
		
		icon_sizes = {
			'minimize': 12,
			'maximize': 8,
			'restore': 12,
			'close': 13,
			'custom': 18
		}
		icon_color = self.button_icon_color
		
		# Draw custom buttons
		for i, rect in enumerate(custom_rects):
			if i >= len(self.custom_buttons):
				continue
			pygame.draw.rect(self.screen, btn_bg(rect, 'custom'), rect)
			btn = self.custom_buttons[i]
			if 'icon' in btn and btn['icon']:
				try:
					if os.path.exists(btn['icon']):
						icon_img = pygame.image.load(btn['icon']).convert_alpha()
						icon_img = pygame.transform.smoothscale(
							icon_img, (icon_sizes['custom'], icon_sizes['custom'])
						)
						icon_rect = icon_img.get_rect(center=rect.center)
						self.screen.blit(icon_img, icon_rect)
				except Exception as e:
					pass
			elif 'label' in btn and btn['label']:
				try:
					font = pygame.font.SysFont(self.titlebar_font_family, 18, bold=True)
					label_surf = font.render(str(btn['label']), True, (255, 255, 255))
					label_rect = label_surf.get_rect(center=rect.center)
					self.screen.blit(label_surf, label_rect)
				except Exception:
					pass
		
		# Draw standard buttons
		try:
			# Minimize button
			pygame.draw.rect(self.screen, btn_bg(min_rect, 'minimize'), min_rect)
			min_img = self.btn_imgs.get(f'minimize_{icon_color}')
			if min_img:
				min_icon = pygame.transform.smoothscale(
					min_img, (icon_sizes['minimize'], icon_sizes['minimize'])
				)
				min_icon_rect = min_icon.get_rect(center=min_rect.center)
				self.screen.blit(min_icon, min_icon_rect)
			
			# Maximize/Restore button
			pygame.draw.rect(self.screen, btn_bg(max_rect, 'maximize'), max_rect)
			if not self.is_maximized:
				max_img = self.btn_imgs.get(f'maximize_{icon_color}')
				icon_key = 'maximize'
			else:
				max_img = self.btn_imgs.get(f'restore_{icon_color}')
				icon_key = 'restore'
			
			if max_img:
				max_icon = pygame.transform.smoothscale(
					max_img, (icon_sizes[icon_key], icon_sizes[icon_key])
				)
				max_icon_rect = max_icon.get_rect(center=max_rect.center)
				self.screen.blit(max_icon, max_icon_rect)
			
			# Close button
			pygame.draw.rect(self.screen, btn_bg(close_rect, 'close'), close_rect)
			close_img = self.btn_imgs.get(f'close_{icon_color}')
			if close_img:
				close_icon = pygame.transform.smoothscale(
					close_img, (icon_sizes['close'], icon_sizes['close'])
				)
				close_icon_rect = close_icon.get_rect(center=close_rect.center)
				self.screen.blit(close_icon, close_icon_rect)
		except Exception as e:
			print(f"[easy_custom_titlebar] Warning: Failed to draw buttons: {e}")
		
		# Draw border if enabled
		if self.titlebar_border:
			try:
				pygame.draw.line(
					self.screen, self.titlebar_border_color,
					(0, self.titlebar_height - 1), (w, self.titlebar_height - 1),
					self.titlebar_border_thickness
				)
			except Exception:
				pass
		
		return custom_rects, min_rect, max_rect, close_rect

	def run(self, draw_content: Optional[Callable] = None) -> None:
		"""
		Run the main window loop.
		
		Args:
			draw_content: Optional function to draw content below titlebar.
				Should accept (screen, width, height, scroll_y) parameters.
		"""
		clock = pygame.time.Clock()
		scroll_step = 10.0  # Pixels per scroll step
		
		try:
			while self.running:
				try:
					w, h = self.screen.get_size()
				except (AttributeError, pygame.error):
					break
				
				# Draw titlebar
				custom_rects, min_btn, max_btn, close_btn = self.draw_titlebar()
				
				# Draw user content
				if draw_content and callable(draw_content):
					try:
						draw_content(self.screen, w, h, self.scroll_y)
					except Exception as e:
						print(f"[easy_custom_titlebar] Error in draw_content: {e}")
				
				pygame.display.flip()
				
				# Handle events
				for event in pygame.event.get():
					if event.type == pygame.QUIT:
						self.running = False
						break
					
					# Handle window controls (drag, resize, etc.)
					if self.handle_event(event):
						continue
					
					# Handle button clicks
					if event.type == pygame.MOUSEBUTTONDOWN:
						if event.button == 1:
							try:
								mx, my = event.pos
								if close_btn.collidepoint(mx, my):
									self.close_window()
									break
								elif max_btn.collidepoint(mx, my):
									self.maximize_window()
								elif min_btn.collidepoint(mx, my):
									self.minimize_window()
							except Exception as e:
								print(f"[easy_custom_titlebar] Warning: Button click error: {e}")
					
					# Handle scrolling
					if self.enable_scroll:
						if event.type == pygame.MOUSEBUTTONDOWN:
							if event.button == 4:  # Scroll up
								self.scroll_y = max(0.0, self.scroll_y - scroll_step)
							elif event.button == 5:  # Scroll down
								self.scroll_y = self.scroll_y + scroll_step
						elif event.type == pygame.KEYDOWN:
							if event.key == pygame.K_UP:
								self.scroll_y = max(0.0, self.scroll_y - scroll_step)
							elif event.key == pygame.K_DOWN:
								self.scroll_y = self.scroll_y + scroll_step
				
				clock.tick(60)
		except KeyboardInterrupt:
			self.running = False
		except Exception as e:
			print(f"[easy_custom_titlebar] Fatal error in main loop: {e}")
			import traceback
			traceback.print_exc()
		finally:
			self._cleanup()
	
	def _cleanup(self) -> None:
		"""Clean up resources."""
		try:
			pygame.quit()
		except Exception:
			pass
		# Don't call sys.exit() here - let the caller handle it
