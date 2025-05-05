"""
Optional extensions for FastChat controller.
This module is not required for basic functionality.
"""


from fastchat.serve.controller import Controller


class EnhancedController(Controller):
    """
    Enhanced version of FastChat's Controller with additional functionality.
    This is a placeholder for future extensions.
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize the enhanced controller."""
        super().__init__(*args, **kwargs)
