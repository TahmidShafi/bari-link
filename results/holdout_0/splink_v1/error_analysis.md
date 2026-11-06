# Linkage Error Analysis: splink_v1 (holdout_0)

**Decision Threshold ($t_{cost}$):** `9.00` (weight) / `0.998051` (probability)  
**Total Ground-Truth True Pairs:** `1,469`  
**Total Scored Candidate Pairs:** `45,507`  
**Scored True Pairs:** `1,298`  
**Unblocked True Pairs (Missed by all rules):** `171` (11.64%)  
**Total False Merges ($p \ge t_{cost}$):** `28`  
**Total Candidate False Negatives ($p < t_{cost}$):** `683`  

---

## 1. Top 15 False Merges (Highest Probability Non-Matches)

Pairs of records representing different individuals that the model scored above the decision threshold:

| Rank | Record L | Record R | Prob | Name L | Name R | Guardian L | Guardian R | Village L | Village R | Phone L | Phone R | Mod L | Mod R |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `bb5d6b5138` | `c0b06ce130` | 1.0000 | Nargis Akter | Shirin eBgum | Mohammad Habibur Rahman Uddin | Hobibur Rahman Uddin | Majher Char | Majher Char | 01948191641 | 01948191641 | livelihood_support | livelihood_support |
| 2 | `08881cc322` | `8a5127ca4c` | 1.0000 | Beauty Begum | Fatema Begum | Mohd. Mizanur Rahman Mondal | Mohammad Mizanur Rahman Mondal | Majher Char | Majher Char | 01969450858 | 8801969450858 | livelihood_support | livelihood_support |
| 3 | `22e743e34a` | `5a73f8298c` | 1.0000 | Kulsum Bibi | Tanjina Bibi | Jashim Uddin Sheikh | Jashim Uddin seikh | Dokkhin Para | Dokkhin Para | +880 1362554395 | 8801362554395 | microfinance_group | livelihood_support |
| 4 | `1e3ff2c681` | `70eee8307c` | 1.0000 | osma Akter | Mst. Jesmin Akter | Mohd. Jalal Uddin Hossain | Jalal Uddin Hossain | Mondal Para | Mondal Para | 01827137690 | 1827137690 | microfinance_group | livelihood_support |
| 5 | `b2bcba1e44` | `bccf253d5d` | 1.0000 | Mosammat Rokeya Begum | Mohammad Habibur Rahman Sarkar | Abdul Karim Hossain | Abdul Karim Hossain | Mondol Poro | Mondol Poro | 01977157800 | 01977157800 | upg_enrolment | livelihood_support |
| 6 | `d6be953e3f` | `ed09d4668c` | 1.0000 | Zahirul Islam Ali | Jalal Uddin Chowdhury | Md. Kola Mia Uddin | Md. Kala Mia ooddin | MondalPara | Mondal Para | 01465291137 | — | livelihood_support | livelihood_support |
| 7 | `f8aa05bf68` | `fe7f465165` | 1.0000 | Bachchu Mia Hossain | Meherun Bibi | Md. Khurshed Alam Chowdhury | Md. Khurshed Alam Chowdhury | Uttar Para | Uttar Para | 01559118967 | 01559118967 | livelihood_support | microfinance_group |
| 8 | `775cdd6333` | `ef573c67a3` | 0.9999 | Mosammat Jahanara Akter | oleya Bibi | Md. Badsha Mia Mondal | Mohammad Badsha Mia Mondal | Uttar Para | Uttar Para | 01576423410 | +880 1576423410 | microfinance_group | livelihood_support |
| 9 | `6dd202e22d` | `f813d4b24e` | 0.9999 | Mosammat Bilkis Begum | Faqrida Khaton | bAdul Kareem Mia | Mohammad bAdul Karim Mia | Uttar Para | Uttar Para | — | 01996755162 | livelihood_support | livelihood_support |
| 10 | `dc74e84c7f` | `edf8d0d88c` | 0.9999 | Mst. Sorkar Maya | Purnimo Rani | Khokon Dey | Mohd. Khokon Diy | Uttar Para | Uttor Poro | — | 019-1621-3104 | livelihood_support | livelihood_support |
| 11 | `08420952ec` | `40f587923d` | 0.9998 | Ranjit Adhikary | Mohd. Subhash Majumder | Dipak Dey | Md. Dipak Diy | MajherChar | Majher Char | 01713982480 | — | livelihood_support | livelihood_support |
| 12 | `8243319966` | `cd2d78c4fd` | 0.9996 | Shyamali Rni | Mst. Anjali Biswas | Tapan Dey | Tapan Dey | Uttar Para | Uttar Para | — | 01585854710 | upg_enrolment | livelihood_support |
| 13 | `251c901041` | `4bb254f2a8` | 0.9995 | Begum Jaheda | Nasima Khatun | Hashem Ali Sheikh | Hashem Ali Sheikh | Mondal Para | Mondal Para | — | — | livelihood_support | livelihood_support |
| 14 | `328c003ea8` | `facad38da3` | 0.9994 | Khalilur Rahman Mia | Uddin Rustam Ali | Nozrul Islam Mondal | Nazrol Islam Mondal | Uttar Para | Uttar Para | — | 1983061988 | livelihood_support | livelihood_support |
| 15 | `745b804b78` | `8fe05545ac` | 0.9993 | Mohammad Tofazzal Hossain Sarkar | Abul Kashem Ahmed | Yakub Ali Ali | Yakub Ali Ali | Mondal Para | Mondal para | 01463765731 | — | livelihood_support | livelihood_support |

