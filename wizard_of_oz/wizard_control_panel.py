from datetime import datetime
import ttkbootstrap as ttk
import time


class Section:
    def __init__(self, root, row, text):
        self.header = ttk.Label(root, text=text)
        self.header.config(font=("Arial", 14, "bold"))
        self.header.grid(row=row, column=0, padx=35, pady=35, sticky="ne")

        self.frame = ttk.Frame(root)
        self.frame.grid(row=row, column=1, padx=0, pady=35, sticky="ew")
        

class WizardControlPanel:
    def __init__(self, shared_state):
        self.shared_state = shared_state

        # You can change the title and theme here.
        self.root = ttk.Window(themename="darkly")
        self.root.title("Wizard of Oz")

        # Add your locations and templates here. Partial templates may include
        # one empty slot, denoted by an underscore '_'.
        self.locations = ["kitchen", "start", "couch1", "couch2", "couch3"]
        self.general_templates = [
            "Can you repeat the question?",
            "You're welcome!",
            "This is a _ template"
            ]
        self.templates_by_scenario = {
            1: ["Template 1.1", "Template 1.2"],
            2: ["Template 2.1", "Template 2.2"],
            3: ["Template 3.1", "Template 3.2"],
            }
        self.num_scenarios = len(self.templates_by_scenario)
        self.max_templates_per_row = 3

        # Initialize UI. Log section is created first so it can be referred to
        # by the other sections when they update the log view.
        self.create_log_section(6)
        self.create_go_to_section(0)
        self.create_scenario_section(1)
        self.create_speak_section(2)
        self.create_volume_section(3)
        self.create_icon_section(4)
        self.create_separator(5)
    
    #-----START-----------------------------------------------------------------

    def start(self):
        self.root.mainloop()

    #-----LOG-------------------------------------------------------------------

    def create_log_section(self, row):
        section = Section(self.root, row, "LOG")
        self.log = ttk.Label(section.frame, text="")
        self.log.pack(side="left")

    #-----GOTO------------------------------------------------------------------

    def create_go_to_section(self, row):
        section = Section(self.root, row, "GO TO")

        for location in self.locations:
            button = ttk.Button(
                section.frame,
                text=location,
                command=lambda l=location: self.set_location(l)
                )
            button.pack(side="left", padx=(0, 20))

    def set_location(self, location):
        self.reset_listening()
        self.reset_thinking()

        self.shared_state.set_location(location)
        self.log.config(text=f"Going to: {location}")

    #-----SCENARIO--------------------------------------------------------------

    def create_scenario_section(self, row):
        section = Section(self.root, row, "SCENARIO")

        scenario_var = ttk.IntVar()
        scenario_var.set(1)
        for i in range(1, self.num_scenarios+1):
            button = ttk.Radiobutton(
                section.frame,
                text=f"Scenario {i}",
                variable=scenario_var,
                value=i,
                command=lambda: self.set_scenario(scenario_var.get())
                )
            button.pack(side="left", padx=(0, 50))

    def set_scenario(self, scenario):
        self.shared_state.set_scenario(scenario)
        self.log.config(text=f"Selected scenario: {scenario}")
        self.update_templates(scenario)

    def update_templates(self, scenario):
        templates = self.general_templates + \
                    self.templates_by_scenario.get(scenario, [])
        
        # Remove existing template buttons.
        for widget in self.template_frame.winfo_children():
            widget.destroy()

        # Add new template buttons.
        for i, template in enumerate(templates):
            if "_" in template:
                button = ttk.Button(
                    self.template_frame,
                    text=template,
                    command=lambda t=template: self.fill_template(t)
                    )
            else:
                button = ttk.Button(
                    self.template_frame,
                    text=template,
                    command=lambda t=template: self.speak(message=t)
                    )
            row = i // self.max_templates_per_row
            column = i % self.max_templates_per_row
            button.grid(
                row=row, column=column, padx=(0, 20), pady=(0, 20), sticky="w"
                )

    #-----SPEAK-----------------------------------------------------------------

    def create_speak_section(self, row):
        section = Section(self.root, row, "SPEAK")

        self.text_input = ttk.Entry(section.frame)
        self.text_input.grid(
            row=0, column=0, padx=(0, 20), pady=(0, 20), sticky="ew"
            )
        section.frame.columnconfigure(0, weight=1)
        self.text_input.bind("<Return>", self.speak)

        submit_button = ttk.Button(
            section.frame,
            text="Submit",
            bootstyle="success",
            command=self.speak
            )
        submit_button.grid(
            row=0, column=1, padx=(0, 20), pady=(0, 20), sticky="w"
            )
        
        submit_listening_button = ttk.Button(
            section.frame,
            text="Submit and Listen",
            bootstyle="success",
            command=self.speak_and_listen
        )
        submit_listening_button.grid(
            row=0, column=2, padx=(0, 20), pady=(0, 20), sticky="w"
        )

        # Create a separate frame for the template buttons.
        self.template_frame = ttk.Frame(section.frame)
        self.template_frame.grid(
            row=1, column=0, columnspan=self.max_templates_per_row, sticky="ew"
            )

        # Start with templates for scenario 1.
        self.update_templates(1)

    def speak(self, event=None, message=None):
        if message is None:
            message = self.text_input.get()
            if not message:
                self.log.config(text="Error: Empty text field")
                return
            
        self.reset_thinking()
        self.reset_listening()

        self.shared_state.set_wizard_speech(message)
        self.text_input.delete(0, ttk.END)
        self.log.config(text=f"You said: {message}")

    def speak_and_listen(self, event=None, message=None):
        if message is None:
            message = self.text_input.get()
            if not message:
                self.log.config(text="Error: Empty text field")
                return
            
        self.speak(event, message)
        time.sleep(len(message.split()) / 2)
        self.listening_var.set(True)
        self.toggle_listening()

    def fill_template(self, template):
        slot_index = template.find("_")
        text = template.replace("_", "")

        self.text_input.delete(0, ttk.END)  
        self.text_input.insert(0, text) 
        
        self.text_input.icursor(slot_index)
        self.text_input.focus()

    #-----VOLUME----------------------------------------------------------------

    def create_volume_section(self, row):
        section = Section(self.root, row, "VOLUME")

        self.volume_var = ttk.IntVar()
        volume_slider = ttk.Scale(
            section.frame,
            from_=0, to=10,
            orient="horizontal",
            variable=self.volume_var,
            command=lambda x: self.volume_var.set(round(float(x)))
        )
        volume_slider.grid(row=0, column=0, sticky="ew", padx=(0, 20))
        section.frame.columnconfigure(0, weight=1)

        # Display the slider's current value.
        volume_label = ttk.Label(section.frame, text="0")
        volume_label.grid(row=0, column=1, padx=(0, 20))

        # Update the label if the slider moves.
        self.volume_var.trace(
            "w",
            lambda *args: volume_label.config(text=str(self.volume_var.get()))
            )

        volume_button = ttk.Button(
            section.frame,
            text="Set volume",
            bootstyle="success",
            command=self.set_volume
            )
        volume_button.grid(row=0, column=2, padx=(0, 20))

    def set_volume(self):
        volume = self.volume_var.get()
        self.shared_state.set_volume(volume)
        self.log.config(text=f"Set volume to: {volume}")

    #-----ICON------------------------------------------------------------------

    def create_icon_section(self, row):
        section = Section(self.root, row, "ICON")

        self.listening_var = ttk.BooleanVar()
        listening_button = ttk.Checkbutton(
            section.frame,
            bootstyle="round-toggle",
            text="Listening",
            variable=self.listening_var,
            command=self.toggle_listening
            )
        listening_button.pack(side="left", padx=(0, 40))

        self.thinking_var = ttk.BooleanVar()
        thinking_button = ttk.Checkbutton(
            section.frame,
            bootstyle="round-toggle",
            text="Thinking",
            variable=self.thinking_var,
            command=self.toggle_thinking
            )
        thinking_button.pack(side="left", padx=(0, 40))

    def toggle_listening(self):
        self.reset_thinking()
        self.shared_state.toggle_listening()
        self.log.config(text=f"Set listening to: {self.listening_var.get()}")

    def toggle_thinking(self):
        self.reset_listening()
        self.shared_state.toggle_thinking()
        self.log.config(text=f"Set thinking to: {self.thinking_var.get()}")

    def reset_thinking(self):
        if self.thinking_var.get():
            self.thinking_var.set(False)
            self.shared_state.toggle_thinking()
            self.log.config(text=f"Set thinking to: {False}")

    def reset_listening(self):
        if self.listening_var.get():
            self.listening_var.set(False)
            self.shared_state.toggle_listening()
            self.log.config(text=f"Set listening to: {False}")

    #-----SEPARATOR-------------------------------------------------------------

    def create_separator(self, row):
        separator = ttk.Separator(self.root, orient="horizontal")
        separator = ttk.Frame(self.root, height=1, relief="flat", style="light")
        separator.grid(row=row, columnspan=2, sticky="ew")
