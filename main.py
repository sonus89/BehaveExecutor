"""
        Description: A simple GUI tool to execute Behave tests
        Business Function: EOS Test Automation
        Author: Máté Gál
        Date-of-creation: 10-May-2022
        Contact: gal.mateo@gmail.com

        Not implemented features:
            - Loading sign while "scanning files"

        Known bugs:
            -
"""

import os
import subprocess
import sys
import parse
import logging
import threading
import tkinter as tk
from datetime import datetime
from tkinter import filedialog
logging.basicConfig(level=logging.INFO)


class MainFrame(tk.Frame):

    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.screen_width = root.winfo_screenwidth()
        self.screen_height = root.winfo_screenheight()
        # Set main frame resolution
        self.res_width = '854'
        self.res_height = '480'
        # Set MainFrame size and top left coordinates ( relative to whole screen size )
        root.geometry(str(self.res_width) + 'x' + str(self.res_height) + '+' +
                      str(int(0.1 * self.screen_width)) + '+' + str(int(0.1 * self.screen_height)))
        # Set MainFrame non-resizable
        root.resizable(False, False)
        # Set MainFrame title
        root.title('Behave Executor')
        # Set MainFrame icon
        # root.iconbitmap('schindler.ico')
        #
        self.display_menus()
        #
        self.features_folder = None
        #
        self.feature_names = []
        self.selected_features = []
        self.undefined_steps = {}
        self.filter_features_label = tk.Label(root, text="Features")
        self.filter_features_listbox = tk.Listbox(root, selectmode='extended', exportselection=False)
        #
        self.tag_names = []
        self.filtered_tags = []
        self.selected_tags = []
        self.filter_tags_label = tk.Label(root, text="Tags")
        self.filter_tags_listbox = tk.Listbox(root, selectmode='extended', exportselection=True)
        #
        self.scenario_names = []
        self.filtered_scenarios = []
        self.selected_scenarios = []
        self.filter_scenarios_label = tk.Label(root, text="Scenarios")
        self.filter_scenarios_listbox = tk.Listbox(root, selectmode="extended", exportselection=True)
        #
        self.behave_command = tk.StringVar()
        self.behave_command_label = tk.Label(root, text="Behave Command")
        self.behave_command_text = tk.Text(root)
        #
        self.instructions_label = tk.Label(root)
        self.display_instructions_label(state=True)
        #
        self.execute_test_button = tk.Button(root)
        #
        self.reset_button = tk.Button(root)
        #
        self.report_path_label = tk.Label(root)
        self.report_path = tk.StringVar()
        self.report_button = tk.Button(root)
        #
        self.report_path_entry = tk.Entry(root)
        self.report_checkbox_var = tk.BooleanVar()
        self.report_checkbox = tk.Checkbutton(root, variable=self.report_checkbox_var)
        self.is_json_added = False
        #
        self.about_window = None
        self.about_window_is_open = False
        #
        self.incomplete_feature_indexes = []

    """
            WIDGET METHODS
    """

    def display_menus(self):
        # Create Menubar
        menu_bar = tk.Menu(root)
        # Create PullDown Menu in Menubar
        file_menu = tk.Menu(menu_bar, tearoff=0, font=("Helvetica", 10))
        file_menu.add_command(label="Open", command=self.browse_features_path)
        file_menu.add_command(label="About", command=self.display_about_window)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.close)
        menu_bar.add_cascade(label="File", menu=file_menu)
        # display the menu
        root.config(menu=menu_bar)

    def display_instructions_label(self, state):
        if state:
            self.instructions_label.config(text='Please browse the behave "features" folder !', font=("Helvetica", 16))
            self.instructions_label.place(x=int(self.res_width) * 0.23, y=int(self.res_height) * 0.4)
        if not state:
            self.instructions_label.place_forget()

    def display_warning_label(self, state):
        warning_label = tk.Label(root)
        if state:
            warning_label.config(text='WARNING! One or more feature files contain undefined steps!',
                                 font=("Helvetica", 16), fg="red")
            warning_label.place(x=int(self.res_width) * 0.16, y=int(self.res_height) * 0.4)
        if not state:
            warning_label.place_forget()

    def display_scanning_label(self, state):
        scanning_label = tk.Label(root)
        if state:
            scanning_label.config(text='Scanning files ...', font=("Helvetica", 16))
            scanning_label.place(x=int(self.res_width) * 0.2, y=int(self.res_height) * 0.4)
        if not state:
            scanning_label.place_forget()

    def check_undefined_steps(self):
        MainFrame.clear_frame()
        self.display_scanning_label(state=True)
        self.incomplete_feature_indexes = []
        for i in range(0, len(self.feature_names)):
            amount_of_undefined_steps = self.has_undefined_steps(self.feature_names[i])
            if str(amount_of_undefined_steps) > str(0):
                self.incomplete_feature_indexes.extend(str(i))

    def browse_features_path(self):
        """ Open the File Explorer and select the features folder """
        self.features_folder = filedialog.askdirectory()
        if self.features_folder:
            logging.info("Features Folder Selected: '" + str(self.features_folder) + "'")
            self.feature_names = MainFrame.list_feature_file_names(folder=self.features_folder)
            if self.feature_names:
                # t1 = threading.Thread(target=self.check_undefined_steps)
                # t2 = threading.Thread(target=lambda state=True: self.display_warning_label(state=state))
                # t1.start()
                self.check_undefined_steps()
                if self.incomplete_feature_indexes:
                    MainFrame.clear_frame()
                    self.display_warning_label(state=True)
                    self.tk_wait(3000)
                    self.display_warning_label(state=False)
                #
                MainFrame.clear_frame()
                self.display_features_listbox(state=True, listbox_content=self.feature_names)
                for index in self.incomplete_feature_indexes:
                    self.filter_features_listbox.itemconfig(index, {'fg': 'red'})
                self.filtered_tags = []
                self.display_tags_listbox(state=False, listbox_content=None)
                self.filtered_scenarios = []
                self.display_scenarios_listbox(state=False, listbox_content=None)
                self.display_instructions_label(state=False)
                self.display_behave_command(state=False, command="")
                self.display_reset_button(state=False)
                self.display_path_browser(state=False)
            else:
                logging.warning("Selected folder contains no feature files!")
                MainFrame.clear_frame()
                self.display_instructions_label(state=True)
        if self.features_folder == '':
            logging.warning("No features folder selected!")
            MainFrame.clear_frame()
            self.display_instructions_label(state=True)

    def display_features_listbox(self, state, listbox_content):
        if state:
            self.filter_features_label.place(x=int(self.res_width) * 0.025, y=int(self.res_height) * 0.05)
            self.filter_features_listbox.place(
                x=int(self.res_width) * 0.025,
                y=int(self.res_height) * 0.1,
                height=300,
                width=260,
            )
            self.filter_features_listbox.delete(0, tk.END)
            listbox_content.sort()
            self.filter_features_listbox.insert(tk.END, *listbox_content)
            self.filter_features_listbox.bind('<<ListboxSelect>>',
                                              lambda event: self.on_select_features(event))
        if not state:
            self.filter_features_listbox.place_forget()
            self.filter_features_label.place_forget()
            self.filter_features_listbox.delete(0, tk.END)

    def display_tags_listbox(self, state, listbox_content):
        if state:
            self.filter_tags_label.place(x=int(self.res_width) * 0.347, y=int(self.res_height) * 0.05)
            self.filter_tags_listbox.place(
                x=int(self.res_width) * 0.347,
                y=int(self.res_height) * 0.1,
                height=300,
                width=260,
            )
            self.filter_tags_listbox.delete(0, tk.END)
            listbox_content.sort()
            self.filter_tags_listbox.insert(tk.END, *listbox_content)
            self.filter_tags_listbox.bind('<<ListboxSelect>>',
                                          lambda event: self.on_select_tags(event))
        if not state:
            self.filter_tags_listbox.place_forget()
            self.filter_tags_label.place_forget()
            self.filter_tags_listbox.delete(0, tk.END)

    def display_scenarios_listbox(self, state, listbox_content):
        if state:
            self.filter_scenarios_label.place(x=int(self.res_width) * 0.67, y=int(self.res_height) * 0.05)
            self.filter_scenarios_listbox.place(
                x=int(self.res_width) * 0.67,
                y=int(self.res_height) * 0.1,
                height=300,
                width=260,
            )
            self.filter_scenarios_listbox.delete(0, tk.END)
            listbox_content.sort()
            self.filter_scenarios_listbox.insert(tk.END, *listbox_content)
            self.filter_scenarios_listbox.bind('<<ListboxSelect>>',
                                               lambda event: self.on_select_scenarios(event))
        if not state:
            self.filter_scenarios_listbox.place_forget()
            self.filter_scenarios_label.place_forget()
            self.filter_scenarios_listbox.delete(0, tk.END)

    def on_select_features(self, event):
        # Get Selected Features
        self.selected_features = MainFrame.get_selected_listbox_items(self.filter_features_listbox)
        # Get Tags for selected Features
        self.filtered_tags = []
        for feature_file_name in self.selected_features:
            feature_file_path = os.path.join(self.features_folder, feature_file_name).replace('\\', '/')
            self.filtered_tags.extend(MainFrame.list_feature_file_tags(feature_file_path=feature_file_path))
        self.filtered_tags = MainFrame.remove_redundancies(self.filtered_tags)
        self.display_tags_listbox(state=True, listbox_content=self.filtered_tags)
        # Get Scenarios for selected Features
        self.filtered_scenarios = []
        for feature_file_name in self.selected_features:
            feature_file_path = os.path.join(self.features_folder, feature_file_name).replace('\\', '/')
            self.filtered_scenarios.extend(MainFrame.list_scenario_names(feature_file_path=feature_file_path))
        self.filtered_scenarios = MainFrame.remove_redundancies(self.filtered_scenarios)
        self.filtered_scenarios = MainFrame.reformat_scenario_names(self.filtered_scenarios)
        self.display_scenarios_listbox(state=True, listbox_content=self.filtered_scenarios)
        # Set Behave Command
        if self.selected_features:
            command = self.selection_to_behave_command(command_type="Features")
            self.display_behave_command(state=True, command=command)
            self.display_path_browser(state=True)
            self.display_reset_button(state=True)
            self.report_checkbox_var.set(False)
            self.json_switch()

    def on_select_tags(self, event):
        self.selected_tags = MainFrame.get_selected_listbox_items(self.filter_tags_listbox)
        self.selected_tags.sort()
        if self.selected_tags:
            command = self.selection_to_behave_command(command_type="Tags")
            self.display_behave_command(state=True, command=command)
            self.display_path_browser(state=True)
            self.display_reset_button(state=True)
            self.report_checkbox_var.set(False)
            self.json_switch()

    def on_select_scenarios(self, event):
        self.selected_scenarios = MainFrame.get_selected_listbox_items(self.filter_scenarios_listbox)
        self.selected_scenarios.sort()
        if self.selected_scenarios:
            command = self.selection_to_behave_command(command_type="Scenarios")
            self.display_behave_command(state=True, command=command)
            self.display_path_browser(state=True)
            self.display_reset_button(state=True)
            self.report_checkbox_var.set(False)
            self.json_switch()

    def display_behave_command(self, state, command):
        if state:
            # Place Textbox
            self.behave_command_label.place(x=int(self.res_width) * 0.025, y=int(self.res_height) * 0.75)
            self.behave_command_text.place(x=int(self.res_width) * 0.025, y=int(self.res_height) * 0.8)
            self.behave_command_text.config(state='normal', width=40, height=3)
            self.behave_command_text.delete('1.0', tk.END)
            self.behave_command_text.insert(tk.END, str(command))
            # Place Button
            self.execute_test_button.place(x=int(self.res_width) * 0.42, y=int(self.res_height) * 0.857)
            self.execute_test_button.config(text="Execute", command=self.execute_behave_command, bg="green", fg="white")
        if not state:
            self.behave_command_text.delete('1.0', tk.END)
            self.behave_command_text.place_forget()
            self.behave_command_label.place_forget()
            self.execute_test_button.place_forget()

    def display_reset_button(self, state):
        if state:
            self.reset_button.place(x=int(self.res_width) * 0.5, y=int(self.res_height) * 0.857)
            self.reset_button.config(text="Reset System", command=self.execute_behave_backgrounds)
        if not state:
            self.reset_button.place_forget()

    def display_path_browser(self, state):
        if state:
            #
            self.report_path_label.config(text="Report Path")
            self.report_path_label.place(x=int(self.res_width) * 0.5, y=int(self.res_height) * 0.75)
            #
            self.report_path_entry.insert(0, str(self.features_folder))
            #
            self.report_path_entry.place(x=int(self.res_width) * 0.505, y=int(self.res_height) * 0.8)
            self.report_path_entry.config(width=65, state='readonly')
            #
            self.report_button.place(x=int(self.res_width) * 0.91, y=int(self.res_height) * 0.86)
            self.report_button.config(text="Browse", command=self.browse_report_path)
            #
            self.report_checkbox.place(x=int(self.res_width) * 0.7, y=int(self.res_height) * 0.86)
            self.report_checkbox.config(text='Generate Test Report', command=self.json_switch)
        if not state:
            self.report_button.place_forget()
            self.report_path_label.place_forget()
            self.report_path_entry.place_forget()
            self.report_checkbox.place_forget()

    def browse_report_path(self):
        self.report_path = filedialog.askdirectory()
        self.report_path_entry.config(state='normal')
        self.report_path_entry.delete(0, tk.END)
        self.report_path_entry.insert(0, str(self.report_path))
        self.report_path_entry.config(state='readonly')

    def destroy_about_window(self):
        self.about_window.destroy()
        self.about_window_is_open = False

    def display_about_window(self):
        if not self.about_window_is_open:
            self.about_window = tk.Toplevel(root)
            self.about_window.geometry('220x120+' + str(root.winfo_x() + 100) + '+' + str(root.winfo_y() + 100))
            # Change directory to Script's path
            abspath = os.path.abspath(__file__)
            script_folder = os.path.dirname(abspath)
            os.chdir(script_folder)
            # self.about_window.iconbitmap('schindler.ico')
            self.about_window.title('About')
            label = tk.Label(self.about_window,
                             text="\nAll rights reserved by:\n©Schindler Aufzüge AG\n"
                                  "Contact: mate.gal@schindler.com\nVersion: Alpha")
            label.pack()
            button = tk.Button(self.about_window, text='OK', command=lambda: self.destroy_about_window())
            button.pack()
            self.about_window.wm_attributes("-topmost", 1)
            self.about_window_is_open = True

    @staticmethod
    def get_selected_listbox_items(listbox):
        selected_items = []
        for element in listbox.curselection():
            selected_items.append(listbox.get(element))
        return selected_items

    @staticmethod
    def clear_frame():
        logging.info("Destroying all widgets")
        try:
            for widget in MainFrame.winfo_children(root):
                widget.place_forget()
        except Exception as e:
            logging.info("Could not clear frame. Exception:\n" + str(e))

    """
            LISTING METHODS
    """

    @staticmethod
    def list_scenario_names(feature_file_path):
        """ List all scenario names of a feature file """
        scenario_names = []
        try:
            with open(feature_file_path) as file:
                for line in file:
                    if 'Scenario' in line:
                        scenario_names.append(line[:-1])
            return scenario_names
        except Exception as e:
            logging.error("The following exception occurred: " + str(e))
            logging.error("Could not open file: '" + str(feature_file_path) + "'")

    @staticmethod
    def list_feature_file_tags(feature_file_path):
        """ List all tags of a feature file """
        tags = []
        try:
            with open(feature_file_path) as file:
                for line in file:
                    words = line.split()
                    for word in words:
                        if word.startswith('@'):
                            tags.append(word)
            return tags
        except Exception as e:
            logging.error("The following exception occurred: " + str(e))
            logging.error("Could not open file: '" + str(feature_file_path) + "'")

    @staticmethod
    def list_feature_file_names(folder):
        """ List all feature file names in a given folder """
        features = []
        try:
            for file in os.listdir(folder):
                if file.endswith('.feature'):
                    features.append(file)
            return features
        except Exception as e:
            logging.error("The following exception occurred: " + str(e))
            logging.error("Could not open folder: '" + str(folder) + "'")

    """
            MISCELLANEOUS METHODS 
    """

    def execute_behave_backgrounds(self):
        os.chdir(self.features_folder)
        command = 'behave --tags @BehaveResetProcedure --no-skipped'
        os.system("start /B start cmd.exe @cmd /k " + str(command))

    def tk_wait(self, timeout):
        var = tk.IntVar()
        root.after(timeout, var.set, 1)
        print("Waiting " + str(timeout) + " milliseconds ...")
        root.wait_variable(var)

    def has_undefined_steps(self, feature_name):
        """ Receives a feature name and
            returns and integer that represents
            the amount of undefined steps """
        command = 'behave -k --dry-run --summary "' + str(feature_name) + '"'
        os.chdir(self.features_folder)
        try:
            output = subprocess.check_output(command, universal_newlines=True)
            words = output.split(' ')
            for i in range(0, len(words)):
                if 'undefined' in words[i]:
                    return words[i - 1]
        except Exception as e:
            logging.warning('The following exception occurred: ' + str(e))

    @staticmethod
    def pretty_print_the_dict(dictionary):
        """ Printing a dictionary readably """
        for key in dictionary:
            value = dictionary[key]
            print(key)
            for i in range(0, len(value)):
                print('\t' + value[i])

    @staticmethod
    def reformat_scenario_names(scenario_names):
        split_names = []
        for scenario_name in scenario_names:
            # split_names.extend(str(scenario_name).split('Scenario: ')[1:])
            if 'Scenario:' in scenario_name:
                split_names.extend(str(scenario_name).split('Scenario:')[1:])
            if 'Scenario Outline:' in scenario_name:
                split_names.extend(str(scenario_name).split('Scenario Outline:')[1:])
        formatted_names = []
        for name in split_names:
            formatted_names.append(name[1:])
        return formatted_names

    @staticmethod
    def subtract_lists(list1, list2):
        """ This method will remove the elements of the second list from the first list and return it """
        return [item for item in list1 if item not in list2]

    def json_switch(self):
        box_checked = self.report_checkbox_var.get()
        command = self.behave_command_text.get('1.0', tk.END)
        if box_checked and not self.is_json_added:
            self.is_json_added = True
            # add json switch
            now = datetime.now().strftime('%Y_%B_%d_%H%M%S')
            report_path = self.report_path_entry.get()
            json_extension = ' -f html -o ' + str(os.path.join(report_path, now).replace('\\', '/')) + '.html'
            command += json_extension
            command = command.rstrip()
            command = command.replace('\n', '')
            self.behave_command_text.delete('1.0', tk.END)
            self.behave_command_text.insert(tk.END, str(command))
        if not box_checked and self.is_json_added:
            self.is_json_added = False
            # remove json switch
            start_word = ' -f'
            end_word = '.html'
            start_index = command.find(start_word)
            end_index = command.find(end_word)
            json_switch = command[:start_index] + command[end_index+len(end_word):]
            command = json_switch.rstrip()
            self.behave_command_text.delete('1.0', tk.END)
            self.behave_command_text.insert(tk.END, str(command))

    def selection_to_behave_command(self, command_type):
        command = "behave -k"
        for feature_name in self.selected_features:
            command += ' "' + str(feature_name) + '"'
        if command_type == 'Features':
            pass
        if command_type == "Tags":
            command += ' --tags='
            for item in self.selected_tags:
                command += item + ','
            command = command[:-1]
        if command_type == "Scenarios":
            for item in self.selected_scenarios:
                command += ' --name="' + item + '"'
        return command

    def execute_behave_command(self):
        command = self.behave_command_text.get('1.0', tk.END)
        report_path = self.report_path_entry.get()
        is_report_generated = self.report_checkbox_var.get()
        now = datetime.now().strftime('%Y_%B_%d_%H%M%S')
        if is_report_generated:
            # os.chdir(report_path)
            # os.mkdir(now)
            os.chdir(self.features_folder)
            command += '-f json.pretty -o ' + str(os.path.join(report_path, now).replace('\\', '/')) + '.json'
            os.system("start /B start cmd.exe @cmd /k " + str(command))
        if not is_report_generated:
            os.system("start /B start cmd.exe @cmd /k " + str(command))

    @staticmethod
    def remove_redundancies(my_list):
        """ Remove duplicate list items and return the list """
        return list(dict.fromkeys(my_list))

    @staticmethod
    def close():
        sys.exit(0)


if __name__ == "__main__":
    root = tk.Tk()
    MainFrame(root).pack(side="bottom", fill="both", expand=True)
    root.mainloop()

