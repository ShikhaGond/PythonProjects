import tkinter as tk
from tkinter import ttk, scrolledtext
import requests
from googletrans import Translator
import json
import os
# from dotenv import load_dotenv

# # Load environment variables from .env file
# load_dotenv()

class LanguageTranslatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Language Translator")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")
        
        # Initialize translator
        self.translator = Translator()
        
        # Dictionary of language codes and names
        self.languages = {
            'af': 'Afrikaans', 'sq': 'Albanian', 'am': 'Amharic', 'ar': 'Arabic',
            'hy': 'Armenian', 'az': 'Azerbaijani', 'eu': 'Basque', 'be': 'Belarusian',
            'bn': 'Bengali', 'bs': 'Bosnian', 'bg': 'Bulgarian', 'ca': 'Catalan',
            'ceb': 'Cebuano', 'ny': 'Chichewa', 'zh-cn': 'Chinese (Simplified)',
            'zh-tw': 'Chinese (Traditional)', 'co': 'Corsican', 'hr': 'Croatian',
            'cs': 'Czech', 'da': 'Danish', 'nl': 'Dutch', 'en': 'English',
            'eo': 'Esperanto', 'et': 'Estonian', 'tl': 'Filipino', 'fi': 'Finnish',
            'fr': 'French', 'fy': 'Frisian', 'gl': 'Galician', 'ka': 'Georgian',
            'de': 'German', 'el': 'Greek', 'gu': 'Gujarati', 'ht': 'Haitian Creole',
            'ha': 'Hausa', 'haw': 'Hawaiian', 'iw': 'Hebrew', 'hi': 'Hindi',
            'hmn': 'Hmong', 'hu': 'Hungarian', 'is': 'Icelandic', 'ig': 'Igbo',
            'id': 'Indonesian', 'ga': 'Irish', 'it': 'Italian', 'ja': 'Japanese',
            'jw': 'Javanese', 'kn': 'Kannada', 'kk': 'Kazakh', 'km': 'Khmer',
            'ko': 'Korean', 'ku': 'Kurdish (Kurmanji)', 'ky': 'Kyrgyz', 'lo': 'Lao',
            'la': 'Latin', 'lv': 'Latvian', 'lt': 'Lithuanian', 'lb': 'Luxembourgish',
            'mk': 'Macedonian', 'mg': 'Malagasy', 'ms': 'Malay', 'ml': 'Malayalam',
            'mt': 'Maltese', 'mi': 'Maori', 'mr': 'Marathi', 'mn': 'Mongolian',
            'my': 'Myanmar (Burmese)', 'ne': 'Nepali', 'no': 'Norwegian', 'ps': 'Pashto',
            'fa': 'Persian', 'pl': 'Polish', 'pt': 'Portuguese', 'pa': 'Punjabi',
            'ro': 'Romanian', 'ru': 'Russian', 'sm': 'Samoan', 'gd': 'Scots Gaelic',
            'sr': 'Serbian', 'st': 'Sesotho', 'sn': 'Shona', 'sd': 'Sindhi',
            'si': 'Sinhala', 'sk': 'Slovak', 'sl': 'Slovenian', 'so': 'Somali',
            'es': 'Spanish', 'su': 'Sundanese', 'sw': 'Swahili', 'sv': 'Swedish',
            'tg': 'Tajik', 'ta': 'Tamil', 'te': 'Telugu', 'th': 'Thai', 'tr': 'Turkish',
            'uk': 'Ukrainian', 'ur': 'Urdu', 'uz': 'Uzbek', 'vi': 'Vietnamese',
            'cy': 'Welsh', 'xh': 'Xhosa', 'yi': 'Yiddish', 'yo': 'Yoruba', 'zu': 'Zulu'
        }
        
        self.create_widgets()
    
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title label
        title_label = ttk.Label(main_frame, text="Language Translator", font=("Helvetica", 18, "bold"))
        title_label.pack(pady=10)
        
        # Language selection frame
        lang_frame = ttk.Frame(main_frame)
        lang_frame.pack(fill=tk.X, pady=5)
        
        # Source language
        source_label = ttk.Label(lang_frame, text="From:")
        source_label.pack(side=tk.LEFT, padx=5)
        
        self.source_lang_var = tk.StringVar()
        self.source_lang_dropdown = ttk.Combobox(lang_frame, textvariable=self.source_lang_var, state="readonly")
        self.source_lang_dropdown['values'] = sorted(list(self.languages.values()))
        self.source_lang_dropdown.current(self.get_language_index('en'))
        self.source_lang_dropdown.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        # Target language
        target_label = ttk.Label(lang_frame, text="To:")
        target_label.pack(side=tk.LEFT, padx=5)
        
        self.target_lang_var = tk.StringVar()
        self.target_lang_dropdown = ttk.Combobox(lang_frame, textvariable=self.target_lang_var, state="readonly")
        self.target_lang_dropdown['values'] = sorted(list(self.languages.values()))
        self.target_lang_dropdown.current(self.get_language_index('es'))
        self.target_lang_dropdown.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        # Text areas frame
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Source text
        source_text_frame = ttk.LabelFrame(text_frame, text="Enter text to translate")
        source_text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.source_text = scrolledtext.ScrolledText(source_text_frame, wrap=tk.WORD, height=10)
        self.source_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Target text
        target_text_frame = ttk.LabelFrame(text_frame, text="Translation")
        target_text_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        self.target_text = scrolledtext.ScrolledText(target_text_frame, wrap=tk.WORD, height=10)
        self.target_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        # Swap languages button
        swap_btn = ttk.Button(buttons_frame, text="↔️ Swap Languages", command=self.swap_languages)
        swap_btn.pack(side=tk.LEFT, padx=5)
        
        # Clear button
        clear_btn = ttk.Button(buttons_frame, text="🗑️ Clear", command=self.clear_text)
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Copy button
        copy_btn = ttk.Button(buttons_frame, text="📋 Copy Translation", command=self.copy_translation)
        copy_btn.pack(side=tk.LEFT, padx=5)
        
        # Translate button
        translate_btn = ttk.Button(buttons_frame, text="🌐 Translate", command=self.translate_text)
        translate_btn.pack(side=tk.RIGHT, padx=5)
        
        # API selection frame
        api_frame = ttk.LabelFrame(main_frame, text="Translation API")
        api_frame.pack(fill=tk.X, pady=5)
        
        self.api_var = tk.StringVar(value="googletrans")
        
        googletrans_radio = ttk.Radiobutton(api_frame, text="Google Translate (Free)", variable=self.api_var, value="googletrans")
        googletrans_radio.pack(side=tk.LEFT, padx=20)
        
        libretrans_radio = ttk.Radiobutton(api_frame, text="LibreTranslate", variable=self.api_var, value="libre")
        libretrans_radio.pack(side=tk.LEFT, padx=20)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def get_language_index(self, lang_code):
        """Get the index of a language in the dropdown by its code"""
        if lang_code in self.languages:
            lang_name = self.languages[lang_code]
            return sorted(list(self.languages.values())).index(lang_name)
        return 0
    
    def get_language_code(self, language_name):
        """Get language code from language name"""
        for code, name in self.languages.items():
            if name == language_name:
                return code
        return 'en'  # Default to English
    
    def translate_text(self):
        """Translate the input text"""
        source_text = self.source_text.get("1.0", tk.END).strip()
        if not source_text:
            self.status_var.set("Please enter text to translate")
            return
        
        source_lang = self.get_language_code(self.source_lang_var.get())
        target_lang = self.get_language_code(self.target_lang_var.get())
        
        self.status_var.set(f"Translating from {self.source_lang_var.get()} to {self.target_lang_var.get()}...")
        self.root.update()
        
        try:
            if self.api_var.get() == "googletrans":
                translated_text = self.translate_with_googletrans(source_text, source_lang, target_lang)
            else:
                translated_text = self.translate_with_libretranslate(source_text, source_lang, target_lang)
            
            self.target_text.delete("1.0", tk.END)
            self.target_text.insert("1.0", translated_text)
            self.status_var.set("Translation complete")
        except Exception as e:
            self.status_var.set(f"Translation error: {str(e)}")
            self.target_text.delete("1.0", tk.END)
            self.target_text.insert("1.0", f"Error: {str(e)}")
    
    def translate_with_googletrans(self, text, source_lang, target_lang):
        """Translate text using the googletrans library"""
        if source_lang == 'auto':
            result = self.translator.translate(text, dest=target_lang)
        else:
            result = self.translator.translate(text, src=source_lang, dest=target_lang)
        return result.text
    
    def translate_with_libretranslate(self, text, source_lang, target_lang):
        """Translate text using LibreTranslate API"""
        # Get API URL and key from environment variables
        libre_url = os.getenv("LIBRETRANSLATE_URL", "https://libretranslate.com/translate")
        libre_api_key = os.getenv("LIBRETRANSLATE_API_KEY", "")
        
        payload = {
            "q": text,
            "source": source_lang,
            "target": target_lang,
            "format": "text"
        }
        
        if libre_api_key:
            payload["api_key"] = libre_api_key
            
        headers = {
            "Content-Type": "application/json"
        }
        
        response = requests.post(libre_url, data=json.dumps(payload), headers=headers)
        
        if response.status_code == 200:
            return response.json()["translatedText"]
        else:
            raise Exception(f"API Error: {response.status_code} - {response.text}")
    
    def swap_languages(self):
        """Swap source and target languages"""
        source_lang = self.source_lang_var.get()
        target_lang = self.target_lang_var.get()
        
        self.source_lang_var.set(target_lang)
        self.target_lang_var.set(source_lang)
        
        # Also swap the text if there's translated text
        source_text = self.source_text.get("1.0", tk.END).strip()
        target_text = self.target_text.get("1.0", tk.END).strip()
        
        if target_text and source_text:
            self.source_text.delete("1.0", tk.END)
            self.target_text.delete("1.0", tk.END)
            
            self.source_text.insert("1.0", target_text)
            self.target_text.insert("1.0", source_text)
    
    def clear_text(self):
        """Clear both text areas"""
        self.source_text.delete("1.0", tk.END)
        self.target_text.delete("1.0", tk.END)
        self.status_var.set("Cleared")
    
    def copy_translation(self):
        """Copy translation to clipboard"""
        translated_text = self.target_text.get("1.0", tk.END).strip()
        self.root.clipboard_clear()
        self.root.clipboard_append(translated_text)
        self.status_var.set("Translation copied to clipboard")

if __name__ == "__main__":
    root = tk.Tk()
    app = LanguageTranslatorApp(root)
    root.mainloop()