import customtkinter as ctk


def confirm_action(action: str, params: dict) -> bool:
    """Simple confirmation dialog before executing an action."""

    dialog = ctk.CTkToplevel()
    dialog.title("Confirm Action")
    dialog.geometry("360x260")
    dialog.resizable(False, False)
    dialog.grab_set()

    details = f"Action: {action}\n\nParameters:\n"
    for key, value in params.items():
        details += f"• {key}: {value}\n"

    label = ctk.CTkLabel(
        dialog,
        text=details,
        justify="left",
        wraplength=320
    )
    label.pack(padx=20, pady=20)

    user_choice = {"confirmed": False}

    def on_confirm():
        user_choice["confirmed"] = True
        dialog.destroy()

    def on_cancel():
        dialog.destroy()

    button_row = ctk.CTkFrame(dialog)
    button_row.pack(pady=10)

    ctk.CTkButton(
        button_row,
        text="Proceed",
        fg_color="green",
        command=on_confirm
    ).pack(side="left", padx=10)

    ctk.CTkButton(
        button_row,
        text="Cancel",
        fg_color="red",
        command=on_cancel
    ).pack(side="left", padx=10)

    dialog.wait_window()
    return user_choice["confirmed"]
