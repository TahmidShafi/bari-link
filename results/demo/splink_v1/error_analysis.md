# Linkage Error Analysis: splink_v1 (demo)

**Decision Threshold ($t_{cost}$):** `0.9900`  
**Total Ground-Truth True Pairs:** `1,424`  
**Total Scored Candidate Pairs:** `49,984`  
**Scored True Pairs:** `1,263`  
**Unblocked True Pairs (Missed by all rules):** `161` (11.31%)  
**Total False Merges ($p \ge t_{cost}$):** `63`  
**Total Candidate False Negatives ($p < t_{cost}$):** `560`  

---

## 1. Top 15 False Merges (Highest Probability Non-Matches)

Pairs of records representing different individuals that the model scored above the decision threshold:

| Rank | Record L | Record R | Prob | Name L | Name R | Guardian L | Guardian R | Village L | Village R | Phone L | Phone R | Mod L | Mod R |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `70a9befd55` | `fef8003a86` | 1.0000 | Most. Parvin | Most. Afroza Bibi | Shah Alam Ali | Md. Shah Alam Aloi | Mondal Para | Mondal Para | 01828649369 | 01328649369 | livelihood_support | livelihood_support |
| 2 | `237de7c9fa` | `b887d34970` | 1.0000 | Abdur Rahman Sarkar | Mohammad Bazlur Rahman Sarkar | Maneeruzzaman Ahmed | Maniruzzaman Ahmed | Dokkhin para | Dokkhin para | 01971089523 | — | livelihood_support | livelihood_support |
| 3 | `126a5e7b5d` | `635d1369d0` | 1.0000 | Kulsum Begum | Kamrun Bibi | Md. Alim Uddin Sarkar | Alim Uddin Sarkar | Majher Char | Majher Char | 018-8739-4442 | 01887394442 | upg_enrolment | livelihood_support |
| 4 | `168be29fff` | `8c3f0126eb` | 1.0000 | Yunus Ali Islam | Md. Ali Islam | Tofazzal Hossain Ahmed | Tofazzal Hossain Ahmed | Uttar Para | Uttar Para | — | 01999198213 | livelihood_support | livelihood_support |
| 5 | `778d846020` | `e4faf6af3b` | 1.0000 | Most. Baby Bibi | Rahima Begoom | Abdul Karim Sheikh | Abdul Karim Shiikh | Mondal Para | Mondal Para | 1340775372 | 01340775372 | livelihood_support | microfinance_group |
| 6 | `2ce6ef7afa` | `acd36d8726` | 0.9999 | Salma Bii | Maleka Khatun | Mohammad Alee Sarkar | Mohammad Ali Sarkar | Uttor Poro | Uttar Para | 01842675708 | 01842675708 | livelihood_support | microfinance_group |
| 7 | `395adf12eb` | `a646d732b8` | 0.9999 | Mohd. Mia Hamidul Islam | Momtaz Bigum | Aminul Islam Udin | Aminul Islam Uddeen | Uttar Para | Uttar para | 01460865019 | +880 1460865019 | livelihood_support | livelihood_support |
| 8 | `4bba750acc` | `bfba94b68c` | 0.9999 | Parvin Bibi | Lol Mia Sheikh | Nurul Islam sharkar | Nurul Islam Sarkar | Uttar Para | Uttar Para | 01501901198 | 01501901198 | upg_enrolment | livelihood_support |
| 9 | `0980847c1e` | `fd6c4fa7d6` | 0.9999 | Rafiqul Islam Sarkar | Most. Shahnaz Akter | Anisur Rahman Ali | Anisoor Rahman Ali | Dokkhin Para | Dokkhin para | 01449672418 | 01449672418 | livelihood_support | microfinance_group |
| 10 | `19dac83400` | `4f65d0c811` | 0.9998 | Nazrul Islam Mondal | Barkat Ali Mia | Mohd. Abul Kashem Islam | — | Uttar Para | Uttar Para | 01642260616 | 01642260616 | livelihood_support | livelihood_support |
| 11 | `59cbc5cb47` | `f573be251f` | 0.9996 | Tania Bibi | Rina Bibi | Shahidul Mia | Mohammad Shahidul Mia | Uttar Para | Uttar Para | 018-8495-1268 | — | livelihood_support | livelihood_support |
| 12 | `a104f1924e` | `e874c87a25` | 0.9995 | Mst. Rahima Khatun | Mosammat Beebi Fatema | Mohammad Ali Hossain | Md. oli Hossain | Uttar Para | Uttar Para | — | — | livelihood_support | livelihood_support |
| 13 | `3631cbb8e0` | `71394e1625` | 0.9995 | Golam Mostafa Sheikh | Jalal Uddin Mia | Kabir Hossain Chowdhury | Kabir Hossain Chowdhury | Dokkhin Para | Dokkhin Para | — | 01651347433 | livelihood_support | livelihood_support |
| 14 | `78713f9af5` | `b9b2bb8333` | 0.9994 | Mst. Munni Begum | Jannat Begoom | Lal Miah Hossain | Lal Mia Hossain | Uttar Para | Uttar Para | — | — | livelihood_support | livelihood_support |
| 15 | `dce16a66c5` | `fd8f02d517` | 0.9994 | Sirojul Islam Islam | Abdul Karim Islam | Shafiol Alam Chowdhury | Shafiul Alam Chowdhury | Uttar Para | Uttar Para | — | — | livelihood_support | livelihood_support |

