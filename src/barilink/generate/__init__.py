"""Population generation package."""

from barilink.generate.name_pools import (
    FEMALE_GIVEN_NAMES_HINDU,
    FEMALE_GIVEN_NAMES_MUSLIM,
    FEMALE_PREFIXES,
    MALE_GIVEN_NAMES_HINDU,
    MALE_GIVEN_NAMES_MUSLIM,
    MALE_PREFIXES,
    SURNAMES_HINDU,
    SURNAMES_HINDU_FEMALE_TITLES,
    SURNAMES_MUSLIM_FEMALE,
    SURNAMES_MUSLIM_MALE,
    compute_zipf_mandelbrot_weights,
)
from barilink.generate.population import (
    Household,
    Person,
    PopulationGenerator,
    generate_population,
)

__all__ = [
    "FEMALE_GIVEN_NAMES_HINDU",
    "FEMALE_GIVEN_NAMES_MUSLIM",
    "FEMALE_PREFIXES",
    "MALE_GIVEN_NAMES_HINDU",
    "MALE_GIVEN_NAMES_MUSLIM",
    "MALE_PREFIXES",
    "SURNAMES_HINDU",
    "SURNAMES_HINDU_FEMALE_TITLES",
    "SURNAMES_MUSLIM_FEMALE",
    "SURNAMES_MUSLIM_MALE",
    "Household",
    "Person",
    "PopulationGenerator",
    "compute_zipf_mandelbrot_weights",
    "generate_population",
]

