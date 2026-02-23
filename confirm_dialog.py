import customtkinter as ctk

def confirm_action(action: str, params: dict) -> bool:
    dialog = ctk.CTkToplevel()
    dialog.title("Confirm Automation")
    dialog.geometry("400x320")
    dialog.attributes("-topmost", True)
    dialog.grab_set()

    # Center dialog
    dialog.update_idletasks()
    width = dialog.winfo_width()
    height = dialog.winfo_height()
    x = (dialog.winfo_screenwidth() // 2) - (width // 2)
    y = (dialog.winfo_screenheight() // 2) - (height // 2)
    dialog.geometry(f'+{x}+{y}')

    header = ctk.CTkLabel(dialog, text="⚠ Confirm Action", font=ctk.CTkFont(size=18, weight="bold"))
    header.pack(pady=(20, 10))

    content_frame = ctk.CTkFrame(dialog, fg_color="gray20")
    content_frame.pack(padx=20, pady=10, fill="both", expand=True)

    text = f"Action: {action.upper()}\n\n"
    for k, v in params.items():
        text += f"• {k}: {v}\n"

    label = ctk.CTkLabel(content_frame, text=text, justify="left", font=ctk.CTkFont(family="Consolas", size=12))
    label.pack(padx=15, pady=15, anchor="w")

    result = {"ok": False}

    def proceed():
        result["ok"] = True
        dialog.destroy()

    def cancel():
        dialog.destroy()

    btns = ctk.CTkFrame(dialog, fg_color="transparent")
    btns.pack(pady=20)

    ctk.CTkButton(btns, text="Proceed", fg_color="#2ecc71", hover_color="#27ae60", text_color="white", width=120, command=proceed, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10)
    ctk.CTkButton(btns, text="Cancel", fg_color="#e74c3c", hover_color="#c0392b", text_color="white", width=120, command=cancel, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10)

    dialog.wait_window()
    return result["ok"]
