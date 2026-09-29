# Number check 2. Split name keys in the team map

Inputs are data/work/nc2_run2_evidence.json (evidence, from pipeline/check_name_keys.py), data/work/nc2_run2_class_A.json and data/work/nc2_run2_class_B.json (two independent classifiers). Every number below is computed by pipeline/merge_name_keys.py, which also re-runs the flag query read-only on data/db/papers.sqlite. A name key is a last name plus first initial, such as 'sato k'. The team map is the stage 4 author graph, which holds only authors with an extended-set paper.

## 1. The count, reproduced

The query returns 147 name keys today, the same as flagged_keys_total in the evidence file and the 147 that the stage 4 grapher logged at 16:44 in deliverables/pitfalls_original_log.md. A key is flagged when more than one author record with that key has an extended-set paper and at least one of those records has a core paper. The rule lives in pipeline/graph.py log_split_person_candidates().

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

| status | flagged keys (of 147) | share | sampled keys (of 15) | final same_person | final different_people | final cannot_tell |
|---|---|---|---|---|---|---|
| all_openalex | 70 | 48 percent | 6 | 1 | 5 | 0 |
| mixed | 69 | 47 percent | 9 | 5 | 3 | 1 |
| all_name_only | 8 | 5 percent | 0 | 0 | 0 | 0 |

An all_openalex key cannot come from the stage 2 merge rule for name-only records, because OpenAlex itself gave its records different author IDs. So that rule can explain at most the 77 mixed or all_name_only keys.

## 3. The 15 sampled keys

The sample is 15 keys drawn at random from the 147 with seed 20260930 (pipeline/check_name_keys.py). The records column counts records in the team map, then all author records with the key. A and B are the two classifier labels. Final is their shared label, else cannot_tell.

| key | records (in map of all) | A | B | final | reason |
|---|---|---|---|---|---|
| chen b | 2 of 3 | different_people | different_people | different_people | Different first names (Benwen, Bao, Bin) at different institutions. The only shared coauthor key, guo h, is two different people (Hangbing Guo, Hangyu Guo). |
| chen g | 2 of 4 | different_people | different_people | different_people | Different first names (Genxiang, Guihai, Guanyu, Guo), and the only overlaps are common coauthor keys such as chen x. |
| chen s | 2 of 4 | same_person | same_person | same_person | A5068274938 and A5108580591 are both 'Sai Chen' at Alibaba Group and share coauthor Chongjin Xie. Only A5068274938 is in the team map. Shixi Chen and Shawn Shuoshuo Chen are other people. |
| chen y | 10 of 20 | same_person | same_person | same_person | The 'Yan Chen' records at Northwestern share coauthors such as Ankit Singla on the OSA (optical switching architecture) papers, and the 'Ying Chen' records at Minzu University of China share coauthors such as Genxiang Chen. The 'Young-kai Chen' records have Alcatel Lucent on both papers and the same topic but no shared coauthor, so that pair is weaker. |
| liu z | 6 of 16 | same_person | same_person | same_person | Zhuotao Liu is split into A5045206037 and name-only #2 and #5, which share coauthors Peirui Cao, Shizhen Zhao and Xinbing Wang. ZhuoRan Liu (name:liu z) and Zhuoran Liu (#4) share coauthors such as Weihao Jiang and Xinchi Han. ZhuoRan and Zhuotao sit on the same papers, so they are two people. |
| patterson d | 2 of 3 | same_person | same_person | same_person | A5077202069 (Google) and name:patterson d share coauthor Cliff Young on Google tensor processing unit (TPU) papers. A5101927146 (Berkeley, Roofline) is outside the map and shares nothing. |
| singh a | 4 of 4 | same_person | same_person | same_person | The 'Arjun Singh' records share many coauthors, such as Amin M. Vahdat, on the Apollo optical circuit switching (OCS) papers. The 'Atul Kumar Singh' records share Princeton and coauthors such as Ankit Singla on Proteus and OSA. |
| wei y | 2 of 2 | different_people | different_people | different_people | Different first names (Yuming, Yiran) with no shared coauthor, institution or paper. |
| wu j | 4 of 7 | different_people | different_people | different_people | Different first names (Jingbo, Jiamin, Jiayang, Jeffrey, Juejian, Junhui, Jian). The only overlaps are common coauthor keys and broad institutions on papers. |
| xu h | 2 of 3 | cannot_tell | cannot_tell | cannot_tell | 'Hongnan Xu' is someone else. 'Hong Li Xu' and 'Hong Xu' both work on data center networking, but they share no coauthor, neither has an affiliation, and their years are far apart, so neither classifier could decide. |
| yang y | 3 of 11 | different_people | different_people | different_people | Every record has a different first name, and the only overlaps are common coauthor keys such as wang h and broad institutions on papers. |
| yang z | 2 of 2 | different_people | different_people | different_people | Different first names (Zijiang, Zhiyong) with no shared coauthor, institution or paper. |
| zhang h | 3 of 12 | different_people | different_people | different_people | Mostly different first names. The 'Hao Zhang' records are at different institutions (Tianjin University, University of Science and Technology of China, Beijing Institute of Technology) on different topics with no shared coauthor. |
| zhang j | 2 of 4 | different_people | different_people | different_people | Jinsong and Jianfa differ by first name. The 'Jie Zhang' records are at Beijing University of Posts and Telecommunications (optical switching) and the China Meteorological Administration (climate model) with no shared coauthor. |
| zhu y | 3 of 7 | same_person | same_person | same_person | A5084336844 and name:zhu y are both 'Yibo Zhu' and share coauthors Yu Zhou and Yimin Jiang (listed once as 'Jiang, Yimin') on data center network papers. The Santa Barbara City College 'Yibo Zhu' shares nothing with them. |

