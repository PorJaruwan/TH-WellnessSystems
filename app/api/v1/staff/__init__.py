# app/api/v1/staff/__init__.py

from . import staff
# from . import staff_availabilities
from . import staff_departments
from . import staff_leave
from . import staff_locations
from . import staff_services
from . import staff_template
# from . import staff_unavailabilities
from . import staff_work_pattern

__all__ = [
    "staff",
    #"staff_availabilities",
    "staff_departments",
    "staff_leave",
    "staff_locations",
    "staff_services",
    "staff_template",
    #"staff_unavailabilities",
    "staff_work_pattern",
]