---

## 2. Top 15 Candidate False Negatives (Lowest Probability True Matches)

Pairs of records representing the same individual that were captured by blocking rules but received low match probabilities:

| Rank | Record L | Record R | Prob | Name L | Name R | Guardian L | Guardian R | Village L | Village R | Phone L | Phone R | Mod L | Mod R |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `4ffaf88418` | `c7ebc15c92` | 0.0000 | Pooly Aktir | Poly Khatun | Md. Tanvir Ahmed Mondal | Mahd. Tanvir Ahmed Mondal | Uttar Para | Uttar Para | — | — | upg_enrolment | microfinance_group |
| 2 | `39f8b7206e` | `a104f1924e` | 0.0001 | Mosammat Rahima Akter | Mst. Rahima Khatun | Muhammad Ali Hossain | Mohammad Ali Hossain | Uttar para | Uttar Para | — | — | club_formation | livelihood_support |
| 3 | `035ed00ef8` | `1da8d811a1` | 0.0001 | Mosammat Kamrun Bigum | Kamrun Begum | Mohammad Tariqul Islam Chowdhury | Mahd. Tariqul Islam Chowdhury | Mondal Para | Mondal Para | — | 01364852646 | livelihood_support | microfinance_group |
| 4 | `1a1b55a349` | `304f97a60a` | 0.0001 | Rahima Aktir | Rohima Akter | Hashem Oli Sheikh | Bachchu Mia Chowdhury | Dokkhin Para | Dokkhin Para | 01800974779 | — | upg_enrolment | microfinance_group |
| 5 | `458192e3dd` | `f167ea3449` | 0.0002 | Reen Akter | Mosammat Rina Aktir | — | Habibur Rahman Hossain | Majher Char | Majher char | 01405098105 | — | upg_enrolment | microfinance_group |
| 6 | `415e0f5938` | `d40a55e595` | 0.0003 | Mst. Jesmeen Bibi | Mosammat Jesmin Khatun | Shamsul Haque Sheikh | Harun-or-Rashid Mondal | Mondal Para | MondalPara | — | — | club_formation | microfinance_group |
| 7 | `119959a3a9` | `c7ebc15c92` | 0.0003 | Poly Akter | Poly Khatun | Mohd. Tanvir Ahmed Mondal | Mahd. Tanvir Ahmed Mondal | Uttar Para | Uttar Para | — | — | livelihood_support | microfinance_group |
| 8 | `a1c6eaeaaf` | `f2c78d5a1c` | 0.0004 | Most. Jesmin Begoom | Jesmin Akter | — | Abdur Rehman Hossain | Uttor Poro | Uttar Para | — | — | microfinance_group | livelihood_support |
| 9 | `66ac075a6f` | `c88cd8589b` | 0.0004 | Rahima | Rahima Begum | Nazrul Islam Chowdhury | Md. Abul Kashem Islam | Dokkhin Para | — | — | — | livelihood_support | microfinance_group |
| 10 | `0ec14a5798` | `d04436c0c4` | 0.0006 | Shahida | Shahida Begum | Liakat Ali Islam | Mohammad Shah Alam Uddin | Majher Char | Majher Char | — | +880 1954534473 | club_formation | microfinance_group |
| 11 | `0ef31ebdbf` | `d90928b9b9` | 0.0008 | Amena | Mosammat Amena Bibi | Mohd. Sirajul Islam seikh | Mohammad Abdul Karim Mia | MajherChar | Majher Char | — | — | microfinance_group | upg_enrolment |
| 12 | `09aea8d229` | `15fcbcb4a9` | 0.0010 | Mosammat Rahima Begum | Rahima Bibi | — | Akbar Ali Sheikh | Dokkhin Para | Dokkhin Para | — | — | upg_enrolment | microfinance_group |
| 13 | `415b7ccfc0` | `49ef5eece2` | 0.0014 | Mst. Fatema Bibi | Most. Fatema Khatun | Abdul Karim Ahmed | — | Uttar Para | Uttar Para | — | — | microfinance_group | upg_enrolment |
| 14 | `4356183d15` | `eb606fb23c` | 0.0015 | Mst. Fatema Begum | Fatema Begum | Md. Idris Ali Mondal | Shawkat Ali Islam | Majher Char | Majher Char | — | — | microfinance_group | club_formation |
| 15 | `3d367f06f4` | `4d340ed72a` | 0.0018 | Jesmin | Mosammat Jesmeen Bibi | Mohammad Oli Ahmed | Habibur Rahman Islam | — | Dokkhin Para | — | — | livelihood_support | microfinance_group |

