from customtkinter import *
import threading

from local_llm import interpret_command
from ahk_generator import generate_ahk
from executor import run_ahk
from confirm_dialog import confirm_action
from mode_executor import execute_mode
from modes import MODES

set_appearance_mode("dark")

app = CTk()
app.geometry("600x420")
app.title("Local AI Assistant")

entry = CTkEntry(app, placeholder_text="Enter command...")
entry.pack(padx=20, pady=10, fill="x")

logbox = CTkTextbox(app, height=280)
logbox.pack(padx=20, pady=10, fill="both", expand=True)


def log(message: str):
    logbox.insert("end", message + "\n")
    logbox.see("end")


def handle_command(text: str):
    try:
        lowered = text.lower().strip()

        if lowered.endswith("mode"):
            mode = lowered.replace("mode", "").strip()
            if mode in MODES:
                command = {
                    "action": "open_mode",
                    "params": {"mode": mode}
                }
                app.after(0, lambda: confirm_and_execute(command))
                return

        command = interpret_command(text)
        app.after(0, lambda: confirm_and_execute(command))

    except Exception as err:
        log(f"❌ {err}")


def submit():
    text = entry.get().strip()
    if not text:
        return

    log(f"> {text}")
    entry.delete(0, "end")

    threading.Thread(
        target=handle_command,
        args=(text,),
        daemon=True
    ).start()


CTkButton(app, text="Run", command=submit).pack(pady=10)


def confirm_and_execute(command: dict):
    try:
        action = command["action"]
        params = command["params"]

        if not confirm_action(action, params):
            log("❌ Cancelled")
            return

        if action == "open_mode":
            execute_mode(params["mode"])
            log(f"✅ Mode '{params['mode']}' activated")
            return

        ahk_script = generate_ahk(command)
        run_ahk(ahk_script)
        log("✅ Command executed")

    except Exception as err:
        log(f"❌ {err}")


app.mainloop()
