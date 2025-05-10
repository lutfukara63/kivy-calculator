from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.animation import Animation
from kivy.properties import NumericProperty, ListProperty, StringProperty
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
import random
from sympy import sympify, sin, cos, tan, pi, rad
import re

class AnimatedButton(Button):
    scale = NumericProperty(1)
    bg_color = ListProperty(get_color_from_hex('#2E2E2E'))
    text_color = ListProperty(get_color_from_hex('#FFFFFF'))
    radius = ListProperty([15]*4)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = [0,0,0,0]
        self.font_size = 24
        self.bold = True
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.bg_color)
            RoundedRectangle(pos=self.pos, size=self.size, radius=self.radius)
            
    def on_press(self):
        Animation.cancel_all(self)
        anim = Animation(scale=0.95, duration=0.1, t='out_quad') + Animation(scale=1, duration=0.1, t='out_elastic')
        anim.start(self)

    def on_scale(self, instance, value):
        self.scale_x = value
        self.scale_y = value

class GradientBackground(BoxLayout):
    color1 = ListProperty(get_color_from_hex('#1a1a1a'))
    color2 = ListProperty(get_color_from_hex('#2d2d2d'))
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.update, size=self.update)
        
    def update(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.color1)
            Rectangle(pos=self.pos, size=self.size)
            Color(*self.color2)
            Rectangle(pos=(self.pos[0], self.pos[1]+self.height/2), size=(self.size[0], self.size[1]/2))