---

## 3. Unblocked True Pairs Analysis

A total of **161** true pairs (11.31%) were never generated as candidate pairs because they failed all 5 blocking rules.

### Sample of Unblocked True Pairs and Rule Failure Attribution

#### Case 1: `0160d61685` and `cc19b12f9c` (Person: `P_0001683`)
- **Record L:** Rita Begum | Guardian: Rafiqul Islam Chowdhury | Village: Mondal para | Phone: — | Age: —
- **Record R:** Md. Abul Kashem Ali | Guardian: Mosammat Rita Begum | Village: Mondal Para | Phone: — | Age: —
- **Blocking Rule Failure Reasons:**
  1. `given_first_skel + village_canon`: different first token skeleton ('rt' vs 'abl')
  2. `phone_norm`: different phone number ('nan' vs 'nan')
  3. `guardian_skeleton + village_canon`: different guardian skeleton ('rfqlslmchwdhry' vs 'rtbgm')
  4. `name_skeleton + union_raw`: different name skeleton ('rt' vs 'ablksml')
  5. `given_first_skel + birth_year_est`: different first token skeleton ('rt' vs 'abl')

#### Case 2: `01b4510e1f` and `b245b80544` (Person: `P_0001795`)
- **Record L:** Reena Barmanb | Guardian: Md. Sobhash Sarkar | Village: Uttar Para | Phone: — | Age: 50.0
- **Record R:** Mosommat Rina Barman | Guardian: Md. Sudhir Chakraborty | Village: — | Phone: — | Age: —
- **Blocking Rule Failure Reasons:**
  1. `given_first_skel + village_canon`: different first token skeleton ('rn' vs 'msmt'), different village ('uttarpara' vs 'nan')
  2. `phone_norm`: different phone number ('nan' vs 'nan')
  3. `guardian_skeleton + village_canon`: different guardian skeleton ('sbhsrkr' vs 'sdhrchkrbrty'), different village ('uttarpara' vs 'nan')
  4. `name_skeleton + union_raw`: different name skeleton ('rnbrmnb' vs 'msmtrnbrmn')
  5. `given_first_skel + birth_year_est`: different first token skeleton ('rn' vs 'msmt'), different birth year estimate (1974 vs None)

