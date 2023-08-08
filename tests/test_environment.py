from helpers import modified_environ
from venv_management.environment import preferred_drivers


def test_preferred_drivers():
    driver_names = ["driver1", "driver2", "driver3"]
    with modified_environ("VENV_MANAGEMENT_PREFERRED_DRIVERS"):
        assert preferred_drivers(driver_names) == driver_names


def test_preferred_drivers_with_preferred_drivers():
    driver_names = ["driver1", "driver2", "driver3"]
    with modified_environ(VENV_MANAGEMENT_PREFERRED_DRIVERS="driver3,driver1"):
        assert preferred_drivers(driver_names) == ["driver3", "driver1", "driver2"]


def test_non_existent_preferred_drivers():
    driver_names = ["driver1", "driver2", "driver3"]
    with modified_environ(VENV_MANAGEMENT_PREFERRED_DRIVERS="driver4"):
        assert preferred_drivers(driver_names) == driver_names
