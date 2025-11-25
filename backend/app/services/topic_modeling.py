from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import TfidfVectorizer
from .preprocessor import preprocess_text
import numpy as np
from typing import List, Tuple, Dict

def train_topic_model(documents: List[str], n_topics: int = 10) -> Tuple:
    """
    Train NMF topic model
    
    Args:
        documents: List of text documents
        n_topics: Number of topics to extract
    
    Returns:
        (model, doc_topics, topics_keywords)
    """
    print(f"Training topic model with {n_topics} topics on {len(documents)} documents...")
    
    # Preprocess documents
    cleaned_docs = [preprocess_text(doc) for doc in documents]
    
    # Vectorize with TF-IDF
    vectorizer = TfidfVectorizer(
        max_features=1000,
        min_df=2,
        max_df=0.95,
        ngram_range=(1, 2)
    )
    
    tfidf = vectorizer.fit_transform(cleaned_docs)
    
    # Train NMF
    nmf = NMF(
        n_components=n_topics,
        random_state=42,
        max_iter=500,
        alpha_W=0.1,
        alpha_H=0.1,
        l1_ratio=0.5
    )
    
    doc_topics = nmf.fit_transform(tfidf)
    
    # Extract keywords per topic
    feature_names = vectorizer.get_feature_names_out()
    topics_keywords = []
    
    for topic_idx, topic in enumerate(nmf.components_):
        top_indices = topic.argsort()[-10:][::-1]
        keywords = [feature_names[i] for i in top_indices]
        
        topics_keywords.append({
            'topic_id': topic_idx,
            'keywords': keywords,
            'weights': topic[top_indices].tolist()
        })
        
        print(f"  Topic {topic_idx + 1}: {', '.join(keywords[:5])}")
    
    return nmf, doc_topics, topics_keywords