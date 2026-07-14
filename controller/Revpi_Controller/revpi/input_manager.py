# ============================== #
# IMPORT LIBRARY
# ============================== #
from revpi.data_provider import read_all

# ============================== #
# DEFAULT DASHBOARD INPUT
# ============================== #

_dashboard_input = {

    # Push Button
    "PB1": False,
    "PB2": False,
    "PB3": False,
    "PB4": False,
    "PB5": False,
    "PB6": False,
    "PB7": False,
    "PB8": False,

    # Emergency
    "EM9": False,

    # Selector
    "SW10": False,
    "SW11": False,
    "SW12": False,
    "SW13": False,
    "SW14": False,

    # Sensor Digital
    "PROXIMITY": False,
}


# ============================== #
# UPDATE DASHBOARD INPUT
# ============================== #
def update_dashboard_input(data: dict):
    """
    Memperbarui input virtual dari Dashboard.
    Hanya key yang dikirim akan di-update.
    """

    global _dashboard_input

    _dashboard_input.update(data)


# ============================== #
# GET INPUT
# ============================== #
def get_input() -> dict:
    """
    Mengembalikan input sesuai mode.

    SW10 = OFF -> Hardware
    SW10 = ON  -> Dashboard
    """

    # ==========================
    # Selalu baca hardware
    # ==========================

    hardware = read_all()

    # ==========================
    # Mode Selector
    # ==========================

    dashboard_mode = bool(
        hardware.get("SW10", False)
    )

    # ==========================
    # Hardware Mode
    # ==========================

    if not dashboard_mode:

        return hardware

    # ==========================
    # Dashboard Mode
    # ==========================

    dashboard = hardware.copy()

    dashboard.update(_dashboard_input)

    return dashboard