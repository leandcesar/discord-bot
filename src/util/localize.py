from __future__ import annotations

import typing as t

if t.TYPE_CHECKING:
    from disnake import Locale, LocalizationProtocol, LocalizationStore

__all__ = (
    "LocalizedStr",
    "Localization",
)

LocalizedStr = t.NewType("LocalizedStr", str)


class Localization:
    def __init__(self, protocol: LocalizationStore | LocalizationProtocol) -> None:
        self._i18n = protocol

    def get(
        self,
        default: str,
        locale: Locale,
        key: str,
        **placeholders: str,
    ) -> LocalizedStr:
        localizations = self._i18n.get(key)
        if localizations is None:
            return LocalizedStr(default.format(**placeholders))

        localized_string = localizations.get(locale.value, default)
        return LocalizedStr(localized_string.format(**placeholders))
