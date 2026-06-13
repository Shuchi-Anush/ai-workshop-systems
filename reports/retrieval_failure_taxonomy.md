# Retrieval Failure Taxonomy

## Summary

- **Keyword Stuffing**: 6 occurrences
- **Seniority Inflation**: 3 occurrences
- **Dense Similarity Collapse**: 2 occurrences
- **Sparse Mismatch**: 2 occurrences
- **Hybrid Dilution**: 2 occurrences

## Detailed Failures

### Query: `Senior Python Developer with FastAPI and Docker` (DENSE)
- **Root Cause(s)**: Keyword Stuffing, Seniority Inflation, Dense Similarity Collapse
- **Adversarial Leaks**: adv_fake_seniority, adv_hr_keyword_stuffed
- **Top Retrieved**: adv_fake_seniority, 20674668_information-technology_java_javascript_python_sql, adv_hr_keyword_stuffed

### Query: `React Frontend Developer with JavaScript` (DENSE)
- **Root Cause(s)**: Keyword Stuffing
- **Adversarial Leaks**: adv_hr_keyword_stuffed
- **Top Retrieved**: adv_fake_seniority, adv_hr_keyword_stuffed, 20674668_information-technology_java_javascript_python_sql

### Query: `Senior C# Backend Engineer .NET Core` (DENSE)
- **Root Cause(s)**: Dense Similarity Collapse
- **Top Retrieved**: 12763627_information-technology_c#_javascript_sql, 10089434_information-technology_azure_c#_java_sql, 13385306_information-technology_c#_sql

### Query: `Senior Python Developer with FastAPI and Docker` (SPARSE)
- **Root Cause(s)**: Keyword Stuffing, Seniority Inflation, Sparse Mismatch
- **Adversarial Leaks**: adv_fake_seniority, adv_hr_keyword_stuffed
- **Top Retrieved**: adv_fake_seniority, 20674668_information-technology_java_javascript_python_sql, adv_hr_keyword_stuffed

### Query: `React Frontend Developer with JavaScript` (SPARSE)
- **Root Cause(s)**: Keyword Stuffing
- **Adversarial Leaks**: adv_hr_keyword_stuffed
- **Top Retrieved**: adv_fake_seniority, adv_hr_keyword_stuffed, 20674668_information-technology_java_javascript_python_sql

### Query: `Senior C# Backend Engineer .NET Core` (SPARSE)
- **Root Cause(s)**: Sparse Mismatch
- **Top Retrieved**: 12763627_information-technology_c#_javascript_sql, 10089434_information-technology_azure_c#_java_sql, 13385306_information-technology_c#_sql

### Query: `Senior Python Developer with FastAPI and Docker` (HYBRID)
- **Root Cause(s)**: Keyword Stuffing, Seniority Inflation, Hybrid Dilution
- **Adversarial Leaks**: adv_fake_seniority, adv_hr_keyword_stuffed
- **Top Retrieved**: adv_fake_seniority, 20674668_information-technology_java_javascript_python_sql, adv_hr_keyword_stuffed

### Query: `React Frontend Developer with JavaScript` (HYBRID)
- **Root Cause(s)**: Keyword Stuffing
- **Adversarial Leaks**: adv_hr_keyword_stuffed
- **Top Retrieved**: adv_fake_seniority, adv_hr_keyword_stuffed, 20674668_information-technology_java_javascript_python_sql

### Query: `Senior C# Backend Engineer .NET Core` (HYBRID)
- **Root Cause(s)**: Hybrid Dilution
- **Top Retrieved**: 12763627_information-technology_c#_javascript_sql, 10089434_information-technology_azure_c#_java_sql, 13385306_information-technology_c#_sql

