"""
Exceptions
Custom exception hierarchy for PlanX3D.

All library-specific exceptions inherit from PlanX3DError so callers
can catch a single base type or handle individual failure modes.
"""


class PlanX3DError(Exception):
    """Base exception for all PlanX3D errors."""


class ImageProcessingError(PlanX3DError):
    """Raised when an image cannot be read, decoded, or processed."""


class ConfigError(PlanX3DError):
    """Raised when a configuration file is missing, malformed, or has invalid values."""


class BlenderError(PlanX3DError):
    """Raised when a Blender invocation or Blender-related operation fails."""
