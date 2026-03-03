import sys
import os
import pandas as pd
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QCheckBox, QFileDialog, QPushButton, QButtonGroup
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT
import seaborn as sns
import matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor

class PlotCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar2QT(self.canvas, self)
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.addWidget(self.toolbar)
        self.setLayout(layout)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HQD-RTP Data")
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.init_ui_for_multiple_files()

    def clear_layout(self):
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def init_ui_for_multiple_files(self):
        self.clear_layout()

        self.plot_canvas = PlotCanvas()
        self.layout.addWidget(self.plot_canvas)

        self.param_group = QButtonGroup(self)
        self.checkboxes = {
            'Pressure': QCheckBox('Show Pressure'),
            'Power': QCheckBox('Show Power'),
            'T_Set': QCheckBox('Show T_Set'),
            'T_Ist': QCheckBox('Show T_Ist'),
            'O2': QCheckBox('Show O\u2082'),
            'Ar_Fluss': QCheckBox('Show Ar-Fluss'),
            'N2_30_Fluss': QCheckBox('Show N\u2082-30-Fluss'),
            'N2_150_Fluss': QCheckBox('Show N\u2082-150-Fluss')
        }

        for checkbox in self.checkboxes.values():
            self.layout.addWidget(checkbox)
            self.param_group.addButton(checkbox)
            checkbox.stateChanged.connect(self.update_plot_multiple)

        self.load_button = QPushButton('Load File')
        self.load_button.clicked.connect(self.load_files)
        self.layout.addWidget(self.load_button)

        self.df_datatoplot = pd.DataFrame()
        self.file_checkboxes = {}

    def init_ui_for_single_file(self):
        self.clear_layout()

        self.plot_canvas = PlotCanvas()
        self.layout.addWidget(self.plot_canvas)

        self.checkbox_pressure = QCheckBox('Show Pressure')
        self.checkbox_pressure.setChecked(True)
        self.checkbox_pressure.stateChanged.connect(self.update_plot_single)
        self.layout.addWidget(self.checkbox_pressure)

        self.checkbox_power = QCheckBox('Show Power')
        self.checkbox_power.setChecked(True)
        self.checkbox_power.stateChanged.connect(self.update_plot_single)
        self.layout.addWidget(self.checkbox_power)

        self.checkbox_t_set = QCheckBox('Show T_Set')
        self.checkbox_t_set.setChecked(True)
        self.checkbox_t_set.stateChanged.connect(self.update_plot_single)
        self.layout.addWidget(self.checkbox_t_set)

        self.checkbox_t_ist = QCheckBox('Show T_Ist')
        self.checkbox_t_ist.setChecked(True)
        self.checkbox_t_ist.stateChanged.connect(self.update_plot_single)
        self.layout.addWidget(self.checkbox_t_ist)

        self.checkbox_o2 = QCheckBox('Show O\u2082')
        self.checkbox_o2.setChecked(True)
        self.checkbox_o2.stateChanged.connect(self.update_plot_single)
        self.layout.addWidget(self.checkbox_o2)

        self.checkbox_o2_limit = QCheckBox('Show O\u2082 Limit (100 ppm)')
        self.checkbox_o2_limit.setChecked(True)
        self.checkbox_o2_limit.stateChanged.connect(self.update_plot_single)
        self.layout.addWidget(self.checkbox_o2_limit)

        self.checkbox_ar_fluss = QCheckBox('Show Ar-Fluss')
        self.checkbox_ar_fluss.setChecked(True)
        self.checkbox_ar_fluss.stateChanged.connect(self.update_plot_single)
        self.layout.addWidget(self.checkbox_ar_fluss)

        self.checkbox_n2_fluss = QCheckBox('Show N\u2082-Fluss')
        self.checkbox_n2_fluss.setChecked(True)
        self.checkbox_n2_fluss.stateChanged.connect(self.update_plot_single)
        self.layout.addWidget(self.checkbox_n2_fluss)

        self.checkbox_fit_axes = QCheckBox('Fit Axes')
        self.checkbox_fit_axes.setChecked(False)
        self.checkbox_fit_axes.stateChanged.connect(self.update_plot_single)
        self.layout.addWidget(self.checkbox_fit_axes)

        self.load_button = QPushButton('Load File')  # "Load File"-Button hinzufügen
        self.load_button.clicked.connect(self.load_files)  # Verbindung zur bestehenden load_files-Methode
        self.layout.addWidget(self.load_button)

    def load_files(self):
        # Setzen Sie den DataFrame zurück, um alte Daten zu löschen
        self.df_datatoplot = pd.DataFrame()

        # Löschen vorhandener Dateicheckboxen
        for checkbox in self.file_checkboxes.values():
            self.layout.removeWidget(checkbox)
            checkbox.deleteLater()
        self.file_checkboxes.clear()

        # Öffnen Sie den Dateidialog und laden Sie neue Dateien
        files, _ = QFileDialog.getOpenFileNames(self, "Select CSV Files", "", "CSV Files (*.csv)")
        if not files:
            return  # Keine Dateien ausgewählt

        if len(files) == 1:
            self.load_single_file(files[0])
        elif len(files) > 1:
            # Wechsle zur Mehrfachdatei-UI
            self.init_ui_for_multiple_files()
            # Lade die Dateien in der Mehrfachdatei-UI
            self.load_multiple_files(files)

    def load_single_file(self, file):
        self.init_ui_for_single_file()
        df = pd.read_csv(file, sep=';', decimal=',', low_memory=False)
        self.df_datatoplot = df.replace('', np.nan)
        self.current_file = file
        self.update_plot_single()

    def load_multiple_files(self, files):
        with ThreadPoolExecutor() as executor:
            dfs = list(executor.map(self.load_file, files))
        self.df_datatoplot = pd.concat(dfs, ignore_index=True)
        for file in files:
            filename = os.path.basename(file)
            if filename not in self.file_checkboxes:
                checkbox = QCheckBox(filename)
                checkbox.setChecked(True)
                self.file_checkboxes[filename] = checkbox
                self.layout.addWidget(checkbox)
                checkbox.stateChanged.connect(self.update_plot_multiple)
        self.update_plot_multiple()

    def load_file(self, file):
        df = pd.read_csv(file, sep=';', decimal=',', low_memory=False)
        df['Filename'] = os.path.basename(file)
        return df

    def update_plot_single(self):
        if self.df_datatoplot is not None: 
            self.plot_canvas.figure.clear()
            self.plot_canvas.ax = self.plot_canvas.figure.subplots()
            filename = os.path.basename(self.current_file) if self.current_file else "Unbekannt"
            self.plot_canvas.ax.set_title(filename[:-4], y=1.02)  # Setzen des Dateinamens als Titel.

            handles, labels = [], []

            self.plot_canvas.ax.set_xlim([0, 900])
            self.plot_canvas.ax.set_xlabel('Time (s)')

            if self.checkbox_pressure.isChecked() and '[2] Chamber_Pressure_Readout in Torr' in self.df_datatoplot.columns:
                scatter = sns.scatterplot(x='Timestamp in s', y='[2] Chamber_Pressure_Readout in Torr', data=self.df_datatoplot, ax=self.plot_canvas.ax, label='Pressure', color='purple')
                h, l = scatter.get_legend_handles_labels()
                handles += h
                labels += l
                scatter.legend_.remove()

                if not self.checkbox_fit_axes.isChecked():
                    self.plot_canvas.ax.set_ylim([700, 900])
                    self.plot_canvas.ax.set_ylabel('Chamber Pressure (Torr)')

            else:
                self.plot_canvas.ax.set_visible(False)  # Achse wird unsichtbar gemacht, wenn keine Daten gezeichnet werden    

            ax5 = self.plot_canvas.ax.twinx()
            ax5.spines['left'].set_position(('outward', 60))
            ax5.yaxis.set_ticks_position('left')
            ax5.yaxis.set_label_position('left')
            ax5.spines['right'].set_color('brown')
            ax5.spines['left'].set_color('black')
            ax5.spines['top'].set_color('none')

            if self.checkbox_power.isChecked() and '[104] Power in kW' in self.df_datatoplot.columns:
                scatter = sns.scatterplot(x='Timestamp in s', y='[104] Power in kW', data=self.df_datatoplot, ax=ax5, label='Power', color='brown')
                h, l = scatter.get_legend_handles_labels()
                handles += h
                labels += l
                scatter.legend_.remove()

                if not self.checkbox_fit_axes.isChecked():
                    ax5.set_ylim([0, 100])
                    ax5.set_ylabel('Power (kW)')

            else:
                ax5.set_visible(False)  # Mache ax5 unsichtbar, wenn die Bedingungen nicht erfüllt sind        

            ax2 = self.plot_canvas.ax.twinx()
            ax2.spines['right'].set_position(('outward', 120))
            ax2.set_yscale('log')  # Diese Zeile setzt die y-Achse auf logarithmische Skalierung
            # Erstellen Sie eine Kopie des DataFrames für die Umrechnung
            df_datatoplot_copy = self.df_datatoplot.copy()

            if self.checkbox_o2.isChecked() and '[84] O2 Level in pu' in df_datatoplot_copy.columns:
                df_datatoplot_copy['[84] O2 Level in ppm'] = df_datatoplot_copy['[84] O2 Level in pu'] * 1e6  # Umrechnung von pu zu ppm
                scatter = sns.scatterplot(x='Timestamp in s', y='[84] O2 Level in ppm', data=df_datatoplot_copy, ax=ax2, label='O2 Level', color='r')
                h, l = scatter.get_legend_handles_labels()
                handles += h
                labels += l
                scatter.legend_.remove()

                if not self.checkbox_fit_axes.isChecked():
                    ax2.set_ylim([1E0, 1E6])
                    ax2.set_ylabel('O2 Level (ppm)')
                    #Zeichnet eine graue, gestrichelte und 50% transparente Linie bei y=100 Mindestwert der erreicht werden muss beim Laseranneler zum Prozessstart
                    if self.checkbox_o2_limit.isChecked():
                        ax2.axhline(y=100, color='gray', linestyle='--', alpha=0.2, zorder=-np.inf) 
                   
                    

            else:
                ax2.set_visible(False)  # Mache ax2 unsichtbar, wenn die Bedingungen nicht erfüllt sind

            # Erstellen einer neuen y-Achse für Temperaturdaten auf der rechten Seite
            ax3 = self.plot_canvas.ax.twinx()
            ax3.spines['right'].set_position(('outward', 0))  # Position der Spine nach außen setzen

            # Überprüfen, ob die Checkbox für 'T_Set' aktiviert ist und ob die entsprechende Spalte in den Daten vorhanden ist
            if self.checkbox_t_set.isChecked() and '[103] T_Set in °C' in self.df_datatoplot.columns:
                if not self.df_datatoplot['[103] T_Set in °C'].isnull().all():  # Sicherstellen, dass die Daten nicht komplett fehlen
                    scatter = sns.scatterplot(x='Timestamp in s', y='[103] T_Set in °C', data=self.df_datatoplot, ax=ax3, label='T_Set', color='g')
                    h, l = scatter.get_legend_handles_labels()
                    if not self.checkbox_t_ist.isChecked():  # Hinzufügen von Handles und Labels, wenn 'T_Ist' nicht gecheckt ist
                        handles += h
                        labels += l
                    scatter.legend_.remove()  # Entfernen der automatisch erzeugten Legende

            # Überprüfen, ob die Checkbox für 'T_Ist' aktiviert ist und ob die entsprechende Spalte in den Daten vorhanden ist
            if self.checkbox_t_ist.isChecked() and '[109] T_Mdl3 in °C' in self.df_datatoplot.columns:
                scatter = sns.scatterplot(x='Timestamp in s', y='[109] T_Mdl3 in °C', data=self.df_datatoplot, ax=ax3, label='T_Ist', color='lightgreen')
                h, l = scatter.get_legend_handles_labels()
                handles += h
                labels += l
                scatter.legend_.remove()  # Entfernen der Legende

            # Einstellen der Achsenbeschriftungen und Grenzen, wenn das Kontrollkästchen 'Fit Axes' nicht aktiviert ist
            if not self.checkbox_fit_axes.isChecked():
                ax3.set_ylim([0, 1400])  # Setzen der y-Achsen-Grenzen
                ax3.set_ylabel('Temperature (°C)')  # Setzen der y-Achsen-Beschriftung

            # Setzen der Achse ax3 auf unsichtbar, wenn keine der Bedingungen erfüllt ist
            if (not self.checkbox_t_set.isChecked() or '[103] T_Set in °C' not in self.df_datatoplot.columns or self.df_datatoplot['[103] T_Set in °C'].isnull().all()) and \
            (not self.checkbox_t_ist.isChecked() or '[109] T_Mdl3 in °C' not in self.df_datatoplot.columns):
                ax3.set_visible(False)  # Achse wird unsichtbar gemacht, wenn keine Daten gezeichnet werden
                

            # Erstellen einer neuen y-Achse auf der rechten Seite des Plots
            ax4 = self.plot_canvas.ax.twinx()

            # Setzen der Position der zusätzlichen y-Achse nach außen um 60 Punkte
            ax4.spines['right'].set_position(('outward', 60))

            # Überprüfen, ob die Checkbox für Argon-Fluss aktiviert ist und ob die entsprechende Spalte in den Daten vorhanden ist
            if self.checkbox_ar_fluss.isChecked() and '[20] Ar_20slm_Readout in slm' in self.df_datatoplot.columns:
                # Erstellen eines Scatterplots für Argon-Fluss
                scatter = sns.scatterplot(x='Timestamp in s', y='[20] Ar_20slm_Readout in slm', data=self.df_datatoplot, ax=ax4, label='Ar-Fluss', color='orange')
                
                # Abrufen der Legende-Handles und Labels
                h, l = scatter.get_legend_handles_labels()
                
                # Wenn die Stickstoff-Fluss Checkbox nicht aktiviert ist, füge die aktuellen Handles und Labels zu den Gesamt-Handles und Labels hinzu
                if not self.checkbox_n2_fluss.isChecked():
                    handles += h
                    labels += l
                
                # Entfernen der automatisch erzeugten Legende
                scatter.legend_.remove()

                # Einstellen der y-Achsenbeschränkungen und Beschriftung, wenn die Checkbox zur Achsenanpassung nicht aktiviert ist
                if not self.checkbox_fit_axes.isChecked():
                    ax4.set_ylim([0, 60])
                    ax4.set_ylabel('Gas-Flow (slm)')

            # Überprüfen, ob die Checkbox für Stickstoff-Fluss aktiviert ist und ob die entsprechenden Spalten in den Daten vorhanden sind
            if self.checkbox_n2_fluss.isChecked() and '[22] N2_30slm_Readout in slm' in self.df_datatoplot.columns and '[83] N2_150slm_Readout in slm' in self.df_datatoplot.columns:
                # Erstellen eines Scatterplots für Stickstoff-Fluss 30 slm
                scatter = sns.scatterplot(x='Timestamp in s', y='[22] N2_30slm_Readout in slm', data=self.df_datatoplot, ax=ax4, label='N2-Flow 30', color='skyblue')
                
                # Abrufen der Legende-Handles und Labels
                h, l = scatter.get_legend_handles_labels()
                
                # Wenn die Argon-Fluss Checkbox nicht aktiviert ist, füge die aktuellen Handles und Labels zu den Gesamt-Handles und Labels hinzu
                if not self.checkbox_ar_fluss.isChecked():
                    handles += h
                    labels += l
                
                # Entfernen der automatisch erzeugten Legende
                scatter.legend_.remove()

                # Erstellen eines weiteren Scatterplots für Stickstoff-Fluss 150 slm
                scatter = sns.scatterplot(x='Timestamp in s', y='[83] N2_150slm_Readout in slm', data=self.df_datatoplot, ax=ax4, label='N2-Flow 150', color='blue')
                h, l = scatter.get_legend_handles_labels()
                handles += h
                labels += l
                scatter.legend_.remove()

                # Einstellen der y-Achsenbeschränkungen und Beschriftung, wenn die Checkbox zur Achsenanpassung nicht aktiviert ist
                if not self.checkbox_fit_axes.isChecked():
                    ax4.set_ylim([0, 60])
                    ax4.set_ylabel('Gas-Flow (slm)')
           
            # Wenn keine der Bedingungen erfüllt ist, setze die Achse ax4 auf unsichtbar, um sie nicht zu zeichnen
            if (not self.checkbox_ar_fluss.isChecked() or '[20] Ar_20slm_Readout in slm' not in self.df_datatoplot.columns) and \
                    (not self.checkbox_n2_fluss.isChecked() or ('[22] N2_30slm_Readout in slm' not in self.df_datatoplot.columns and '[83] N2_150slm_Readout in slm' not in self.df_datatoplot.columns)):
                ax4.set_visible(False)

            # Legende erstellen
            self.plot_canvas.ax.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, -0.15), fancybox=False, shadow=False, ncol=5)
            self.plot_canvas.figure.tight_layout()
            self.plot_canvas.canvas.draw()
    def update_plot_multiple(self):
        # Überprüfen, ob `self.checkboxes` existiert und gültige QCheckBox-Objekte enthält
        if not hasattr(self, 'checkboxes') or not self.checkboxes or not all(isinstance(cb, QCheckBox) for cb in self.checkboxes.values()):
            return  # Beenden, wenn die Checkboxen nicht existieren oder ungültig sind

        self.plot_canvas.figure.clear()
        self.plot_canvas.ax = self.plot_canvas.figure.subplots()

        active_checkbox = next((cb for cb in self.checkboxes.values() if cb.isChecked()), None)

        if active_checkbox and not self.df_datatoplot.empty:
            column_map = {
                'Show Pressure': '[2] Chamber_Pressure_Readout in Torr',
                'Show Power': '[104] Power in kW',
                'Show T_Set': '[103] T_Set in °C',
                'Show T_Ist': '[109] T_Mdl3 in °C',
                'Show O\u2082': '[84] O2 Level in pu',
                'Show Ar-Fluss': '[20] Ar_20slm_Readout in slm',
                'Show N\u2082-30-Fluss': '[22] N2_30slm_Readout in slm',
                'Show N\u2082-150-Fluss': '[83] N2_150slm_Readout in slm'
            }

            column = column_map.get(active_checkbox.text())
            if column in self.df_datatoplot.columns:
                selected_files = [filename for filename, checkbox in self.file_checkboxes.items() if checkbox.isChecked()]
                filtered_data = self.df_datatoplot[self.df_datatoplot['Filename'].isin(selected_files)]

                # Entfernen von Zeilen mit fehlenden Werten im relevanten Plot
                filtered_data = filtered_data.dropna(subset=[column, 'Timestamp in s'])

                # Abtastung basierend auf dem ausgewählten Parameter
                if active_checkbox.text() in ['Show Pressure']:
                    filtered_data = filtered_data.iloc[::10, :]  # Jeder 10. Wert
                elif active_checkbox.text() in ['Show Power']:
                    filtered_data = filtered_data.iloc[::50, :]  # Jeder 50. Wert
                elif active_checkbox.text() in ['Show T_Set', 'Show T_Ist']:
                    filtered_data = filtered_data.iloc[::100, :]  # Jeder 100. Wert
                else:
                    filtered_data = filtered_data.iloc[::2, :]  # Jeder 2. Wert für andere

                if active_checkbox.text() == 'Show O\u2082':
                    if '[84] O2 Level in pu' in filtered_data.columns:
                        filtered_data['[84] O2 Level in ppm'] = filtered_data['[84] O2 Level in pu'] * 1e6
                        sns.scatterplot(x='Timestamp in s', y='[84] O2 Level in ppm', data=filtered_data, hue='Filename', ax=self.plot_canvas.ax)
                        self.plot_canvas.ax.set_yscale('log')
                        self.plot_canvas.ax.set_ylim(1E0, 1E6)
                        self.plot_canvas.ax.set_ylabel('O2 Level (ppm)')
                else:
                    sns.scatterplot(x='Timestamp in s', y=column, data=filtered_data, hue='Filename', ax=self.plot_canvas.ax)
                    self.plot_canvas.ax.set_yscale('linear')

                if active_checkbox.text() == 'Show Pressure':
                    self.plot_canvas.ax.set_ylim([700, 900])
                elif active_checkbox.text() == 'Show Power':
                    self.plot_canvas.ax.set_ylim([0, 100])
                elif active_checkbox.text() in ['Show T_Set', 'Show T_Ist']:
                    self.plot_canvas.ax.set_ylim([0, 1400])
                elif active_checkbox.text() in ['Show Ar-Fluss', 'Show N\u2082-30-Fluss', 'Show N\u2082-150-Fluss']:
                    self.plot_canvas.ax.set_ylim([0, 60])

                handles, labels = self.plot_canvas.ax.get_legend_handles_labels()
                if handles:
                    self.plot_canvas.ax.legend(title='Dateien', loc='upper center', bbox_to_anchor=(0.5, -0.20), fancybox=False, shadow=False, ncol=2)

        self.plot_canvas.figure.tight_layout(rect=[0, 0.05, 1, 0.95])
        self.plot_canvas.canvas.draw()

# Anwendung starten
app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
sys.exit(app.exec())