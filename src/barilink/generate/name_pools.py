"""Canonical name pools and distribution weights for rural Bangladeshi population generation.

All given names are stored in their clean, canonical romanised form.
Honorific prefixes (Md., Mst., etc.) are stored in isolated collections and
never embedded directly in the clean ground-truth given names.
"""

from typing import Final, Sequence

import numpy as np

# Female honorific prefixes (stored separately, to be introduced in corruption step)
FEMALE_PREFIXES: Final[list[str]] = ["Mst.", "Most.", "Mosammat"]

# Male honorific prefixes (stored separately, to be introduced in corruption step)
MALE_PREFIXES: Final[list[str]] = ["Md.", "Mohammad", "Mohd."]

# Muslim Female Given Names (115 canonical romanised names)
FEMALE_GIVEN_NAMES_MUSLIM: Final[list[str]] = [
    "Rahima",
    "Fatema",
    "Ayesha",
    "Nasima",
    "Shahida",
    "Rokeya",
    "Momtaz",
    "Salma",
    "Rina",
    "Parvin",
    "Jesmin",
    "Shefali",
    "Laily",
    "Kulsum",
    "Taslima",
    "Morium",
    "Jannat",
    "Amena",
    "Halima",
    "Kohinoor",
    "Sufia",
    "Beauty",
    "Bilkis",
    "Hasina",
    "Khaleda",
    "Shirin",
    "Jahanara",
    "Rozina",
    "Sabina",
    "Nazma",
    "Rehana",
    "Farida",
    "Minara",
    "Rubina",
    "Asma",
    "Anwara",
    "Monira",
    "Lucky",
    "Baby",
    "Sharmin",
    "Sumi",
    "Aklima",
    "Maya",
    "Shapla",
    "Parul",
    "Bithi",
    "Sheuli",
    "Jharna",
    "Poly",
    "Mukta",
    "Laboni",
    "Ruma",
    "Shampa",
    "Tanjina",
    "Nargis",
    "Shilpi",
    "Alo",
    "Champa",
    "Rita",
    "Dolly",
    "Runu",
    "Selina",
    "Shahnaz",
    "Marufa",
    "Ferdousi",
    "Nurjahan",
    "Rabeya",
    "Aleya",
    "Saleha",
    "Maleka",
    "Jaheda",
    "Hafiza",
    "Hamida",
    "Rashida",
    "Momena",
    "Saheda",
    "Tahmina",
    "Najma",
    "Kamrun",
    "Hosne Ara",
    "Meherun",
    "Shamsun",
    "Afroza",
    "Suraiya",
    "Nahid",
    "Shamima",
    "Rumana",
    "Sadia",
    "Nusrat",
    "Farzana",
    "Sumaiya",
    "Tania",
    "Sultana",
    "Mahmuda",
    "Habiba",
    "Sayeeda",
    "Munni",
    "Shanta",
    "Tumpa",
    "Kakoli",
    "Shimul",
    "Chobi",
    "Kona",
    "Mimi",
    "Mita",
    "Popy",
    "Sonia",
    "Bristi",
    "Nipa",
    "Munira",
    "Nahar",
    "Zannatul",
    "Shahana",
    "Rahela",
    "Shajeda",
]

# Muslim Male Given Names (114 canonical romanised names)
MALE_GIVEN_NAMES_MUSLIM: Final[list[str]] = [
    "Abdul Karim",
    "Mohammad Ali",
    "Rafiqul Islam",
    "Abul Kashem",
    "Shahidul",
    "Jalal Uddin",
    "Abdur Rahman",
    "Habibur Rahman",
    "Mizanur Rahman",
    "Nurul Islam",
    "Aminul Islam",
    "Jahangir Alam",
    "Shah Alam",
    "Kabir Hossain",
    "Delwar Hossain",
    "Monir Hossain",
    "Anisur Rahman",
    "Faruk Hossain",
    "Nazrul Islam",
    "Shafiqul Islam",
    "Sirajul Islam",
    "Mozammel Haque",
    "Azizul Haque",
    "Shamsul Haque",
    "Mokbul Hossain",
    "Golam Mostafa",
    "Tariqul Islam",
    "Ashraful Islam",
    "Saiful Islam",
    "Kamrul Islam",
    "Zahirul Islam",
    "Badsha Mia",
    "Lal Mia",
    "Kala Mia",
    "Chand Mia",
    "Suruj Mia",
    "Bachchu Mia",
    "Rustam Ali",
    "Osman Ali",
    "Shawkat Ali",
    "Liakat Ali",
    "Yunus Ali",
    "Yusuf Ali",
    "Idris Ali",
    "Yakub Ali",
    "Kashem Ali",
    "Hashem Ali",
    "Soleman Ali",
    "Ismail Hossain",
    "Ibrahim Ali",
    "Khalilur Rahman",
    "Latifur Rahman",
    "Fazlur Rahman",
    "Harun-or-Rashid",
    "Bazlur Rahman",
    "Motiur Rahman",
    "Shafiul Alam",
    "Ziaur Rahman",
    "Alim Uddin",
    "Nasir Uddin",
    "Anwar Hossain",
    "Akbar Ali",
    "Asaduzzaman",
    "Babul Mia",
    "Enamul Haque",
    "Feroz Ahmed",
    "Gias Uddin",
    "Hamidul Islam",
    "Imran Hossain",
    "Jashim Uddin",
    "Kamal Hossain",
    "Liaquat Hossain",
    "Mahbubur Rahman",
    "Naimur Rahman",
    "Obaidul Islam",
    "Palash Mia",
    "Quamrul Hasan",
    "Rezaul Karim",
    "Sohrab Hossain",
    "Tanvir Ahmed",
    "Uzzal Hossain",
    "Wahiduzzaman",
    "Zakir Hossain",
    "Shahjahan Ali",
    "Altaf Hossain",
    "Barkat Ali",
    "Chowdhury Mia",
    "Didarul Alam",
    "Eskander Ali",
    "Fazle Rabbi",
    "Golam Rabbani",
    "Hafizur Rahman",
    "Iqbal Hossain",
    "Jahidul Islam",
    "Khurshed Alam",
    "Lokman Hossain",
    "Maniruzzaman",
    "Nazim Uddin",
    "Omar Faruk",
    "Panir Hossain",
    "Quddus Mia",
    "Rashidul Hasan",
    "Sultan Ahmed",
    "Tofazzal Hossain",
    "Waliur Rahman",
    "Zillur Rahman",
    "Khorshed Alam",
    "Ataur Rahman",
    "Emdadul Haque",
    "Mamunur Rashid",
    "Shahabuddin",
    "Saidur Rahman",
]