---

## 2. Top 15 Candidate False Negatives (Lowest Probability True Matches)

Pairs of records representing the same individual that were captured by blocking rules but received low match probabilities:

| Rank | Record L | Record R | Prob | Name L | Name R | Guardian L | Guardian R | Village L | Village R | Phone L | Phone R | Mod L | Mod R |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `8a967e7caf` | `e29e91fc1e` | 0.0000 | Motaz Atker | Momtaz Akter | Zaheerul Islam Mondal | Hamidul Islam Islam | Dokkhin Para | Dokkhin Para | 01481822097 | — | microfinance_group | club_formation |
| 2 | `55720ad0e3` | `f792d45252` | 0.0001 | Popy Khatun | Poy Ater | Abul-Oashem Mondal | Mohd .Quamrul Hasan Mondal | Mondal Para | Mondal Para | — | — | microfinance_group | livelihood_support |
| 3 | `38659c057d` | `752f299669` | 0.0001 | Kohinoor Aktir | Kohinoor Khatun | Aminul Islam Mondal | Mohd. Jahangir Alam Ali | Mondal Para | Mondal Para | — | — | livelihood_support | microfinance_group |
| 4 | `57f42aee19` | `fd329c1177` | 0.0001 | Mst. Nasima Begum | Nasima Begoom | Shahidul Hossain | Shah Alam Miah | Uttar Para | Uttar Para | — | 01664398182 | livelihood_support | microfinance_group |
| 5 | `754f166428` | `ce217c7600` | 0.0002 | Mst. Rahima Khatun | Mst. Rahima Akter | Mahd. Yunus Ali Sheihk | Abdul Karim Ahmed | Mondal Para | Mondal Para | 01930285865 | 01430258865 | livelihood_support | microfinance_group |
| 6 | `9fb937c8d8` | `e58cda60eb` | 0.0004 | Mosammat Kulsum Akter | Klsum Begum | Monir Hossain Hsosain | Md. Abul Kashem Islam | Majher Char | MajherChar | — | — | microfinance_group | club_formation |
| 7 | `970368723c` | `9bcf207963` | 0.0004 | Rahima Akter | Mst. Rahima Begum | Mohammed Abul Kashem Sarkar | Abul Kashem Sarkar | Dokkhin Para | Dokkhin Para | — | — | livelihood_support | microfinance_group |
| 8 | `63b7834361` | `6a72dd71e3` | 0.0004 | Shahida katun | Most. Shahida Khatun | Waliur Rahman Mondal | Muhammad Waliur Rahman Mondal | Mondal Para | Mondal Para | — | — | microfinance_group | club_formation |
| 9 | `95d87aeadf` | `f3ab849784` | 0.0004 | SalmaA kter | Most. Salma Akter | Md. Shah Alam sharkar | Shahidul Sarkar | Dokkhin Para | Dokkhin Para | — | 1614595962 | club_formation | microfinance_group |
| 10 | `147cd7c4d6` | `472428f68c` | 0.0005 | Amena | Amina Begum | Shahidul Mondal | Nurul Islam Sheikh | Uttor Poro | UttarPara | 01553471968 | — | microfinance_group | livelihood_support |
| 11 | `2d0497a3e0` | `f3f856ff59` | 0.0006 | zesmin Akter | Mst. Jesmin | Mohd. Yunus Ali Sarkar | Jalal Uddeen Hossai | Mondal Para | Mondal Para | — | — | microfinance_group | upg_enrolment |
| 12 | `d9d41b04b0` | `e5bb6a96d8` | 0.0007 | Nasima Akter | Nasima Akter | Ibrahim Ali Hossain | Altaf Hussain Mondal | MondalPara | Mondal Para | — | — | microfinance_group | livelihood_support |
| 13 | `6a72dd71e3` | `c45ae61523` | 0.0007 | Most. Shahida Khatun | Mosammat Shahida Khatun | Muhammad Waliur Rahman Mondal | Waliur Rahman Mondal | Mondal Para | Mondal Para | — | — | club_formation | livelihood_support |
| 14 | `5640b839c8` | `fe1c69d29b` | 0.0007 | Mosammat Ayesha Akter | Ayesha Bibi | Mohammad Anisur Rahman Chowdhury | Jahangir Alam Mondal | Mondal Para | Mondal Para | — | — | microfinance_group | upg_enrolment |
| 15 | `8e8964b390` | `cd3683de8b` | 0.0008 | Nasima Khatun | Nasima | Nurul Islam Hossazin | Rafiqol Islam Sarkar | — | Majher char | 01987877147 | — | microfinance_group | upg_enrolment |

