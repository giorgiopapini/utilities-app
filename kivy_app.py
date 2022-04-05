from kivymd.app import MDApp
from kivy.lang import Builder
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDFlatButton, MDRectangleFlatButton, MDRoundFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.bottomsheet import MDGridBottomSheet
from kivymd.uix.snackbar import Snackbar
from kivymd import toast
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.image import Image
from kivy.properties import ObjectProperty
from kivy.app import platform
from PIL import Image, ImageOps, ImageDraw
import instagram_explore as ie
import urllib.request
import deezer
import os

class MyApp(MDApp):

    src_manager = ObjectProperty(None)

    dialog = None   

    def show_alert(self):
        if not self.dialog:
            self.dialog = MDDialog(
                text="Questa sezione è in fase di sviluppo",
                radius=[20, 7, 20, 7],
                size_hint= (0.8, 0.8),
                pos_hint = {"center_x": 0.5, "center_y": 0.5},
                buttons = [
                    MDRaisedButton(
                        text = "OK", text_color = self.theme_cls.primary_color, on_release = self.close_alert
                    ),
                ],
            )

        self.dialog.open()

    def close_alert(self, instance):
        self.dialog.dismiss()

    def theme_callback(self):
        self.change_theme_color()

    dark_theme = True    

    def change_theme_color(self):
        RED = (0.95686274509803921568627450980392, 0.26274509803921568627450980392157, 0.21176470588235294117647058823529, 1)
        BLUE = (0.12941176470588235294117647058824, 0.58823529411764705882352941176471, 0.95294117647058823529411764705882, 1)
        if self.dark_theme == True:
            self.theme_cls.theme_style = "Light"
            self.theme_cls.primary_palette = "Blue"
            self.root.artist_name.text_color = BLUE
            self.root.album_name.text_color = BLUE
            self.root.insta_username.text_color = BLUE
            self.root.insta_real_name.text_color = BLUE
            self.root.followers.text_color = BLUE
            self.root.followed_accounts.text_color = BLUE
            self.root.private_account.text_color = BLUE
            self.dark_theme = False
        else:
            self.theme_cls.theme_style = "Dark"
            self.theme_cls.primary_palette = "Red"
            self.root.artist_name.text_color = RED
            self.root.album_name.text_color = RED
            self.root.insta_username.text_color = RED
            self.root.insta_real_name.text_color = RED
            self.root.followers.text_color = RED
            self.root.followed_accounts.text_color = RED
            self.root.private_account.text_color = RED
            self.dark_theme = True

        theme = lambda: "scuro" if self.dark_theme == True else "chiaro"
        Snackbar(text=f"Tema {theme()} selezionato correttamente", duration = 1).show()

    def download_folder_for_system(self):
        if platform == "android":
            DATA_FOLDER = os.getenv('EXTERNAL_STORAGE') or os.path.expanduser("~") + "\\Pictures\\Utilities_downloads"
        elif platform == "win":
            DATA_FOLDER = os.getenv('EXTERNAL_STORAGE') or os.path.expanduser("~") + "\\Pictures\\Utilities_downloads"
        if not os.path.exists(DATA_FOLDER):
            os.mkdir(DATA_FOLDER)
        return DATA_FOLDER

# INIZIO CODICE SPOTIFY

    def change_spotify_search_field_pos(self):

        if self.root.spotify_search_field.focus == True or len(self.get_spotify_text()) != 0:
            self.root.spotify_search_field.pos_hint = {"x": 0.2, "top": 0.82}
        else:
            self.root.spotify_search_field.pos_hint = {"x": 0.2, "top": 0.6}

    def get_spotify_text(self):
        text = self.root.spotify_search_field.text 
        return text

    spotify_exists = True

    def get_spotify_pics(self):
        self.spotify_exists = True
        text = self.get_spotify_text()
        if len(text) != 0:
            try:
                client = deezer.Client()
                data = client.search(self.get_spotify_text())[0].asdict()
                self.spotify_artist_pic_download = data["artist"]["picture_big"]
                self.spotify_album_pic_download = data["album"]["cover_big"]
                self.spotify_pic_number = data["album"]["md5_image"]
                self.root.spotify_artist_pic.source = data["artist"]["picture"]
                self.root.spotify_album_pic.source = data["album"]["cover"]
                self.root.spotify_artist_pic.pos_hint = {"x": 0.25, "top": 0.75}
                self.root.spotify_album_pic.pos_hint = {"x": 0.25, "top": 0.419}
                self.root.download_manager.pos_hint = {"x": 0.76, "top": 0.12}
                artist_name = data["artist"]["name"]
                album_name = data["album"]["title"]
                self.root.artist_name.text = f"Artista: {artist_name}"
                self.root.album_name.text = f"Album: {album_name}"

            except IndexError:
                self.spotify_exists = False

        self.spotify_error()
        self.spotify_pics_clean()

    def spotify_error(self):
        if len(self.get_spotify_text()) != 0 and self.spotify_exists == False:
            self.root.spotify_error.text = "Oops... non ho trovato nulla che corrisponde con ciò che hai cercato"
            self.root.spotify_error_icon.icon = "alert-circle-outline" #-off
        else:
            self.root.spotify_error.text = ""
            self.root.spotify_error_icon.icon = ""

    def spotify_pics_clean(self):
        if len(self.get_spotify_text()) == 0 or self.spotify_exists == False:
            self.root.spotify_artist_pic.source = ""
            self.root.spotify_album_pic.source = ""
            self.root.spotify_artist_pic.pos_hint = {"x": 100}
            self.root.spotify_album_pic.pos_hint = {"x": 100}
            self.root.artist_name.text = ""
            self.root.album_name.text = ""
            self.root.download_manager.pos_hint = {"x": 100}


    def download_menu_open(self):
        if self.root.artist_name.text != "":
            bottom_sheet_menu = MDGridBottomSheet()
            data = {
                "Scarica l'immagine profilo dell'artista": "artist",
                "Scarica la copertina dell'album": "album",
            }
            for item in data.items():
                bottom_sheet_menu.add_item(
                    item[0],
                    lambda x, y=item[0]: self.download_menu_callback(y),
                    icon_src=item[1],
                )
            bottom_sheet_menu.open()

    download_dialog = None

    def show_download_alert(self):
        if not self.download_dialog:
            self.download_dialog = MDDialog(
                text="Immagine scaricata correttamente!",
                radius=[20, 7, 20, 7],
                size_hint= (0.8, 0.8),
                pos_hint = {"center_x": 0.5, "center_y": 0.5},
                buttons = [
                    MDRaisedButton(
                        text = "OK", text_color = self.theme_cls.primary_color, on_release = self.close_download_alert
                    ),
                ],
            )

        self.download_dialog.open()


    def close_download_alert(self, instance):
        self.download_dialog.dismiss()

    def download_menu_callback(self, *args):
        image_type = args[0]
        self.show_download_alert()
        if "artist" in image_type:
            artist_image = urllib.request.urlretrieve(self.spotify_artist_pic_download, f"{self.download_folder_for_system()}\\artist_{self.spotify_pic_number}_image.jpg") # Cambiare cartella di salvataggio per Android
        else:
            album_image = urllib.request.urlretrieve(self.spotify_album_pic_download, f"{self.download_folder_for_system()}\\album_{self.spotify_pic_number}_image.jpg") # Cambiare cartella di salvataggio per Android

