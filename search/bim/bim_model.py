
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from collections import defaultdict
import math

# Ensure NLTK resources are downloaded (for English preprocessing)
def download_nltk_resources():
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords')
    try:
        nltk.data.find('corpora/wordnet')
    except LookupError:
        nltk.download('wordnet')
    # The 'punkt_tab' resource is usually needed for sent_tokenize, but word_tokenize might internally use other punkt models.
    # It was causing issues earlier, but let's include it for completeness if needed.
    try:
        nltk.data.find('tokenizers/punkt_tab')
    except LookupError:
        nltk.download('punkt_tab')

# English Text Preprocessing Function
def preprocess_english_text(text):
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()
    tokens = word_tokenize(text.lower())
    processed_tokens = [lemmatizer.lemmatize(token) for token in tokens if token.isalpha() and token not in stop_words]
    return processed_tokens

# BIM Probability Estimation Function
def calculate_bim_probabilities(document_frequencies, num_documents, pseudo_count_r=0.5, pseudo_count_nr=0.5):
    p_t_R = {}
    p_t_nR = {}

    for term in document_frequencies:
        df_t = document_frequencies[term]
        p_t_R[term] = pseudo_count_r / (pseudo_count_r + pseudo_count_r) # Effectively 0.5
        p_t_nR[term] = (df_t + pseudo_count_nr) / (num_documents + pseudo_count_nr * 2)

        p_t_R[term] = max(1e-6, min(1 - 1e-6, p_t_R[term]))
        p_t_nR[term] = max(1e-6, min(1 - 1e-6, p_t_nR[term]))
    return p_t_R, p_t_nR

# BIM Score Calculation Function
def calculate_bim_score(query_tokens, document_tf, p_t_R, p_t_nR):
    score = 0
    for term in query_tokens:
        if term in p_t_R and term in p_t_nR:
            if term in document_tf: # Term is present in the document
                p = p_t_R[term]
                q = p_t_nR[term]
                if p > 0 and q < 1: # Ensure valid probability for log calculation
                    weight = math.log((p / (1 - p)) / (q / (1 - q)))
                    score += weight
    return score

# Document Ranking Function
def rank_documents(queries_raw, all_documents_raw, preprocessed_documents, binary_term_frequencies, p_t_R, p_t_nR, preprocess_func):
    ranked_results = {}
    for query_text in queries_raw:
        preprocessed_query = preprocess_func(query_text)
        doc_scores = []
        for i, doc_tf in enumerate(binary_term_frequencies):
            score = calculate_bim_score(preprocessed_query, doc_tf, p_t_R, p_t_nR)
            doc_scores.append((f"Document {i+1}", score, all_documents_raw[i]))

        doc_scores.sort(key=lambda x: x[1], reverse=True)
        ranked_results[query_text] = doc_scores
    return ranked_results

if __name__ == '__main__':
    print("Running BIM demonstration from bim_model.py")
    download_nltk_resources()

    documents = [
        "The quick brown fox jumps over the lazy dog.",
        "The dog barks loudly at the cat.",
        "A brown fox is a wild animal.",
        "The cat sleeps peacefully on the mat.",
        "Quickly, the fox ran away from the barking dog."
    ]

    queries = [
        "brown fox",
        "lazy dog sleeps",
        "cat barking"
    ]

    preprocessed_documents = [preprocess_english_text(doc) for doc in documents]

    vocabulary = set()
    for doc_tokens in preprocessed_documents:
        vocabulary.update(doc_tokens)
    vocabulary = sorted(list(vocabulary))

    binary_term_frequencies = []
    for doc_tokens in preprocessed_documents:
        doc_tf = {term: 1 for term in doc_tokens}
        binary_term_frequencies.append(doc_tf)

    document_frequencies = defaultdict(int)
    for doc_tf in binary_term_frequencies:
        for term in doc_tf:
            document_frequencies[term] += 1

    num_documents = len(documents)
    p_t_R, p_t_nR = calculate_bim_probabilities(document_frequencies, num_documents)

    ranked_documents = rank_documents(queries, documents, preprocessed_documents, binary_term_frequencies, p_t_R, p_t_nR, preprocess_english_text)

    print("
Document ranking completed.")
    for query, ranks in ranked_documents.items():
        print(f"
Query: '{query}'")
        for doc_name, score, original_doc in ranks:
            print(f"  {doc_name} (Score: {score:.4f}): {original_doc}")