---

## 3. Unblocked True Pairs Analysis

A total of **171** true pairs (11.64%) were never generated as candidate pairs because they failed all 5 blocking rules.

### Sample of Unblocked True Pairs and Rule Failure Attribution

#### Case 1: `006cfe43bd` and `f63f840923` (Person: `P_0002168`)
- **Record L:** Mst. Rubina Bibi | Guardian: Liakat Ali Ali | Village: Uttar Para | Phone: — | Age: 50.0
- **Record R:** Mosammat Bibi Rubina | Guardian: Liakat Ali Ali | Village: — | Phone: — | Age: 49.0
- **Blocking Rule Failure Reasons:**
  1. `given_first_skel + village_canon`: different first token skeleton ('rbn' vs 'b'), different village ('uttarpara' vs 'nan')
  2. `phone_norm`: different phone number ('nan' vs 'nan')
  3. `guardian_skeleton + village_canon`: different village ('uttarpara' vs 'nan')
  4. `name_skeleton + union_raw`: different name skeleton ('rbn' vs 'brbn')
  5. `given_first_skel + birth_year_est`: different first token skeleton ('rbn' vs 'b'), different birth year estimate (1974 vs 1975)

#### Case 2: `0106bd5c82` and `57e4eed730` (Person: `P_0007656`)
- **Record L:** Md. Idris Ali Chowdhury | Guardian: Most. Morium Akter | Village: Majher Char | Phone: — | Age: 22.0
- **Record R:** Morium Akter | Guardian: Idris Ali Chowdhury | Village: Majher Char | Phone: 8801447353142 | Age: 25.0
- **Blocking Rule Failure Reasons:**
  1. `given_first_skel + village_canon`: different first token skeleton ('idrs' vs 'mrm')
  2. `phone_norm`: different phone number ('nan' vs '01447353142')
  3. `guardian_skeleton + village_canon`: different guardian skeleton ('mrmktr' vs 'idrslchwdhry')
  4. `name_skeleton + union_raw`: different name skeleton ('idrslchwdhry' vs 'mrm'), different union ('nan' vs 'Bidyananda')
  5. `given_first_skel + birth_year_est`: different first token skeleton ('idrs' vs 'mrm'), different birth year estimate (2001 vs 1998)

