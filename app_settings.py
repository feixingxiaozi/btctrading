
import json
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button


CONFIG_FILE = "api_config.json"

def save_api_config(api_key, secret_key, passphrase):
    config = {
        "api_key": api_key,
        "secret_key": secret_key,
        "passphrase": passphrase
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

def load_api_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {"api_key": "", "secret_key": "", "passphrase": ""}


class APISettingsLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(APISettingsLayout, self).__init__(orientation="vertical", **kwargs)
        self.config = load_api_config()

        self.api_key_input = TextInput(text=self.config.get("api_key", ""), hint_text="API Key", multiline=False)
        self.secret_key_input = TextInput(text=self.config.get("secret_key", ""), hint_text="Secret Key", multiline=False)
        self.passphrase_input = TextInput(text=self.config.get("passphrase", ""), hint_text="Passphrase", multiline=False)

        self.save_button = Button(text="保存设置", size_hint=(1, 0.2))
        self.save_button.bind(on_press=self.save_settings)

        self.add_widget(Label(text="设置 Bitget API", size_hint=(1, 0.2)))
        self.add_widget(self.api_key_input)
        self.add_widget(self.secret_key_input)
        self.add_widget(self.passphrase_input)
        self.add_widget(self.save_button)

    def save_settings(self, instance):
        save_api_config(
            self.api_key_input.text,
            self.secret_key_input.text,
            self.passphrase_input.text
        )

        from kivy.clock import Clock
        from kivy.uix.popup import Popup

        popup = Popup(
            title="保存成功",
            content=Label(text="✅ API 信息已保存"),
            size_hint=(0.6, 0.3)
        )
        popup.open()

        def close_and_exit(dt):
            popup.dismiss()
            App.get_running_app().stop()

        Clock.schedule_once(close_and_exit, 2)


class APISettingsApp(App):
    def build(self):
        return APISettingsLayout()


if __name__ == "__main__":
    APISettingsApp().run()
