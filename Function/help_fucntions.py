from tkinter import Tk, messagebox
import warnings


def generate_warning(warning_header, msg):
    """
    This function generates the warning dialog box
    :param warning_header: The text to be shown on the dialog box header
    :param msg: the message to be shown in dialog box
    :return: None as it is GUI operation
    """

    # initialization
    window = Tk()
    window.withdraw()

    # generates message box
    messagebox.showwarning(warning_header, msg)

    # kills the gui
    window.deiconify()
    window.destroy()
    window.quit()


def check_slot_change(slot_name, new_value, old_value, correct_range):
    if not correct_range[0] <= new_value <= correct_range[1]:
        msg = "The parameter '{:}' must be between {:} - {:}"

        warnings.warn(msg)
        generate_warning("Warning: ", msg.format(slot_name, correct_range[0], correct_range[1]))
        return old_value
    else:
        return new_value
