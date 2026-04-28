
# Binary Independence Model (BIM) Implementation

This repository contains a simple, custom implementation of the Binary Independence Model (BIM) for information retrieval. BIM is a probabilistic retrieval model that ranks documents based on the probability of their relevance to a given query.

## Features
- Text preprocessing (tokenization, lowercasing, lemmatization) using NLTK.
- Vocabulary building and binary term frequency calculation.
- Probability estimation for terms in relevant (P(t|R)) and non-relevant (P(t|nR)) documents using initial heuristic estimations (pseudo-counts).
- Document ranking based on BIM scores.
- Self-contained Python script (`bim_model.py`) for easy execution.

## Getting Started

### Prerequisites
- Python 3.x
- `nltk` library

```bash
pip install nltk
```

### Usage

To run the BIM demonstration, simply execute the `bim_model.py` script:

```bash
python bim_model.py
```

This will perform the following steps:
1. Download necessary NLTK resources (punkt, stopwords, wordnet).
2. Define sample documents and queries.
3. Preprocess the documents and queries.
4. Build a vocabulary and calculate document frequencies.
5. Estimate BIM probabilities P(t|R) and P(t|nR).
6. Rank the documents for each sample query and print the results.

### Code Structure

- `download_nltk_resources()`: Ensures all required NLTK data is downloaded.
- `preprocess_english_text(text)`: Cleans and preprocesses English text by tokenizing, lowercasing, removing stopwords, and lemmatizing.
- `calculate_bim_probabilities(document_frequencies, num_documents, pseudo_count_r, pseudo_count_nr)`: Estimates the probabilities P(t|R) and P(t|nR) for each term in the vocabulary.
- `calculate_bim_score(query_tokens, document_tf, p_t_R, p_t_nR)`: Calculates the BIM score for a single document given a query.
- `rank_documents(queries_raw, all_documents_raw, preprocessed_documents, binary_term_frequencies, p_t_R, p_t_nR, preprocess_func)`: Ranks a collection of documents for multiple queries.

### Sample Data

The `bim_model.py` script includes predefined sample documents and queries for demonstration purposes:

**Documents:**
```
[
    "The quick brown fox jumps over the lazy dog.",
    "The dog barks loudly at the cat.",
    "A brown fox is a wild animal.",
    "The cat sleeps peacefully on the mat.",
    "Quickly, the fox ran away from the barking dog."
]
```

**Queries:**
```
[
    "brown fox",
    "lazy dog sleeps",
    "cat barking"
]
```

## How BIM Works (Briefly)

The Binary Independence Model (BIM) assumes that terms are statistically independent and that the presence/absence of a term in a document is independent of the presence/absence of other terms in the same document. It also assumes that documents can be classified as either relevant or non-relevant to a query.

The core idea is to calculate a Relevance Weight (RW) for each term, which is the logarithm of the odds ratio of the term appearing in relevant documents versus non-relevant documents. The total score for a document is the sum of the RWs of the query terms present in that document.

Initial probability estimates `P(t|R)` and `P(t|nR)` are often made heuristically (e.g., using pseudo-counts or assuming 0.5) and can be refined through relevance feedback.

## License

This project is open-source and available under the MIT License.
