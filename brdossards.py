import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import pytz
import csv
import ttkbootstrap as ttk

class RaceTimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Race Timer")

        style = ttk.Style()
        style.theme_use('flatly')

        self.sas_times = {
            "SAS 1": "14:00:00",
            "SAS 2": "14:30:00",
            "SAS 3": "15:00:00"
        }

        self.bib_to_name = self.import_bib_to_name()

        self.create_widgets()
        self.bind_events()

        # Start the auto-save process without saving initially
        self.root.after(300000, self.auto_save)  # Schedule the first save for 5 minutes later

    def import_bib_to_name(self):
        filename = filedialog.askopenfilename(title="Sélectionnez le fichier CSV", filetypes=[("CSV files", "*.csv")])
        if not filename:
            return {}

        bib_to_name = {}
        with open(filename, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                bib_number = row.get('n° dossard')
                first_name = row.get('Prénom')
                last_name = row.get('Nom')
                if bib_number and first_name and last_name:
                    bib_to_name[bib_number] = f"{first_name} {last_name}"

        return bib_to_name

    def create_widgets(self):
        ttk.Label(self.root, text="Sélectionner le SAS :", font=("Helvetica", 14)).pack(pady=10)

        self.sas_var = tk.StringVar()
        self.sas_combobox = ttk.Combobox(self.root, textvariable=self.sas_var, values=list(self.sas_times.keys()), font=("Helvetica", 14))
        self.sas_combobox.pack(pady=10)
        self.sas_combobox.current(0)
        self.sas_combobox.bind('<<ComboboxSelected>>', self.update_start_time_label)

        self.sas_start_time_label = ttk.Label(self.root, text=f"Heure de départ: {self.sas_times[self.sas_combobox.get()]}", font=("Helvetica", 14))
        self.sas_start_time_label.pack(pady=10)

        ttk.Label(self.root, text="N° de dossard :", font=("Helvetica", 14)).pack(pady=10)
        self.bib_number_entry = ttk.Entry(self.root, font=("Helvetica", 14))
        self.bib_number_entry.pack(pady=10)

        self.calculate_button = ttk.Button(self.root, text="Calculer Temps Total", command=self.calculate_time, bootstyle="primary")
        self.calculate_button.pack(pady=20)

        self.result_label = ttk.Label(self.root, text="", font=("Helvetica", 14))
        self.result_label.pack(pady=10)

        self.arrivals_label = ttk.Label(self.root, text="Liste des arrivées :", font=("Helvetica", 14))
        self.arrivals_label.pack(pady=10)

        self.arrivals_listbox = tk.Listbox(self.root, font=("Helvetica", 14), width=100, height=10)
        self.arrivals_listbox.pack(pady=10)

        self.export_button = ttk.Button(self.root, text="Exporter les données", command=self.export_data, bootstyle="secondary")
        self.export_button.pack(pady=10)
        
        # Add delete button
        self.delete_button = ttk.Button(self.root, text="Supprimer sélection", command=self.delete_selected, bootstyle="danger")
        self.delete_button.pack(pady=10)

        # Add a live clock with larger font
        self.clock_label = ttk.Label(self.root, font=("Helvetica", 24))
        self.clock_label.pack(pady=10)
        self.update_clock()

    def bind_events(self):
        self.root.bind('<Return>', self.on_enter)
        self.root.bind('<KP_Enter>', self.on_enter)

    def update_start_time_label(self, event=None):
        selected_sas = self.sas_var.get()
        self.sas_start_time_label.config(text=f"Heure de départ: {self.sas_times[selected_sas]}")

    def calculate_time(self):
        sas = self.sas_var.get()
        start_time_str = self.sas_times[sas]
        paris_tz = pytz.timezone('Europe/Paris')
        now = datetime.now(paris_tz)
        start_time = now.replace(hour=int(start_time_str.split(":")[0]), 
                                 minute=int(start_time_str.split(":")[1]), 
                                 second=int(start_time_str.split(":")[2]), 
                                 microsecond=0)

        end_time = datetime.now(paris_tz)
        total_seconds = (end_time - start_time).total_seconds()
        total_time = timedelta(seconds=total_seconds)
        total_time_str = str(total_time).split('.')[0]

        bib_number = self.bib_number_entry.get()
        if bib_number in self.bib_to_name:
            name = self.bib_to_name.get(bib_number, "Inconnu")
            arrival_entry = f"Dossard {bib_number} ({name}) - {sas}, Départ: {start_time_str}, Arrivée: {end_time.strftime('%H:%M:%S')}, Temps total: {total_time_str}"
            self.arrivals_listbox.insert(0, arrival_entry)  # Insert at the top
            self.result_label.config(text=f"Temps total pour dossard '{bib_number}' ({name}) : {total_time_str}")
            self.bib_number_entry.delete(0, tk.END)
        else:
            self.result_label.config(text="Numéro de dossard inconnu.")

    def on_enter(self, event):
        self.calculate_time()

    def export_data(self, filename=None):
        arrivals = self.arrivals_listbox.get(0, tk.END)
        if arrivals:
            current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"arrivals_{current_time}.csv"
            with open(filename, "w", newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Dossard", "Nom", "SAS", "Départ", "Arrivée", "Temps total"])
                for arrival in arrivals:
                    parts = arrival.split(" - ")
                    if len(parts) == 2:
                        bib_and_name = parts[0].split(" (")
                        bib_number = bib_and_name[0].split(" ")[1]
                        name = bib_and_name[1][:-1] if len(bib_and_name) > 1 else "Inconnu"
                        sas_and_times = parts[1].split(", ")
                        sas = sas_and_times[0].split(": ")[1] if len(sas_and_times) > 0 else ""
                        start_time = sas_and_times[1].split(": ")[1] if len(sas_and_times) > 1 else ""
                        end_time = sas_and_times[2].split(": ")[1] if len(sas_and_times) > 2 else ""
                        total_time = sas_and_times[3].split(": ")[1] if len(sas_and_times) > 3 else ""
                        writer.writerow([bib_number, name, sas, start_time, end_time, total_time])
            messagebox.showinfo("Exportation réussie", f"Les données ont été exportées avec succès dans '{filename}'.")
        else:
            messagebox.showwarning("Aucune donnée", "Il n'y a aucune donnée à exporter.")
    
    def delete_selected(self):
        selected_indices = self.arrivals_listbox.curselection()
        for index in selected_indices[::-1]:  # Reverse order to avoid issues with deleting
            self.arrivals_listbox.delete(index)
    
    def update_clock(self):
        now = datetime.now().strftime('%H:%M:%S')
        self.clock_label.config(text=f"Heure actuelle : {now}")
        self.root.after(1000, self.update_clock)

    def auto_save(self):
        arrivals = self.arrivals_listbox.get(0, tk.END)
        if arrivals:  # Only save if there are entries in the listbox
            current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"arrivals_{current_time}.csv"
            self.export_data(filename)
        self.root.after(300000, self.auto_save)  # Save every 5 minutes

if __name__ == "__main__":
    root = ttk.Window(themename="flatly")
    app = RaceTimerApp(root)
    root.mainloop()