#### Case 3: `0106bd5c82` and `67a7f1c126` (Person: `P_0007656`)
- **Record L:** Md. Idris Ali Chowdhury | Guardian: Most. Morium Akter | Village: Majher Char | Phone: — | Age: 22.0
- **Record R:** Mast. Morium | Guardian: Mohd. Idris Ali Chowdhury | Village: Majher Char | Phone: — | Age: 25.0
- **Blocking Rule Failure Reasons:**
  1. `given_first_skel + village_canon`: different first token skeleton ('idrs' vs 'mst')
  2. `phone_norm`: different phone number ('nan' vs 'nan')
  3. `guardian_skeleton + village_canon`: different guardian skeleton ('mrmktr' vs 'idrslchwdhry')
  4. `name_skeleton + union_raw`: different name skeleton ('idrslchwdhry' vs 'mstmrm'), different union ('nan' vs 'Bidyananda')
  5. `given_first_skel + birth_year_est`: different first token skeleton ('idrs' vs 'mst'), different birth year estimate (2001 vs 1998)

#### Case 4: `0106bd5c82` and `b12372ff1e` (Person: `P_0007656`)
- **Record L:** Md. Idris Ali Chowdhury | Guardian: Most. Morium Akter | Village: Majher Char | Phone: — | Age: 22.0
- **Record R:** Mst. Moreeum Akter | Guardian: Ziaoor Rahman Hoissain | Village: Majher Char | Phone: — | Age: 24.0
- **Blocking Rule Failure Reasons:**
  1. `given_first_skel + village_canon`: different first token skeleton ('idrs' vs 'mrm')
  2. `phone_norm`: different phone number ('nan' vs 'nan')
  3. `guardian_skeleton + village_canon`: different guardian skeleton ('mrmktr' vs 'jrhmnhsn')
  4. `name_skeleton + union_raw`: different name skeleton ('idrslchwdhry' vs 'mrm'), different union ('nan' vs 'Bidyananda')
  5. `given_first_skel + birth_year_est`: different first token skeleton ('idrs' vs 'mrm'), different birth year estimate (2001 vs 2000)

#### Case 5: `01db4cb923` and `0d33a126f6` (Person: `P_0012079`)
- **Record L:** Mosommat Bibi Fatema | Guardian: — | Village: Majher Char | Phone: — | Age: 25.0
- **Record R:** Most. Fatema Bibi | Guardian: Latifur Rahman Uddin | Village: Majher char | Phone: — | Age: 24.0
- **Blocking Rule Failure Reasons:**
  1. `given_first_skel + village_canon`: different first token skeleton ('msmt' vs 'ftm')
  2. `phone_norm`: different phone number ('nan' vs 'nan')
  3. `guardian_skeleton + village_canon`: different guardian skeleton ('nan' vs 'ltfrhmndn')
  4. `name_skeleton + union_raw`: different name skeleton ('msmtbftm' vs 'ftm'), different union ('nan' vs 'Mahimaganj')
  5. `given_first_skel + birth_year_est`: different first token skeleton ('msmt' vs 'ftm'), different birth year estimate (1999 vs 2000)

#### Case 6: `01db4cb923` and `8feb7ad481` (Person: `P_0012079`)
- **Record L:** Mosommat Bibi Fatema | Guardian: — | Village: Majher Char | Phone: — | Age: 25.0
- **Record R:** phatema Bibi | Guardian: Latifur Rahman Uddin | Village: Majher Char | Phone: — | Age: 25.0
- **Blocking Rule Failure Reasons:**
  1. `given_first_skel + village_canon`: different first token skeleton ('msmt' vs 'ftm')
  2. `phone_norm`: different phone number ('nan' vs 'nan')
  3. `guardian_skeleton + village_canon`: different guardian skeleton ('nan' vs 'ltfrhmndn')
  4. `name_skeleton + union_raw`: different name skeleton ('msmtbftm' vs 'ftm'), different union ('nan' vs 'nan')
  5. `given_first_skel + birth_year_est`: different first token skeleton ('msmt' vs 'ftm'), different birth year estimate (1999 vs 2000)

