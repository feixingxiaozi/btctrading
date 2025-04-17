import json
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.dropdown import DropDown

from app_settings import load_api_config
from BitgetAPI import BitgetAPI
from strategy_executor import place_strategy_orders


class StrategyUI(BoxLayout):
    def __init__(self, **kwargs):
        super(StrategyUI, self).__init__(orientation="vertical", padding=10, spacing=10, **kwargs)

        # 输入区
        input_box = BoxLayout(orientation="horizontal", size_hint=(1, 0.1), spacing=10)
        self.price_a_input = TextInput(hint_text="A 点价格", multiline=False, input_filter="float", size_hint=(0.3, 1))
        self.price_b_input = TextInput(hint_text="B 点价格", multiline=False, input_filter="float", size_hint=(0.3, 1))
        self.capital_input = TextInput(hint_text="本金 USDT", multiline=False, input_filter="float", size_hint=(0.3, 1))
        input_box.add_widget(self.price_a_input)
        input_box.add_widget(self.price_b_input)
        input_box.add_widget(self.capital_input)

        # 按钮
        self.execute_button = Button(text="开始挂单", size_hint=(1, 0.1))
        self.execute_button.bind(on_press=self.execute_strategy)

        self.api_button = Button(text="⚙️ API 设置", size_hint=(1, 0.1))
        self.api_button.bind(on_press=self.go_back_to_settings)

        # 日志显示区域
        self.output_label = Label(size_hint_y=None, height=500, text="", valign="top")
        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(self.output_label)

        # 布局组合
        self.add_widget(Label(text="📈 自动挂单策略界面", size_hint=(1, 0.1)))
        self.add_widget(input_box)
        self.add_widget(self.execute_button)
        self.add_widget(self.api_button)
        self.add_widget(scroll)

    def execute_strategy(self, instance):
        try:
            a = float(self.price_a_input.text)
            b = float(self.price_b_input.text)
            capital = float(self.capital_input.text)
        except ValueError:
            self.show_popup("输入错误", "请确保 A/B 点和本金都是数字")
            return

        try:
            cfg = load_api_config()
            api = BitgetAPI(cfg["api_key"], cfg["secret_key"], cfg["passphrase"])
            result = place_strategy_orders(api, a, b, capital)

            ts_a = result.get("timestamp_A", "未知")
            ts_b = result.get("timestamp_B", "未知")
            direction = result.get("direction")
            current = result.get("current_price")
            entries = result.get("entry_prices", [])
            qtys = result.get("qtys", [])
            stops = result.get("stop_loss", [])

            # 格式化每一个挂单信息
            order_details = "\n".join([
                f"👉 单{idx+1}：价格 {entries[idx]}，止损 {stops[idx]}，仓位 {qtys[idx]}"
                for idx in range(len(entries))
            ])

            info_text = (
                f"[A点时间] {ts_a}\n"
                f"[B点时间] {ts_b}\n"
                f"[当前价格] {current}\n"
                f"[方向] {'做多' if direction == 'long' else '做空'}\n\n"
                f"{order_details}"
            )

            self.output_label.text = info_text
        except Exception as e:
            self.output_label.text = f"❌ 执行出错: {str(e)}"

    def show_popup(self, title, message):
        popup = Popup(
            title=title,
            content=Label(text=message),
            size_hint=(0.7, 0.3)
        )
        popup.open()

    def go_back_to_settings(self, instance):
        from app_settings import APISettingsApp
        App.get_running_app().stop()
        APISettingsApp().run()


class StrategyApp(App):
    def build(self):
        return StrategyUI()


if __name__ == "__main__":
    StrategyApp().run()