#### Case 3: `023138fc9c` and `54c163e799` (Person: `P_0002136`)
- **Record L:** Ali Hossain | Guardian: Mst. Fatema Begum | Village: Majher Char | Phone: — | Age: 36.0
- **Record R:** Fatema Begum | Guardian: Mohammad Ali Hossain | Village: Majher Char | Phone: — | Age: —
- **Blocking Rule Failure Reasons:**
  1. `given_first_skel + village_canon`: different first token skeleton ('al' vs 'ftm')
  2. `phone_norm`: different phone number ('nan' vs 'nan')
  3. `guardian_skeleton + village_canon`: different guardian skeleton ('ftmbgm' vs 'alhsn')
  4. `name_skeleton + union_raw`: different name skeleton ('alhsn' vs 'ftm')
  5. `given_first_skel + birth_year_est`: different first token skeleton ('al' vs 'ftm'), different birth year estimate (1989 vs None)

#### Case 4: `023138fc9c` and `85cf9f0176` (Person: `P_0002136`)
- **Record L:** Ali Hossain | Guardian: Mst. Fatema Begum | Village: Majher Char | Phone: — | Age: 36.0
- **Record R:** Mst. Fatema Begum | Guardian: Ali Hussain | Village: Majher Char | Phone: — | Age: 35.0
- **Blocking Rule Failure Reasons:**
  1. `given_first_skel + village_canon`: different first token skeleton ('al' vs 'ftm')
  2. `phone_norm`: different phone number ('nan' vs 'nan')
  3. `guardian_skeleton + village_canon`: different guardian skeleton ('ftmbgm' vs 'alhsn')
  4. `name_skeleton + union_raw`: different name skeleton ('alhsn' vs 'ftm')
  5. `given_first_skel + birth_year_est`: different first token skeleton ('al' vs 'ftm'), different birth year estimate (1989 vs 1990)

#### Case 5: `026aea4d72` and `bd3e75599d` (Person: `P_0003065`)
- **Record L:** Mst. Nazma Bibi | Guardian: — | Village: Uttar Para | Phone: — | Age: 30.0
- **Record R:** Most. Beebi Nazma | Guardian: Mohd. Kabir Hossain Uddin | Village: UttarPara | Phone: — | Age: —
- **Blocking Rule Failure Reasons:**
  1. `given_first_skel + village_canon`: different first token skeleton ('njm' vs 'b')
  2. `phone_norm`: different phone number ('nan' vs 'nan')
  3. `guardian_skeleton + village_canon`: different guardian skeleton ('nan' vs 'kbrhsndn')
  4. `name_skeleton + union_raw`: different name skeleton ('njm' vs 'bnjm')
  5. `given_first_skel + birth_year_est`: different first token skeleton ('njm' vs 'b'), different birth year estimate (1995 vs None)

#### Case 6: `02fd57b0c7` and `444fa897ed` (Person: `P_0000296`)
- **Record L:** Aktir Ayesha | Guardian: Abul-Kashem Ahmed | Village: Majher Char | Phone: — | Age: —
- **Record R:** oyesha Akter | Guardian: Oboidul Islam Hoesaqin | Village: Majher Char | Phone: — | Age: —
- **Blocking Rule Failure Reasons:**
  1. `given_first_skel + village_canon`: different first token skeleton ('aktr' vs 'ays')
  2. `phone_norm`: different phone number ('nan' vs 'nan')
  3. `guardian_skeleton + village_canon`: different guardian skeleton ('ablksmhmd' vs 'abdlslmhsqn')
  4. `name_skeleton + union_raw`: different name skeleton ('aktrys' vs 'ays')
  5. `given_first_skel + birth_year_est`: different first token skeleton ('aktr' vs 'ays')