#### Case 7: `01e9d0fafe` and `1f7d774bb7` (Person: `P_0011335`)
- **Record L:** Halima Akter | Guardian: Mohd. Zakeer Hossain Ali | Village: Mondal Para | Phone: — | Age: —
- **Record R:** Md. Zakir Hossain Ali | Guardian: Haleema Akter | Village: MondalPara | Phone: — | Age: 58.0
- **Blocking Rule Failure Reasons:**
  1. `given_first_skel + village_canon`: different first token skeleton ('hlm' vs 'jkr')
  2. `phone_norm`: different phone number ('nan' vs 'nan')
  3. `guardian_skeleton + village_canon`: different guardian skeleton ('jkrhsnl' vs 'hlmktr')
  4. `name_skeleton + union_raw`: different name skeleton ('hlm' vs 'jkrhsnl'), different union ('Chakirpashar' vs 'nan')
  5. `given_first_skel + birth_year_est`: different first token skeleton ('hlm' vs 'jkr'), different birth year estimate (None vs 1967)

#### Case 8: `022016654f` and `2bf77f4b2d` (Person: `P_0010902`)
- **Record L:** Begum Rahima | Guardian: Md. Abul Kashem Mia | Village: Uttar Para | Phone: 01552792372 | Age: —
- **Record R:** Rahima Begum | Guardian: Mohd. Idris oli Sheikh | Village: Uttar Para | Phone: 01982727984 | Age: 50.0
- **Blocking Rule Failure Reasons:**
  1. `given_first_skel + village_canon`: different first token skeleton ('bgm' vs 'rhm')
  2. `phone_norm`: different phone number ('01552792372' vs '01982727984')
  3. `guardian_skeleton + village_canon`: different guardian skeleton ('ablksm' vs 'idrslsk')
  4. `name_skeleton + union_raw`: different name skeleton ('bgmrhm' vs 'rhm')
  5. `given_first_skel + birth_year_est`: different first token skeleton ('bgm' vs 'rhm'), different birth year estimate (None vs 1974)

#### Case 9: `0290c7d00f` and `80e44d86fb` (Person: `P_0009791`)
- **Record L:** Mosommat Salma | Guardian: Anwar Hssian Chowdhury | Village: Uttar Para | Phone: — | Age: 50.0
- **Record R:** Monir Hossain Uddin | Guardian: Salma Begum | Village: Uttar Para | Phone: 01772493563 | Age: 51.0
- **Blocking Rule Failure Reasons:**
  1. `given_first_skel + village_canon`: different first token skeleton ('msmt' vs 'mnr')
  2. `phone_norm`: different phone number ('nan' vs '01772493563')
  3. `guardian_skeleton + village_canon`: different guardian skeleton ('anwrhsnchwdhry' vs 'slmbgm')
  4. `name_skeleton + union_raw`: different name skeleton ('msmtslm' vs 'mnrhsndn')
  5. `given_first_skel + birth_year_est`: different first token skeleton ('msmt' vs 'mnr'), different birth year estimate (1974 vs 1973)

#### Case 10: `029986908f` and `98f1946ea7` (Person: `P_0009306`)
- **Record L:** Mosommat Fatema Begum | Guardian: Mohd. Zaheerul Islam Ahmed | Village: Majher Char | Phone: 01401773420 | Age: 31.0
- **Record R:** Fatema Begum | Guardian: Hamidul Islam Sheikh | Village: Majher Char | Phone: 1893043673 | Age: 31.0
- **Blocking Rule Failure Reasons:**
  1. `given_first_skel + village_canon`: different first token skeleton ('msmt' vs 'ftm')
  2. `phone_norm`: different phone number ('01401773420' vs '01893043673')
  3. `guardian_skeleton + village_canon`: different guardian skeleton ('jhrlslmhmd' vs 'hmdlslmsk')
  4. `name_skeleton + union_raw`: different name skeleton ('msmtftm' vs 'ftm')
  5. `given_first_skel + birth_year_est`: different first token skeleton ('msmt' vs 'ftm')

