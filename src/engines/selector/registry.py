"""
Selector Registry.

The registry provides a single access point for selector
profiles used by the Selector Engine.

Its responsibilities are:

- Register selector profiles.
- Retrieve selectors by semantic name.
- Validate selector existence.
- Isolate scraper implementations from selector storage.

The registry does not perform DOM queries.

It only manages selector definitions.
"""

from collections.abc import Mapping

from .profiles import GOOGLE_MAPS_PROFILE


class SelectorRegistry:
    """
    Central registry of selector profiles.
    """

    def __init__(self) -> None:

        self._profiles = {
            "google_maps": GOOGLE_MAPS_PROFILE,
        }

    def available_profiles(self) -> list[str]:
        """
        Return every registered profile.
        """

        return sorted(self._profiles.keys())

    def has_profile(
        self,
        profile: str,
    ) -> bool:
        """
        Check whether a profile exists.
        """

        return profile in self._profiles

    def profile(
        self,
        profile: str,
    ) -> Mapping[str, list[str]]:
        """
        Return an entire selector profile.
        """

        try:
            return self._profiles[profile]

        except KeyError as exc:

            raise ValueError(
                f"Unknown selector profile '{profile}'."
            ) from exc

    def selectors(
        self,
        profile: str,
        name: str,
    ) -> list[str]:
        """
        Return every selector associated with a semantic name.

        Example
        -------

        selectors(
            "google_maps",
            "website"
        )

        Returns

        [
            "...",
            "...",
            "..."
        ]
        """

        profile_data = self.profile(profile)

        try:
            return profile_data[name]

        except KeyError as exc:

            raise ValueError(
                f"Selector '{name}' not found "
                f"in profile '{profile}'."
            ) from exc

    def register(
        self,
        name: str,
        profile: Mapping[str, list[str]],
    ) -> None:
        """
        Register a new selector profile.

        Existing profiles are overwritten intentionally.

        This allows applications to provide customized
        selector implementations.
        """

        self._profiles[name] = dict(profile)