import pygame
import sys
import os
import win32gui
import win32con
import win32api
import win32ui
from ctypes import windll, create_unicode_buffer, sizeof, byref, c_int
import importlib.resources

TITLEBAR_HEIGHT = 40
BUTTON_WIDTH = 55
BUTTON_HEIGHT = TITLEBAR_HEIGHT
PADDING = 8
TITLE_Y_OFFSET = 5
BG_COLOR = (30, 30, 30)
TITLE_CLIENT_BG = (25, 25, 25)
TITLE_CLIENT_TEXT = (230, 230, 230)
BUTTON_HOVER_BG = (150, 150, 150)

# Helper to get resource path for package data

def resource_path(filename):
    try:
        with importlib.resources.path("easy_custom_titlebar.assets", filename) as p:
            return str(p)
    except Exception:
        return os.path.join(os.path.dirname(__file__), "assets", filename)

class CustomTitleBarWindow:
    def __init__(self, width=1200, height=700, title="", enable_scroll=False, titlebar_color=None, button_color=None, button_hover_color=None, button_icon_color="white", titlebar_border=False, titlebar_border_color=(0,0,0), titlebar_border_thickness=1, titlebar_font_family="Consolas", titlebar_font_size=28, titlebar_font_bold=True, left_notch_width=0, titlebar_height=40, close_button_color=(200,0,0), close_button_hover_color=(255,0,0), minmax_button_hover_color=None, window_icon=None, minimize_icon=None, maximize_icon=None, restore_icon=None, close_icon=None, custom_buttons=None):
        pygame.init()
        self.width = width
        self.height = height
        self.title = title
        self.enable_scroll = enable_scroll
        self.titlebar_border = titlebar_border
        self.titlebar_border_color = titlebar_border_color
        self.titlebar_border_thickness = titlebar_border_thickness
        self.titlebar_font_family = titlebar_font_family
        self.titlebar_font_size = titlebar_font_size
        self.titlebar_font_bold = titlebar_font_bold
        self.left_notch_width = left_notch_width
        self._titlebar_height = titlebar_height
        self.custom_buttons = custom_buttons or []
        # Set window/taskbar icon if provided
        if window_icon is not None:
            try:
                icon_surface = pygame.image.load(window_icon)
                pygame.display.set_icon(icon_surface)
            except Exception as e:
                print(f"[easy_custom_titlebar] Failed to set window icon: {e}")
        # Handle titlebar color (accept hex or tuple)
        if titlebar_color is None:
            self.titlebar_color = TITLE_CLIENT_BG
        elif isinstance(titlebar_color, str) and titlebar_color.startswith("#"):
            hex_color = titlebar_color.lstrip("#")
            self.titlebar_color = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        else:
            self.titlebar_color = titlebar_color
        # Handle button color
        if button_color is None:
            self.button_color = self.titlebar_color
        elif isinstance(button_color, str) and button_color.startswith("#"):
            hex_color = button_color.lstrip("#")
            self.button_color = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        else:
            self.button_color = button_color
        # Handle button hover color
        if button_hover_color is None:
            self.button_hover_color = BUTTON_HOVER_BG
        elif isinstance(button_hover_color, str) and button_hover_color.startswith("#"):
            hex_color = button_hover_color.lstrip("#")
            self.button_hover_color = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        else:
            self.button_hover_color = button_hover_color
        # Handle icon color
        self.button_icon_color = button_icon_color.lower() if button_icon_color else "white"
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.NOFRAME)
        pygame.display.set_caption(self.title)
        self.hwnd = win32gui.GetForegroundWindow()
        self._init_window_styles()
        self._center_window()
        self.dragging = False
        self.drag_offset = (0, 0)
        self.resizing = False
        self.resize_edge = None
        self.is_maximized = False
        self.original_size = (self.width, self.height)
        self.original_pos = (0, 0)
        self.RESIZE_BORDER = 5
        self.resize_start_size = None
        self.resize_start_pos = None
        self.resize_mouse_start = None
        self.scroll_y = 0.0
        self.scroll_speed = 0.0
        self.running = True
        self.FONT = pygame.font.SysFont("Consolas", 18)
        self.HEADER_FONT = pygame.font.SysFont(self.titlebar_font_family, self.titlebar_font_size, bold=self.titlebar_font_bold)
        # Load button images (allow custom overrides)
        from . import resource_path
        def load_icon(path, fallback):
            if path is not None:
                try:
                    return pygame.image.load(path).convert_alpha()
                except Exception as e:
                    print(f"[easy_custom_titlebar] Failed to load custom icon {path}: {e}")
            return pygame.image.load(resource_path(fallback)).convert_alpha()
        self.btn_imgs = {
            'minimize_white': load_icon(minimize_icon, 'minimize_white.png'),
            'maximize_white': load_icon(maximize_icon, 'maximize_white.png'),
            'restore_white': load_icon(restore_icon, 'restore_white.png'),
            'close_white': load_icon(close_icon, 'close_white.png'),
            'minimize_black': load_icon(minimize_icon, 'minimize_black.png'),
            'maximize_black': load_icon(maximize_icon, 'maximize_black.png'),
            'restore_black': load_icon(restore_icon, 'restore_black.png'),
            'close_black': load_icon(close_icon, 'close_black.png'),
        }
        self.close_button_color = close_button_color
        self.close_button_hover_color = close_button_hover_color
        self.minmax_button_hover_color = minmax_button_hover_color if minmax_button_hover_color is not None else BUTTON_HOVER_BG

    @property
    def titlebar_height(self):
        return self._titlebar_height

    def _init_window_styles(self):
        style = win32gui.GetWindowLong(self.hwnd, win32con.GWL_STYLE)
        style = style & ~win32con.WS_CAPTION & ~win32con.WS_THICKFRAME
        style = style | win32con.WS_MAXIMIZEBOX | win32con.WS_MINIMIZEBOX | win32con.WS_SYSMENU
        win32gui.SetWindowLong(self.hwnd, win32con.GWL_STYLE, style)
        ex_style = win32gui.GetWindowLong(self.hwnd, win32con.GWL_EXSTYLE)
        ex_style = ex_style | win32con.WS_EX_LAYERED
        win32gui.SetWindowLong(self.hwnd, win32con.GWL_EXSTYLE, ex_style)
        try:
            import ctypes
            from ctypes import wintypes
            DWMWA_WINDOW_CORNER_PREFERENCE = 33
            DWMWCP_ROUND = 2
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                wintypes.HWND(self.hwnd),
                DWMWA_WINDOW_CORNER_PREFERENCE,
                ctypes.byref(wintypes.INT(DWMWCP_ROUND)),
                ctypes.sizeof(wintypes.INT)
            )
        except:
            pass

    def _center_window(self):
        screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
        x = (screen_width - self.width) // 2
        y = (screen_height - self.height) // 2
        win32gui.SetWindowPos(self.hwnd, 0, x, y, self.width, self.height, 0)

    def set_title(self, title):
        self.title = title
        pygame.display.set_caption(self.title)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if self.is_resize_area(mouse_pos):
                    self.resizing = True
                    self.resize_edge = self.get_resize_edge(mouse_pos)
                    rect = win32gui.GetWindowRect(self.hwnd)
                    self.resize_start_size = (rect[2] - rect[0], rect[3] - rect[1])
                    self.resize_start_pos = (rect[0], rect[1])
                    self.resize_mouse_start = mouse_pos
                    return True
                w = self.screen.get_size()[0]
                if self.left_notch_width > 0:
                    custom_rects, min_rect, max_rect, close_rect = self.get_button_rects(w - self.left_notch_width, x_offset=self.left_notch_width)
                else:
                    custom_rects, min_rect, max_rect, close_rect = self.get_button_rects(w)
                if mouse_pos[1] < self.titlebar_height:
                    # Custom button clicks
                    for i, rect in enumerate(custom_rects):
                        if rect.collidepoint(mouse_pos):
                            btn = self.custom_buttons[i]
                            if 'callback' in btn and callable(btn['callback']):
                                btn['callback']()
                            return True
                    if not (min_rect.collidepoint(mouse_pos) or max_rect.collidepoint(mouse_pos) or close_rect.collidepoint(mouse_pos)):
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
        return False

    def update_cursor(self, pos):
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

    def is_resize_area(self, pos):
        x, y = pos
        w, h = self.screen.get_size()
        return (x < self.RESIZE_BORDER or x > w - self.RESIZE_BORDER or y < self.RESIZE_BORDER or y > h - self.RESIZE_BORDER)

    def get_resize_edge(self, pos):
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
        return None

    def handle_drag(self, pos):
        if not self.is_maximized:
            rect = win32gui.GetWindowRect(self.hwnd)
            x = rect[0] + (pos[0] - self.drag_offset[0])
            y = rect[1] + (pos[1] - self.drag_offset[1])
            win32gui.SetWindowPos(self.hwnd, 0, x, y, 0, 0, win32con.SWP_NOSIZE)

    def handle_resize(self, pos):
        if not self.is_maximized and self.resize_start_size and self.resize_start_pos and self.resize_mouse_start:
            start_x, start_y = self.resize_start_pos
            start_w, start_h = self.resize_start_size
            mouse_start_x, mouse_start_y = self.resize_mouse_start
            dx = pos[0] - mouse_start_x
            dy = pos[1] - mouse_start_y
            x, y = start_x, start_y
            w, h = start_w, start_h
            if self.resize_edge in ['left', 'topleft', 'bottomleft']:
                new_width = start_w - dx
                if new_width >= 400:
                    x = start_x + dx
                    w = new_width
            if self.resize_edge in ['right', 'topright', 'bottomright']:
                new_width = start_w + dx
                if new_width >= 400:
                    w = new_width
            if self.resize_edge in ['top', 'topleft', 'topright']:
                new_height = start_h - dy
                if new_height >= 300:
                    y = start_y + dy
                    h = new_height
            if self.resize_edge in ['bottom', 'bottomleft', 'bottomright']:
                new_height = start_h + dy
                if new_height >= 300:
                    h = new_height
            win32gui.SetWindowPos(self.hwnd, 0, x, y, w, h, 0)
            pygame.display.set_mode((w, h), pygame.NOFRAME)

    def maximize_window(self):
        if not self.is_maximized:
            rect = win32gui.GetWindowRect(self.hwnd)
            self.original_size = (rect[2] - rect[0], rect[3] - rect[1])
            self.original_pos = (rect[0], rect[1])
            x, y = 0, 0
            w = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
            h = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
            win32gui.SetWindowPos(self.hwnd, win32con.HWND_TOP, x, y, w, h, win32con.SWP_SHOWWINDOW)
            pygame.display.set_mode((w, h), pygame.NOFRAME)
        else:
            win32gui.SetWindowPos(self.hwnd, win32con.HWND_TOP, self.original_pos[0], self.original_pos[1], self.original_size[0], self.original_size[1], win32con.SWP_SHOWWINDOW)
            pygame.display.set_mode(self.original_size, pygame.NOFRAME)
        self.is_maximized = not self.is_maximized

    def minimize_window(self):
        win32gui.ShowWindow(self.hwnd, win32con.SW_MINIMIZE)

    def close_window(self):
        win32gui.DestroyWindow(self.hwnd)
        self.running = False

    def get_button_rects(self, window_width, x_offset=0):
        top_y = 0
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
            if 'left' in btn and btn['left'] is not None:
                custom_x = x_offset + int(btn['left'])
            else:
                custom_x = min_x - (packed_index + 1) * (BUTTON_WIDTH + PADDING) + x_offset
                packed_index += 1
            custom_rects.append(pygame.Rect(custom_x, top_y, BUTTON_WIDTH, self.titlebar_height))
        return custom_rects, min_rect, max_rect, close_rect

    def draw_titlebar(self):
        w, h = self.screen.get_size()
        self.screen.fill(BG_COLOR)
        # Draw left notch (transparent or BG_COLOR)
        if self.left_notch_width > 0:
            pygame.draw.rect(self.screen, BG_COLOR, (0, 0, self.left_notch_width, self.titlebar_height))
            pygame.draw.rect(self.screen, self.titlebar_color, (self.left_notch_width, 0, w-self.left_notch_width, self.titlebar_height))
            custom_rects, min_rect, max_rect, close_rect = self.get_button_rects(w - self.left_notch_width, x_offset=self.left_notch_width)
        else:
            pygame.draw.rect(self.screen, self.titlebar_color, (0, 0, w, self.titlebar_height))
            custom_rects, min_rect, max_rect, close_rect = self.get_button_rects(w)
        title_surf = self.HEADER_FONT.render(self.title, True, TITLE_CLIENT_TEXT)
        title_y = self.titlebar_height // 2 - title_surf.get_height() // 2 + TITLE_Y_OFFSET
        title_x = PADDING * 2 + self.left_notch_width
        self.screen.blit(title_surf, (title_x, title_y))
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        def btn_bg(rect, kind):
            if kind == 'close':
                if rect.collidepoint(mouse_pos):
                    return self.close_button_hover_color if not mouse_pressed else self.close_button_color
                else:
                    return self.button_color
            elif kind == 'custom':
                if rect.collidepoint(mouse_pos):
                    return self.button_hover_color
                else:
                    return self.button_color
            else:
                if rect.collidepoint(mouse_pos):
                    return (80, 80, 80) if mouse_pressed else self.minmax_button_hover_color
                else:
                    return self.button_color
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
            pygame.draw.rect(self.screen, btn_bg(rect, 'custom'), rect)
            btn = self.custom_buttons[i]
            if 'icon' in btn and btn['icon']:
                try:
                    icon_img = pygame.image.load(btn['icon']).convert_alpha()
                    icon_img = pygame.transform.smoothscale(icon_img, (icon_sizes['custom'], icon_sizes['custom']))
                    icon_rect = icon_img.get_rect(center=rect.center)
                    self.screen.blit(icon_img, icon_rect)
                except Exception as e:
                    pass
            elif 'label' in btn and btn['label']:
                font = pygame.font.SysFont(self.titlebar_font_family, 18, bold=True)
                label_surf = font.render(btn['label'], True, (255,255,255))
                label_rect = label_surf.get_rect(center=rect.center)
                self.screen.blit(label_surf, label_rect)
        # Draw standard buttons
        pygame.draw.rect(self.screen, btn_bg(min_rect, 'minimize'), min_rect)
        min_img = self.btn_imgs[f'minimize_{icon_color}']
        min_icon = pygame.transform.smoothscale(min_img, (icon_sizes['minimize'], icon_sizes['minimize']))
        min_icon_rect = min_icon.get_rect(center=min_rect.center)
        self.screen.blit(min_icon, min_icon_rect)
        pygame.draw.rect(self.screen, btn_bg(max_rect, 'maximize'), max_rect)
        if not self.is_maximized:
            max_img = self.btn_imgs[f'maximize_{icon_color}']
            max_icon = pygame.transform.smoothscale(max_img, (icon_sizes['maximize'], icon_sizes['maximize']))
        else:
            max_img = self.btn_imgs[f'restore_{icon_color}']
            max_icon = pygame.transform.smoothscale(max_img, (icon_sizes['restore'], icon_sizes['restore']))
        max_icon_rect = max_icon.get_rect(center=max_rect.center)
        self.screen.blit(max_icon, max_icon_rect)
        pygame.draw.rect(self.screen, btn_bg(close_rect, 'close'), close_rect)
        close_img = self.btn_imgs[f'close_{icon_color}']
        close_icon = pygame.transform.smoothscale(close_img, (icon_sizes['close'], icon_sizes['close']))
        close_icon_rect = close_icon.get_rect(center=close_rect.center)
        self.screen.blit(close_icon, close_icon_rect)
        if self.titlebar_border:
            pygame.draw.line(self.screen, self.titlebar_border_color, (0, self.titlebar_height-1), (w, self.titlebar_height-1), self.titlebar_border_thickness)
        return custom_rects, min_rect, max_rect, close_rect

    def run(self, draw_content=None):
        clock = pygame.time.Clock()
        while self.running:
            w, h = self.screen.get_size()
            custom_rects, min_btn, max_btn, close_btn = self.draw_titlebar()
            if draw_content:
                draw_content(self.screen, w, h, self.scroll_y)
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if self.handle_event(event):
                    continue
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mx, my = event.pos
                        if close_btn.collidepoint(mx, my):
                            self.close_window()
                        elif max_btn.collidepoint(mx, my):
                            self.maximize_window()
                        elif min_btn.collidepoint(mx, my):
                            self.minimize_window()
                if self.enable_scroll:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 4:
                            self.scroll_y = max(0, self.scroll_y - 1)
                        elif event.button == 5:
                            self.scroll_y = self.scroll_y + 1
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP:
                            self.scroll_y = max(0, self.scroll_y - 1)
                        elif event.key == pygame.K_DOWN:
                            self.scroll_y = self.scroll_y + 1
            clock.tick(60)
        pygame.quit()
        sys.exit()
