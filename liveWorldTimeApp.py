from datetime import datetime
import pytz
from tkinter import *
from tkinter import ttk
import webbrowser

root = Tk()
root.title("OPEN World")
root.geometry("700x400")

# Function to open Google Maps with the selected location
def open_map():
   map_url = f"https://www.google.com/maps/search/?api=1&query={country_var.get().replace(' ', '+')}"
   webbrowser.open(map_url)

# Function to update the map and time display
def update_map_and_time():
   continent = continent_var.get()
   country = country_var.get()

   if continent == 'Asia':
      if country == 'India':
         timezone = 'Asia/Kolkata'
      elif country == 'China':
         timezone = 'Asia/Shanghai'
      elif country == 'Japan':
         timezone = 'Asia/Tokyo'
      elif country == 'Pakistan':
         timezone = 'Asia/Karachi'
      elif country == 'Bangladesh':
         timezone = 'Asia/Dhaka'
      else:
         return
   elif continent == 'Australia':
      timezone = 'Australia/Victoria'
   elif continent == 'Africa':
      if country == 'Nigeria':
         timezone = 'Africa/Lagos'
      elif country == 'Algeria':
         timezone = 'Africa/Algiers'
      else:
         return
   elif continent == 'America':
      if country == 'USA (West)':
         timezone = 'America/Los_Angeles'
      elif country == 'Argentina':
         timezone = 'America/Argentina/Buenos_Aires'
      elif country == 'Canada':
         timezone = 'America/Toronto'
      elif country == 'Brazil':
         timezone = 'America/Sao_Paulo'
      else:
         return
   elif continent == 'Europe':
      if country == 'UK':
         timezone = 'Europe/London'
      elif country == 'Portugal':
         timezone = 'Europe/Lisbon'
      elif country == 'Italy':
         timezone = 'Europe/Rome'
      elif country == 'Spain':
         timezone = 'Europe/Madrid'
      else:
         return
    
   # Update the time
   home = pytz.timezone(timezone)
   local_time = datetime.now(home)
   current_time = local_time.strftime("%H:%M:%S")
   clock_label.config(text=current_time)

   # Open Google Maps in the web browser
   open_map()

# Function to update the country options based on selected continent
def update_countries(event):
   continent = continent_var.get()

   if continent == 'Asia':
      countries = ['India', 'China', 'Japan', 'Pakistan', 'Bangladesh']
   elif continent == 'Australia':
      countries = ['Australia']
   elif continent == 'Africa':
      countries = ['Nigeria', 'Algeria']
   elif continent == 'America':
      countries = ['USA (West)', 'Argentina', 'Canada', 'Brazil']
   elif continent == 'Europe':
      countries = ['UK', 'Portugal', 'Italy', 'Spain']
   else:
      countries = []

   country_menu['values'] = countries
   country_var.set('')  # Reset country selection

# Continent Selection
continent_var = StringVar()
continent_var.set('Asia')  # Default value
continent_label = Label(root, text="Select Continent:", font=("Arial", 14))
continent_label.pack(pady=10)
continent_menu = ttk.Combobox(root, textvariable=continent_var, font=("Arial", 12), state="readonly", width=20)
continent_menu['values'] = ['Asia', 'Australia', 'Africa', 'America', 'Europe']
continent_menu.pack(pady=10)
continent_menu.bind('<<ComboboxSelected>>', update_countries)

# Country Selection
country_var = StringVar()
country_label = Label(root, text="Select Country:", font=("Arial", 14))
country_label.pack(pady=10)
country_menu = ttk.Combobox(root, textvariable=country_var, font=("Arial", 12), state="readonly", width=20)
country_menu.pack(pady=10)
country_menu.bind('<<ComboboxSelected>>', lambda event: update_map_and_time())

# Time Display
clock_label = Label(root, font=("Arial", 25, "bold"))
clock_label.pack(pady=20)

root.mainloop()