#### Case 7: `02fd57b0c7` and `9f56a9e6be` (Person: `P_0000296`)
- **Record L:** Aktir Ayesha | Guardian: Abul-Kashem Ahmed | Village: Majher Char | Phone: — | Age: —
- **Record R:** Ayesha Akter | Guardian: Mohammed Obaidul Islam Hossain | Village: Majher char | Phone: 01438265328 | Age: 25.0
- **Blocking Rule Failure Reasons:**
  1. `given_first_skel + village_canon`: different first token skeleton ('aktr' vs 'ays')
  2. `phone_norm`: different phone number ('nan' vs '01438265328')
  3. `guardian_skeleton + village_canon`: different guardian skeleton ('ablksmhmd' vs 'mhmdbdlslmhsn')
  4. `name_skeleton + union_raw`: different name skeleton ('aktrys' vs 'ays')
  5. `given_first_skel + birth_year_est`: different first token skeleton ('aktr' vs 'ays'), different birth year estimate (None vs 1999)

#### Case 8: `0313ca4b95` and `538d6a0c25` (Person: `P_0002280`)
- **Record L:** Ayisha Akter | Guardian: Mohammad Jahangir Alam Ali | Village: Mondal Para | Phone: 01944951507 | Age: —
- **Record R:** Mosommat Ayesha Bibi | Guardian: Md. Jalal Uddin Mondal | Village: Mondal Para | Phone: — | Age: 58.0
- **Blocking Rule Failure Reasons:**
  1. `given_first_skel + village_canon`: different first token skeleton ('ays' vs 'msmt')
  2. `phone_norm`: different phone number ('01944951507' vs 'nan')
  3. `guardian_skeleton + village_canon`: different guardian skeleton ('jhngrlml' vs 'jldnmndl')
  4. `name_skeleton + union_raw`: different name skeleton ('ays' vs 'msmtys')
  5. `given_first_skel + birth_year_est`: different first token skeleton ('ays' vs 'msmt'), different birth year estimate (None vs 1967)

#### Case 9: `03ceaf9c00` and `3dd09d120e` (Person: `P_0003214`)
- **Record L:** Mitga Begum | Guardian: Habibur Rahman Uddeen | Village: Uttar Para | Phone: — | Age: 59.0
- **Record R:** Mita Begum | Guardian: Mohammad Altaf Hossain Mia | Village: Uttar Para | Phone: — | Age: 59.0
- **Blocking Rule Failure Reasons:**
  1. `given_first_skel + village_canon`: different first token skeleton ('mtg' vs 'mt')
  2. `phone_norm`: different phone number ('nan' vs 'nan')
  3. `guardian_skeleton + village_canon`: different guardian skeleton ('hbrhmndn' vs 'altfhsnm')
  4. `name_skeleton + union_raw`: different name skeleton ('mtg' vs 'mt')
  5. `given_first_skel + birth_year_est`: different first token skeleton ('mtg' vs 'mt')

#### Case 10: `048ee5ecd0` and `20e11409ac` (Person: `P_0008058`)
- **Record L:** Nurjahan Bibi | Guardian: Abul Kashem Mia | Village: Dokkhin Poro | Phone: — | Age: 26.0
- **Record R:** Bibi Nurjahan | Guardian: Md. Ahul Kashem Mia | Village: Dokkhin Para | Phone: — | Age: —
- **Blocking Rule Failure Reasons:**
  1. `given_first_skel + village_canon`: different first token skeleton ('nrjhn' vs 'b')
  2. `phone_norm`: different phone number ('nan' vs 'nan')
  3. `guardian_skeleton + village_canon`: different guardian skeleton ('ablksm' vs 'ahlksm')
  4. `name_skeleton + union_raw`: different name skeleton ('nrjhn' vs 'bnrjhn')
  5. `given_first_skel + birth_year_est`: different first token skeleton ('nrjhn' vs 'b'), different birth year estimate (1998 vs None)

