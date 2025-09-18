from dataclasses import dataclass, field
from typing import Optional, Union


@dataclass(frozen=True)
class TestStep:
    """
    Base dataclass for all test step operations. These will be frozen, read-only objects used to represent a step or sequence in a test plan.

    All test steps inherit from this class and get automatic __init__, __repr__, __eq__, and other dataclass methods.

    This class serves as the foundation for all pseudo operations in test scenarios, providing consistent behavior and interface across different step types.
    """

    inputs: list[Union["TestStep", int]] = field(default_factory=list)

    def __str__(self):
        """
        Automatically generate string representation based on instance attributes.

        Returns a string in the format: ClassName(attr1=value1, attr2=value2, ...)

        :return: String representation of the test step
        :rtype: str
        """
        class_name = self.__class__.__name__
        attrs = []

        # Get all instance attributes (excluding private ones)
        for attr_name, attr_value in self.__dict__.items():
            if not attr_name.startswith("_"):
                attrs.append(f"{attr_name}={attr_value}")

        return f"{class_name}({', '.join(attrs)})"

    def __repr__(self):
        """
        Return the same string representation as __str__.

        :return: String representation of the test step
        :rtype: str
        """
        return self.__str__()

    @classmethod
    def get_keyword(cls) -> str:
        """
        Get the keyword for this test step class.

        This method returns the class name as the keyword used
        for parsing and registration in the test step registry.

        :return: The keyword identifier for this test step class
        :rtype: str
        """
        return cls.__name__
