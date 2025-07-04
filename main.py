from kivymd.app import MDApp
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from timer_screen import TimerScreen

class ProductivityApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "DeepPurple"
        self.theme_cls.theme_style = "Light"
        
        # Create bottom navigation
        bottom_nav = MDBottomNavigation()
        
        # Timer Screen
        timer_screen = MDBottomNavigationItem(
            name='timer',
            text='Timer',
            icon='timer'
        )
        timer_screen.add_widget(TimerScreen())
        
        # Stats Screen
        stats_screen = MDBottomNavigationItem(
            name='stats',
            text='Stats',
            icon='chart-line'
        )
        stats_label = MDLabel(
            text='Statistics Coming Soon',
            halign='center'
        )
        stats_screen.add_widget(stats_label)
        
        # Add screens to navigation
        bottom_nav.add_widget(timer_screen)
        bottom_nav.add_widget(stats_screen)
        
        return bottom_nav

if __name__ == '__main__':
    ProductivityApp().run() 