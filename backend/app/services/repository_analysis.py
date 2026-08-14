from app.schemas.repository import (
    LanguageBreakdown,
    RepositoryLanguagesResponse,
)


def calculate_language_breakdown(
    language_bytes: dict[str, int],
) -> RepositoryLanguagesResponse:
    """
    Convert GitHub language byte counts into a structured
    RepoPulse language breakdown with percentages.
    """

    # Calculate the total number of bytes across all detected languages.
    total_bytes = sum(language_bytes.values())

    # Some repositories may not have any detected programming languages.
    if total_bytes == 0:
        return RepositoryLanguagesResponse(
            total_bytes=0,
            languages=[],
        )

    languages: list[LanguageBreakdown] = []

    for language_name, bytes_count in language_bytes.items():
        # Calculate the percentage of the repository for this language.
        percentage = (bytes_count / total_bytes) * 100

        languages.append(
            LanguageBreakdown(
                name=language_name,
                bytes=bytes_count,
                percentage=round(percentage, 2),
            )
        )

    # Show the most-used languages first.
    languages.sort(
        key=lambda language: language.percentage,
        reverse=True,
    )

    return RepositoryLanguagesResponse(
        total_bytes=total_bytes,
        languages=languages,
    )