## 4. Agreement between the two classifiers

A and B gave the same label on 15 of 15 keys (100 percent). They also listed exactly the same same-person record pairs on 15 of 15 keys. Final labels are same_person 6, different_people 8, cannot_tell 1.

## 5. Estimate

The share of flagged keys that hide a real split (final label same_person) is 6 of 15, or 40 percent. The 95 percent Wilson interval is 20 percent to 64 percent. Scaled to the 147 keys that is about 59 keys, with a range of 29 to 94. This comes from a sample of 15 keys, so the interval is wide. It uses no finite population correction, which would narrow it a little. The cannot_tell key is counted as not split.

One same_person key (chen s) has its split pair partly outside the team map. Counting only keys where a same-person pair has both records in the map gives 5 of 15 (33 percent, Wilson interval 15 percent to 58 percent).

Across the 6 same_person keys, an agreed same-person pair joins an OpenAlex record to a name-only record in 3 keys, two name-only records in 1 key, and two OpenAlex records in 3 keys. A key can have more than one kind.

## 6. Conclusion

This is a real bug, though in this sample not for most keys, because 6 of 15 sampled keys hide at least one person split into several records. That puts about 40 percent of the 147 keys in that state (95 percent interval 20 percent to 64 percent, from a sample of 15), and the interval includes half, so the sample cannot say whether most flagged keys are real splits. The 16:44 grapher line blames the stage 2 merge rule for name-only records, but in 3 of the 6 keys OpenAlex itself gave one person two author IDs, which that rule cannot cause. In 3 keys an OpenAlex record was not joined to an arXiv name-only record. The split people include authors of core OCS papers such as Arjun Singh (Apollo), Yan Chen (OSA) and Zhuotao Liu. For recruiting individuals, the map undercounts these people's papers and can show one person as several nodes, so every person-level ranking needs a hand check before use. For partnering with groups, the map is safer, because this flag marks one person shown as several nodes, not strangers merged into one, so a group is still found but its size and output are understated.