# Muslim Surnames / Titles
SURNAMES_MUSLIM_FEMALE: Final[list[str]] = [
    "Khatun",
    "Begum",
    "Akter",
    "Bibi",
]

SURNAMES_MUSLIM_MALE: Final[list[str]] = [
    "Islam",
    "Hossain",
    "Uddin",
    "Mia",
    "Sheikh",
    "Sarkar",
    "Mondal",
    "Ali",
    "Ahmed",
    "Chowdhury",
]

# Hindu Female Given Names (36 names)
FEMALE_GIVEN_NAMES_HINDU: Final[list[str]] = [
    "Rina",
    "Gita",
    "Maya",
    "Pratima",
    "Saraswati",
    "Lakshmi",
    "Anjali",
    "Sandhya",
    "Sunita",
    "Shanti",
    "Bharati",
    "Rekha",
    "Aparna",
    "Shipra",
    "Bina",
    "Radha",
    "Purnima",
    "Shikha",
    "Sujata",
    "Champa",
    "Jharna",
    "Kalyani",
    "Sumitra",
    "Urmila",
    "Archana",
    "Minoti",
    "Pushpa",
    "Basanti",
    "Shova",
    "Kalpana",
    "Swapna",
    "Namita",
    "Ruma",
    "Shyamali",
    "Sampa",
    "Dipti",
]

# Hindu Male Given Names (36 names)
MALE_GIVEN_NAMES_HINDU: Final[list[str]] = [
    "Subhash",
    "Bipul",
    "Tapan",
    "Ranjit",
    "Nirmal",
    "Bishwajit",
    "Dulal",
    "Narayan",
    "Uttam",
    "Haradhan",
    "Gobinda",
    "Prodip",
    "Ashok",
    "Gopal",
    "Bikash",
    "Manoranjan",
    "Sudhir",
    "Sanjoy",
    "Kamal",
    "Dipak",
    "Amal",
    "Shankar",
    "Prabir",
    "Samir",
    "Babul",
    "Khokon",
    "Kartik",
    "Anil",
    "Sunil",
    "Sukumar",
    "Pabitra",
    "Barun",
    "Tarun",
    "Nitai",
    "Gouranga",
    "Madhab",
]

# Hindu Surnames / Titles
SURNAMES_HINDU: Final[list[str]] = [
    "Das",
    "Roy",
    "Biswas",
    "Sarkar",
    "Majumder",
    "Dey",
    "Bhowmik",
    "Adhikary",
    "Chakraborty",
    "Barman",
]

SURNAMES_HINDU_FEMALE_TITLES: Final[list[str]] = [
    "Rani",
    "Bala",
    "Das",
    "Roy",
    "Biswas",
    "Sarkar",
    "Dey",
    "Barman",
]


def compute_zipf_mandelbrot_weights(
    n: int, zipf_exponent: float = 1.1, zipf_offset: float = 3.0
) -> np.ndarray:
    """Compute normalized Zipf-Mandelbrot probability weights.

    Formula:
        P(k) proportional to (k + q)^(-s) for k = 1, 2, ..., n
    where:
        s = zipf_exponent
        q = zipf_offset

    Args:
        n: Number of elements in pool.
        zipf_exponent: Power-law slope (s).
        zipf_offset: Rank shift parameter (q) flattening the very top rank.

    Returns:
        1D numpy array of probabilities summing to 1.0.
    """
    if n <= 0:
        raise ValueError(f"Pool size n must be positive, got {n}")
    ranks = np.arange(1, n + 1, dtype=np.float64)
    raw_weights = (ranks + float(zipf_offset)) ** (-float(zipf_exponent))
    return raw_weights / np.sum(raw_weights)


def sample_name(
    pool: Sequence[str],
    weights: np.ndarray,
    rng: np.random.Generator,
) -> str:
    """Sample a name from the pool according to the provided probability weights.

    Args:
        pool: Sequence of canonical names.
        weights: Normalized probabilities matching the pool length.
        rng: NumPy random generator instance.

    Returns:
        Selected name string.
    """
    idx: int = int(rng.choice(len(pool), p=weights))
    return pool[idx]