class CalculatorApp(App):
    result_text = StringProperty('Sonuç: ')
    
    def build(self):
        self.history = []
        self.themes = [
            {'name': 'Gece', 'primary': '#1A1A2E', 'secondary': '#16213E', 'accent': '#E94560', 'text': '#FFFFFF', 'close': '#E94560'},
            {'name': 'Okyanus', 'primary': '#0A3D62', 'secondary': '#1E88E5', 'accent': '#FFD166', 'text': '#E6F1FA', 'close': '#EF5350'},
            {'name': 'Gün Batımı', 'primary': '#FF6F61', 'secondary': '#FFB88C', 'accent': '#2D3047', 'text': '#2D3047', 'close': '#2D3047'},
            {'name': 'Orman', 'primary': '#2E8B57', 'secondary': '#3CB371', 'accent': '#A9DFBF', 'text': '#F0FFF0', 'close': '#C0392B'},
            {'name': 'Lavanta', 'primary': '#6C3483', 'secondary': '#BB8FCE', 'accent': '#F9E79F', 'text': '#FDEBD0', 'close': '#922B21'},
            {'name': 'Gökyüzü', 'primary': '#3498DB', 'secondary': '#85C1E9', 'accent': '#F7DC6F', 'text': '#EBF5FB', 'close': '#E74C3C'},
            {'name': 'Kum Fırtınası', 'primary': '#C19A6B', 'secondary': '#F4D03F', 'accent': '#6E2C00', 'text': '#FDF2E9', 'close': '#922B21'},
            {'name': 'Karpuz', 'primary': '#FF3B3F', 'secondary': '#75B79E', 'accent': '#A8D8EA', 'text': '#FFF0F5', 'close': '#8B0000'},
            {'name': 'Gece Gökyüzü', 'primary': '#0D1B2A', 'secondary': '#1B263B', 'accent': '#E0E1DD', 'text': '#F5F5F5', 'close': '#FF6B6B'},
            {'name': 'Pastel Rüyası', 'primary': '#FADCD9', 'secondary': '#D6EADF', 'accent': '#FFB7B2', 'text': '#5C5470', 'close': '#EF476F'}
        ]
        
        self.current_theme = 0
        
        self.root = GradientBackground(orientation='vertical', padding=15, spacing=15)
        
        # Geliştirici bilgisi etiketi
        developer_label = Label(
            text='Geliştirici: Lütfü Karakeçili 2025',
            font_size=16,
            color=get_color_from_hex(self.themes[0]['text']),
            size_hint=(1, 0.05),
            pos_hint={'top': 1}
        )
        self.root.add_widget(developer_label)
        
        self.input_box = TextInput(
            text='', 
            multiline=False, 
            font_size=32,
            background_normal='',
            background_color=get_color_from_hex(self.themes[0]['primary']),
            foreground_color=get_color_from_hex(self.themes[0]['text']),
            padding=20,
            cursor_color=get_color_from_hex(self.themes[0]['accent']),
            cursor_width=3,
            size_hint=(1, 0.2))
        self.root.add_widget(self.input_box)
        
        self.result_label = Label(
            text='Sonuç: ', 
            font_size=28,
            color=get_color_from_hex(self.themes[0]['accent']),
            bold=True,
            size_hint=(1, 0.1),
            opacity=0)
        self.root.add_widget(self.result_label)
        
        self.keyboard = GridLayout(cols=5, rows=6, spacing=10, size_hint=(1, 0.6))
        buttons = [
            ('7', 'secondary'), ('8', 'secondary'), ('9', 'secondary'), ('/', 'accent'), ('C', 'close'),
            ('4', 'secondary'), ('5', 'secondary'), ('6', 'secondary'), ('*', 'accent'), ('sin', 'secondary'),
            ('1', 'secondary'), ('2', 'secondary'), ('3', 'secondary'), ('-', 'accent'), ('cos', 'secondary'),
            ('0', 'secondary'), ('.', 'secondary'), ('=', 'secondary'), ('+', 'accent'), ('tan', 'secondary'),
            ('(', 'secondary'), (')', 'secondary'), ('π', 'secondary'), ('◄', 'secondary'), ('Geçmiş', 'secondary'),
            ('Temalar', 'secondary')
        ]
        
        for text, btn_type in buttons:
            btn = AnimatedButton(text=text)
            btn.bg_color = get_color_from_hex(self.themes[0][btn_type])
            btn.text_color = get_color_from_hex(self.themes[0]['text'])
            btn.bind(on_press=self.button_handler)
            self.keyboard.add_widget(btn)
        
        self.root.add_widget(self.keyboard)
        
        self.particle_pos = []
        for _ in range(20):
            self.particle_pos.append((
                Window.width * 0.2 + Window.width * 0.6 * random.random(),
                Window.height * 0.2 + Window.height * 0.6 * random.random(),
                random.uniform(0.5, 2)
            ))
        
        Clock.schedule_once(self.animate_particles, 0)
        Window.bind(on_keyboard=self.on_keyboard)
        return self.root

    def on_keyboard(self, window, key, *args):
        if key == 27:  # Geri tuşu
            return True
        return False

    def animate_particles(self, dt):
        for i in range(len(self.particle_pos)):
            x, y, speed = self.particle_pos[i]
            new_y = y - 2 * speed
            if new_y < 0:
                new_y = Window.height
            self.particle_pos[i] = (x, new_y, speed)
        
        self.root.canvas.after.clear()
        with self.root.canvas.after:
            for x, y, size in self.particle_pos:
                Color(rgba=(1, 1, 1, 0.05))
                Rectangle(pos=(x, y), size=(size, size))
        
        Clock.schedule_once(self.animate_particles, 0.1)

    def button_handler(self, instance):
        {
            'C': self.clear_input,
            '=': self.calculate,
            '◄': self.backspace,
            'Kapat': self.close_app,
            'sin': lambda x: self.add_function('sin('),
            'cos': lambda x: self.add_function('cos('),
            'tan': lambda x: self.add_function('tan('),
            'π': lambda x: self.input_box.insert_text('π'),
            'Geçmiş': self.show_history,
            'Temalar': self.switch_theme
        }.get(instance.text, self.add_to_input)(instance)

    def add_to_input(self, instance):
        self.input_box.insert_text(instance.text)
        self.animate_text_input()

    def add_function(self, func):
        self.input_box.insert_text(func)
        self.animate_text_input()

    def backspace(self, instance):
        self.input_box.text = self.input_box.text[:-1]
        self.animate_text_input()

    def clear_input(self, instance):
        self.input_box.text = ''
        self.result_label.opacity = 0
        self.animate_text_input()

    def calculate(self, instance):
        try:
            expression = self.input_box.text.strip()
            if not expression:
                return
                
            expression = expression.replace('π', str(pi))
            safe_expr = re.sub(r'sin\((.*?)\)', r'sin(rad(\1))', expression)
            safe_expr = re.sub(r'cos\((.*?)\)', r'cos(rad(\1))', safe_expr)
            safe_expr = re.sub(r'tan\((.*?)\)', r'tan(rad(\1))', safe_expr)
            
            result = sympify(safe_expr, evaluate=True)
            result = float(result) if result.is_real else result
            result_str = f"{result:.6f}" if isinstance(result, float) else str(result)
            self.history.append(f"{expression} = {result_str}")
            self.show_result(result_str)
        except Exception as e:
            self.show_result("Hatalı İfade!", error=True)

    def show_result(self, text, error=False):
        self.result_label.color = get_color_from_hex('#FF5555' if error else self.themes[self.current_theme]['accent'])
        self.result_label.text = text
        anim = Animation(opacity=1, y=self.result_label.y + 20, duration=0.3, t='out_quad') 
        anim += Animation(opacity=1, y=self.result_label.y, duration=0.2, t='out_elastic')
        anim.start(self.result_label)

    def show_history(self, instance):
        if not self.history:
            self.show_result("Geçmiş boş!", error=True)
        else:
            history_text = "\n".join(self.history[-5:])
            self.result_label.color = get_color_from_hex(self.themes[self.current_theme]['accent'])
            self.result_label.text = history_text
            anim = Animation(opacity=1, y=self.result_label.y + 20, duration=0.3, t='out_quad')
            anim.start(self.result_label)

    def switch_theme(self, instance):
        self.current_theme = (self.current_theme + 1) % len(self.themes)
        theme = self.themes[self.current_theme]
        
        self.root.color1 = get_color_from_hex(theme['primary'])
        self.root.color2 = get_color_from_hex(theme['secondary'])
        self.input_box.background_color = get_color_from_hex(theme['primary'])
        self.input_box.foreground_color = get_color_from_hex(theme['text'])
        self.input_box.cursor_color = get_color_from_hex(theme['accent'])
        self.result_label.color = get_color_from_hex(theme['accent'])
        
        for btn in self.keyboard.children:
            if btn.text in ['7', '8', '9', '4', '5', '6', '1', '2', '3', '0', '.', '=', 'sin', 'cos', 'tan', '(', ')', 'π', '◄', 'Geçmiş', 'Temalar']:
                btn.bg_color = get_color_from_hex(theme['secondary'])
            elif btn.text in ['/', '*', '-', '+']:
                btn.bg_color = get_color_from_hex(theme['accent'])
            elif btn.text in ['C', 'Kapat']:
                btn.bg_color = get_color_from_hex(theme['close'])
            btn.text_color = get_color_from_hex(theme['text'])
        
        self.show_result(f"{theme['name']} Teması", error=False)

    def animate_text_input(self):
        anim = Animation(font_size=34, duration=0.1) + Animation(font_size=32, duration=0.1)
        anim.start(self.input_box)

    def close_app(self, instance):
        Animation.stop_all(self.root)
        anim = Animation(opacity=0, duration=0.3, t='out_quad')
        anim.bind(on_complete=lambda *x: App.get_running_app().stop())
        anim.start(self.root)

if __name__ == '__main__':
    from kivy.config import Config
    Config.set('graphics', 'width', '400')
    Config.set('graphics', 'height', '600')
    CalculatorApp().run()