# FINE CODICE SPOTIFY
# INIZIO CODICE INSTAGRAM

    def change_insta_account_pos(self):

        if self.root.insta_account_field.focus == True or len(self.get_insta_username()) != 0:
            self.root.insta_account_field.pos_hint = {"x": 0.2, "top": 0.82}
        else:
            self.root.insta_account_field.pos_hint = {"x": 0.2, "top": 0.6}

    def get_insta_username(self):
        username = self.root.insta_account_field.text
        return username

    is_account = True

    def get_insta_profile_pic(self):
        self.is_account = True
        username = self.get_insta_username()
        if len(username) != 0:
            try:
                res = ie.user(username)
                profile_pic_hd = res.data["profile_pic_url_hd"]
                username = res.data["username"]
                real_name = res.data["full_name"]
                followers = res.data["edge_followed_by"]["count"]
                followed_accounts = res.data["edge_follow"]["count"]
                is_private = lambda: "privato" if res.data["is_private"] == True else "pubblico"
                self.root.insta_username.text = username
                self.root.insta_real_name.text = f"Nome reale: {real_name}"
                self.root.followers.text = f"Followers: {followers}"
                self.root.followed_accounts.text = f"Account seguiti: {followed_accounts}"
                self.root.private_account.text = f"Account {is_private()}"
                self.root.profile_pic.source = profile_pic_hd
                self.root.profile_pic.pos_hint = {"x": 0.25, "top": 0.72}
                self.root.insta_download_button.pos_hint = {"x": 0.76, "top": 0.12}
            except (KeyError, ValueError):
                self.is_account = False

        self.profile_error()
        self.profile_pic_clean()


    def profile_error(self):
        if len(self.get_insta_username()) != 0 and self.is_account == False:
            self.root.error.text = "Oops... Sembra che questo account non esista"
            self.root.error_icon.icon = "account-off" #-off
        else:
            self.root.error.text = ""
            self.root.error_icon.icon = ""

    def profile_pic_clean(self):
        if len(self.get_insta_username()) == 0 or self.is_account == False:
            self.root.profile_pic.source = ""
            self.root.profile_pic.pos_hint = {"x": 100}
            self.root.profile_pic.size_hint = (0.5, 0.5)
            self.root.insta_username.text = ""
            self.root.insta_real_name.text = ""
            self.root.followers.text = ""
            self.root.followed_accounts.text = ""
            self.root.private_account.text = ""
            self.root.insta_download_button.pos_hint = {"x": 100}

    def download_insta_menu_open(self):
        if self.root.insta_username.text != "":
            bottom_sheet_menu = MDGridBottomSheet()
            data = {
                "Scarica l'immagine profilo": "clipboard-account",
            }
            for item in data.items():
                bottom_sheet_menu.add_item(
                    item[0],
                    lambda x, y=item[0]: self.download_insta_pic_callback(y),
                    icon_src=item[1],
                )
            bottom_sheet_menu.open()

    def download_insta_pic_callback(self, *args):
        try:
            image_type = args[0]
            self.show_download_alert()
            insta_profile_pic = urllib.request.urlretrieve(self.root.profile_pic.source, f"{self.download_folder_for_system()}\\{self.get_insta_username()}_profilepic.jpg") # Cambiare cartella di salvataggio per Android
        except ValueError:
            print("Nessun account selezionato")

# FINE CODICE INSTAGRAM

    def build(self):
        self.title = "Utilities"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Red"
        kv = Builder.load_file("my.kv")
        return kv


if __name__ == "__main__":
    MyApp().run()
