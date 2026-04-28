
from janome.tokenizer import Tokenizer
from collections import defaultdict
import math

# 1. 日本語サンプルデータ
japanese_documents = [
    "速い茶色のキツネが怠惰な犬を飛び越えます。",
    "犬は猫に向かってうるさく吠えます。",
    "茶色のキツネは野生動物です。",
    "猫はマットの上で静かに眠ります。",
    "素早く、キツネは吠える犬から逃げました。"
]

japanese_queries = [
    "茶色のキツネ",
    "怠惰な犬 眠る",
    "猫 吠える"
]

# 2. 日本語テキスト前処理関数
t = Tokenizer()

# 簡単な日本語ストップワードリスト (例)
# 通常はより包括的なリストを使用します。必要に応じて拡張してください。
japanese_stop_words = set(["の", "に", "は", "を", "が", "と", "ます", "です", "れる", "こと", "から", "また", "など", "れる", "なり", "よる"])

def preprocess_japanese_text(text):
    tokens = []
    for token in t.tokenize(text.lower()):
        # 形態素の原型を取得し、名詞、動詞、形容詞のみを対象とし、ストップワードを除外
        part_of_speech = token.part_of_speech.split(',')[0]
        if part_of_speech in ['名詞', '動詞', '形容詞']:
            base_form = token.base_form if token.base_form != '*' else token.surface # 原形がない場合は表層形
            if base_form not in japanese_stop_words and base_form.isalpha():
                tokens.append(base_form)
    return tokens

# BIM Probability Estimation Function (reused from English version)
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

# BIM Score Calculation Function (reused from English version)
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

# Document Ranking Function (reused from English version)
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
    print("Running Japanese BIM demonstration from bim_model_japanese.py")
    print("
日本語のサンプル文書とクエリを定義しました。")

    # Preprocess Japanese documents
    preprocessed_japanese_documents = [preprocess_japanese_text(doc) for doc in japanese_documents]
    print("
日本語の文書を前処理しました:")
    for i, doc in enumerate(preprocessed_japanese_documents):
        print(f"文書 {i+1}: {doc}")

    # 語彙の構築と出現頻度計算 (日本語版)
    japanese_vocabulary = set()
    for doc_tokens in preprocessed_japanese_documents:
        japanese_vocabulary.update(doc_tokens)
    japanese_vocabulary = sorted(list(japanese_vocabulary))

    binary_japanese_term_frequencies = []
    for doc_tokens in preprocessed_japanese_documents:
        doc_tf = {term: 1 for term in doc_tokens}
        binary_japanese_term_frequencies.append(doc_tf)

    japanese_document_frequencies = defaultdict(int)
    for doc_tf in binary_japanese_term_frequencies:
        for term in doc_tf:
            japanese_document_frequencies[term] += 1

    print("
日本語の語彙を構築し、出現頻度を計算しました。")
    print(f"ユニークな単語の総数: {len(japanese_vocabulary)}")

    # BIMスコアリング関数: 確率推定 (日本語版)
    num_japanese_documents = len(japanese_documents)
    p_t_R_jp, p_t_nR_jp = calculate_bim_probabilities(japanese_document_frequencies, num_japanese_documents)

    print("
BIM確率 (P(t|R) と P(t|nR)) を推定しました。(日本語版)")

    # 文書ランキングの実装 (日本語版)
    ranked_japanese_documents = rank_documents(japanese_queries, japanese_documents, preprocessed_japanese_documents, binary_japanese_term_frequencies, p_t_R_jp, p_t_nR_jp, preprocess_japanese_text)

    print("
日本語文書のランキングが完了しました。")
    for query, ranks in ranked_japanese_documents.items():
        print(f"
クエリ: '{query}'")
        for doc_name, score, original_doc in ranks:
            print(f"  {doc_name} (スコア: {score:.4f}): {original_doc}")
