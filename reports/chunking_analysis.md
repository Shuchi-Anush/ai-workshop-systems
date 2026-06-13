# Chunking Quality Analysis

## 1. Chunking Distributions
Current dataset index contains 61 chunks across 27 candidates.
- **Mean Chunk Length:** ~1045 characters
- **Max Chunk Length:** 4192 characters (Outlier/Dense Experience blocks)
- **Min Chunk Length:** 32 characters (Skills/Summary snippets)

## 2. Retrieval Effectiveness by Chunk Type
Chunking directly impacts ranking mathematics, particularly BM25 term frequency.

### Semantic Dilution
When highly dense skill sections are bundled with long, verbose experience bullet points (Max length 4192), the BM25 term frequency drops. This penalizes the chunk relative to adversarial resumes which stack keywords into shorter chunks.
**Verdict:** Chunk boundaries currently cause semantic dilution for candidates with verbose descriptions.

### Overlap Impact
We do not use sliding window overlap currently. The rule-based extractor segments strictly by section headers (`EXPERIENCE`, `EDUCATION`, `SKILLS`).
This prevents double-counting in RRF, but hard boundaries sometimes split context (e.g., a tool mentioned in "Skills" is ranked separately from its application in "Experience").

## 3. Section-Aware Contribution
During the benchmark:
- **Skill Chunks** contribute heavily to BM25.
- **Experience Chunks** contribute heavily to Dense similarity.

**Recommendation for Evolution:**
Implement sliding-window overlapping for `EXPERIENCE` sections, while treating `SKILLS` sections as exact-match metadata instead of embedding them.
