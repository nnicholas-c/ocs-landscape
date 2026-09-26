# Number check 2. Split name keys in the team map

Inputs are data/work/nc2_evidence.json (evidence, from pipeline/check_name_keys.py), data/work/nc2_class_A.json and data/work/nc2_class_B.json (two independent classifiers). Every number below is computed by pipeline/merge_name_keys.py, which also re-runs the flag query read-only on data/db/papers.sqlite. A name key is a last name plus first initial, such as 'sato k'. The team map is the stage 4 author graph, which holds only authors with an extended-set paper.

## 1. The count, reproduced

The query returns 149 name keys today, the same as flagged_keys_total in the evidence file and the 149 that the stage 4 grapher logged at 06:32 in deliverables/pitfalls_original_log.md. A key is flagged when more than one author record with that key has an extended-set paper and at least one of those records has a core paper. The rule lives in pipeline/graph.py log_split_person_candidates().

```sql
WITH ext AS (
        SELECT pa.author_id,
               MAX(p.core_set) AS has_core
        FROM paper_authors pa
        JOIN papers p ON p.paper_id = pa.paper_id
        WHERE p.extended_set = 1
        GROUP BY pa.author_id
    )
    SELECT a.name_key
    FROM ext JOIN authors a ON a.author_id = ext.author_id
    GROUP BY a.name_key
    HAVING COUNT(*) > 1 AND MAX(ext.has_core) = 1
    ORDER BY a.name_key;
```

## 2. Keys by OpenAlex ID status

Status is read from the records of each key that are in the team map. all_openalex means every such record has an OpenAlex author ID (identifier). all_name_only means none does, which is the case for arXiv-only authors. mixed means some do and some do not.

| status | flagged keys (of 149) | share | sampled keys (of 15) | final same_person | final different_people | final cannot_tell |
|---|---|---|---|---|---|---|
| all_openalex | 60 | 40 percent | 3 | 2 | 1 | 0 |
| mixed | 79 | 53 percent | 11 | 7 | 3 | 1 |
| all_name_only | 10 | 7 percent | 1 | 1 | 0 | 0 |

An all_openalex key cannot come from the stage 2 merge rule for name-only records, because OpenAlex itself gave its records different author IDs. So that rule can explain at most the 89 mixed or all_name_only keys.

## 3. The 15 sampled keys

The sample is 15 keys drawn at random from the 149 with seed 20260927 (pipeline/check_name_keys.py). The records column counts records in the team map, then all author records with the key. A and B are the two classifier labels. Final is their shared label, else cannot_tell.

| key | records (in map of all) | A | B | final | reason |
|---|---|---|---|---|---|
| ding e | 3 of 3 | same_person | same_person | same_person | All records are name-only 'Eric Ding' and every pair shares coauthor singh r (Rachee Singh) on photonic switching papers. |
| fu x | 2 of 3 | cannot_tell | cannot_tell | cannot_tell | 'Xing Fu' is someone else. The two 'Xin Fu' records share no coauthor, institution or route and their years do not overlap, so neither classifier could decide. |
| hu w | 2 of 3 | same_person | same_person | same_person | A5015039354 and name:hu w are both 'Weisheng Hu' and share coauthor sun w. A5000636579 is 'Weijin Hu', a different person. |
| inoue t | 3 of 3 | same_person | same_person | same_person | A5081996202 and name:inoue t are both 'Takeru Inoue' and share several coauthors (oki e, anazawa k, mano t). A5066816626 is 'Takashi Inoue'. |
| li y | 3 of 12 | same_person | same_person | same_person | The two 'Yang Li' records share coauthors and a Swinburne affiliation, but neither is in the team map. The records in the map (Yannanqi, Yupeng, Yinmei) are different people. |
| ma q | 2 of 3 | same_person | same_person | same_person | A5102968002 and name:ma q are both 'Qian Ma' with shared coauthors (dai d, hu y, lu y) and the same route. A5083422711 shares nothing and stays apart. |
| miles a | 2 of 2 | same_person | same_person | same_person | Both OpenAlex records share every coauthor and the University of Arizona affiliation on digital micromirror device (DMD) fiber switch papers, but the first names differ (Alexander, Arriel LaVena). |
| patterson d | 2 of 3 | same_person | same_person | same_person | A5077202069 (Google) and name:patterson d share coauthors jouppi n and young c on Google tensor processing unit (TPU) papers. A5101927146 (Berkeley, Roofline) is outside the map and shares nothing. |
| sato k | 2 of 2 | same_person | same_person | same_person | Both records are 'Ken-ichi Sato', share coauthor namiki s (Shu Namiki), and are on large optical circuit switch papers. |
| schmid s | 6 of 6 | same_person | same_person | same_person | All records are 'Stefan Schmid'. Four are tied by coauthors avin c and addanki v, and two (#2, #5) share only the name and route, so they were left undecided. |
| tang s | 2 of 3 | different_people | different_people | different_people | Three different first names (Shiwei, Shaojie, Sirui) with no shared coauthor, institution or route. |
| wang j | 4 of 11 | different_people | different_people | different_people | First names differ, except two 'Jian Wang' records at different institutions on different topics. The high-overlap pairs sit on the same paper, so they are two people. |
| xu y | 2 of 2 | different_people | different_people | different_people | 'Yue Xu' and 'Yelong Xu' share no coauthor, institution or route. |
| yang y | 3 of 10 | different_people | different_people | different_people | Every record has a different first name, and the only overlaps are common coauthor keys such as zhang y. |
| young c | 2 of 2 | same_person | same_person | same_person | Both records are 'Cliff Young' and share coauthors jouppi n and patterson d on Google TPU papers. |

## 4. Agreement between the two classifiers

A and B gave the same label on 15 of 15 keys (100 percent). They also listed exactly the same same-person record pairs on 15 of 15 keys. Final labels are same_person 10, different_people 4, cannot_tell 1.

## 5. Estimate

The share of flagged keys that hide a real split (final label same_person) is 10 of 15, or 67 percent. The 95 percent Wilson interval is 42 percent to 85 percent. Scaled to the 149 keys that is about 99 keys, with a range of 62 to 126. This comes from a sample of 15 keys, so the interval is wide. It uses no finite population correction, which would narrow it a little. The cannot_tell key is counted as not split.

One same_person key (li y) has its split pair entirely outside the team map. Counting only keys where a same-person pair has both records in the map gives 9 of 15 (60 percent, Wilson interval 36 percent to 80 percent).

Across the 10 same_person keys, an agreed same-person pair joins an OpenAlex record to a name-only record in 7 keys, two name-only records in 2 keys, and two OpenAlex records in 2 keys. A key can have more than one kind.

## 6. Conclusion

This is mostly a real bug, because 10 of 15 sampled keys hide at least one person split into several records, which puts about 67 percent of the 149 keys in that state (95 percent interval 42 percent to 85 percent, from a sample of 15). The most common cause is an OpenAlex record not joined to an arXiv name-only record (7 keys), and the split people include authors of core OCS (optical circuit switching) papers such as Ken-ichi Sato, Stefan Schmid and David Patterson. For recruiting individuals, the map undercounts these people's papers and can show one person as several nodes, so every person-level ranking needs a hand check before use. For partnering with groups, the map is safer, because this flag marks one person shown as several nodes, not strangers merged into one, so a group is still found but its size and output are understated.
