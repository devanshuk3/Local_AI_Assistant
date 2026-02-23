from customtkinter import *
import threading

from local_llm import interpret_command
from ahk_generator import generate_ahk, generate_multi_step_ahk
from executor import run_ahk
from confirm_dialog import confirm_action
from mode_executor import execute_mode
from modes import MODES
from rule_parser import try_rule_based_parse


# ---------------- APP SETUP ----------------
set_appearance_mode("dark")
set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class App(CTk):
    def __init__(self):
        super().__init__()

        self.title("AI Local Assistant")
        self.geometry("850x500")

        # set grid layout 1x2
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # create sidebar frame with widgets
        self.sidebar_frame = CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        
        self.logo_label = CTkLabel(self.sidebar_frame, text="AI ASSISTANT", font=CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.status_label = CTkLabel(self.sidebar_frame, text="● Status: Ready", text_color="green", font=CTkFont(size=12))
        self.status_label.grid(row=1, column=0, padx=20, pady=10)

        self.appearance_mode_label = CTkLabel(self.sidebar_frame, text="Appearance:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))
        self.appearance_mode_optionemenu.set("Dark")

        # create main frame
        self.main_frame = CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        # logbox in main frame
        self.logbox = CTkTextbox(self.main_frame, font=CTkFont(family="Consolas", size=13))
        self.logbox.grid(row=0, column=0, sticky="nsew", pady=(0, 20))

        # input frame
        self.input_frame = CTkFrame(self.main_frame, fg_color="transparent")
        self.input_frame.grid(row=1, column=0, sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.entry = CTkEntry(self.input_frame, placeholder_text="Type a command (e.g., 'open chrome and search cats')", font=CTkFont(size=14))
        self.entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.entry.bind("<Return>", lambda event: self.submit())

        self.run_button = CTkButton(self.input_frame, text="Execute", width=100, command=self.submit, font=CTkFont(weight="bold"))
        self.run_button.grid(row=0, column=1)

    def change_appearance_mode_event(self, new_appearance_mode: str):
        set_appearance_mode(new_appearance_mode)

    def log(self, msg, color=None):
        self.logbox.insert("end", msg + "\n")
        self.logbox.see("end")

    def set_status(self, text, color="white"):
        self.status_label.configure(text=f"● Status: {text}", text_color=color)

    def submit(self):
        text = self.entry.get().strip()
        if not text:
            return

        self.log(f"> {text}")
        self.set_status("Thinking...", "orange")

        threading.Thread(
            target=handle_command,
            args=(text, self),
            daemon=True
        ).start()

        self.entry.delete(0, "end")

app = App()

# ---------------- COMMAND REPAIR ----------------
def repair_steps(command, user_text):
    """Fix missing params in multi-step commands."""
    if "steps" not in command:
        return command

    text = user_text.lower()

    # Simple keyword mapping for common apps
    app_keywords = {
        "chrome": "chrome",
        "google": "chrome",
        "notepad": "notepad",
        "edit": "notepad",
        "edge": "msedge",
        "browser": "browser"
    }

    for step in command["steps"]:
        if step["action"] == "open_app" and "app" not in step["params"]:
            for kw, app_name in app_keywords.items():
                if kw in text:
                    step["params"]["app"] = app_name
                    break

    return command


# ---------------- CORE HANDLER (BACKGROUND THREAD) ----------------
def handle_command(text, app_instance):
    try:
        lowered = text.lower().strip()

        # 1️⃣ MODE SHORTCUT (NO LLM)
        if lowered.endswith("mode"):
            mode_name = lowered.replace("mode", "").strip()
            if mode_name in MODES:
                command = {
                    "action": "open_mode",
                    "params": {"mode": mode_name}
                }
                app_instance.after(0, lambda: confirm_and_execute(command, app_instance))
                return

        # 2️⃣ RULE-BASED MULTI STEP
        rule_command = try_rule_based_parse(text)
        if rule_command:
            app_instance.after(0, lambda: confirm_and_execute(rule_command, app_instance))
            return

        # 3️⃣ LLM FALLBACK
        command = interpret_command(text)
        command = repair_steps(command, text)

        # Show Jarvis's thoughts
        if "thought" in command:
            app_instance.after(0, lambda: app_instance.log(f"🧠 Jarvis: {command['thought']}", color="cyan"))

        app_instance.after(0, lambda: confirm_and_execute(command, app_instance))

    except Exception as e:
        app_instance.after(0, lambda: app_instance.log(f"❌ Error: {e}"))
        app_instance.after(0, lambda: app_instance.set_status("Error", "red"))


# ---------------- UI THREAD EXECUTION ----------------
def confirm_and_execute(command, app_instance):
    try:
        app_instance.set_status("Executing...", "blue")
        
        # -------- MODE --------
        if command.get("action") == "open_mode":
            if not confirm_action("open_mode", command["params"]):
                app_instance.log("❌ Cancelled by user")
                app_instance.set_status("Ready", "green")
                return

            execute_mode(command["params"]["mode"])
            app_instance.log(f"✅ Mode '{command['params']['mode']}' activated")
            app_instance.set_status("Ready", "green")
            return

        # -------- MULTI STEP --------
        if "steps" in command:
            if not confirm_action("multi_step", {"steps": len(command["steps"])}):
                app_instance.log("❌ Cancelled by user")
                app_instance.set_status("Ready", "green")
                return

            ahk = generate_multi_step_ahk(command["steps"])
            run_ahk(ahk)
            app_instance.log("✅ Multi-step command executed")
            app_instance.set_status("Ready", "green")
            return

        # -------- SINGLE STEP --------
        action = command["action"]
        params = command["params"]

        if not confirm_action(action, params):
            app_instance.log("❌ Cancelled by user")
            app_instance.set_status("Ready", "green")
            return

        ahk = generate_ahk(command)
        run_ahk(ahk)
        app_instance.log("✅ Command executed")
        app_instance.set_status("Ready", "green")

    except Exception as e:
        app_instance.log(f"❌ Error: {e}")
        app_instance.set_status("Error", "red")

app.mainloop()
