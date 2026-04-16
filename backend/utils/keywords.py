from typing import List

import numpy as np
from scipy import sparse


def extract_top_keywords(vectorizer, tfidf_vector_row, top_k: int = 8) -> List[str]:
    """
    Extract top TF-IDF weighted keywords for UI highlighting.

    tfidf_vector_row must be a single-row sparse matrix (shape: [1, n_features]).
    """
    if vectorizer is None or tfidf_vector_row is None:
        return []

    if sparse.issparse(tfidf_vector_row):
        row = tfidf_vector_row.tocsr()
    else:
        row = sparse.csr_matrix(tfidf_vector_row)

    if row.shape[1] == 0:
        return []

    feature_names = (
        vectorizer.get_feature_names_out()
        if hasattr(vectorizer, "get_feature_names_out")
        else vectorizer.get_feature_names()
    )

    indices = row.indices
    data = row.data
    if len(indices) == 0:
        return []

    # Get top weighted terms from this sample.
    order = np.argsort(-data)
    top_indices = indices[order][:top_k]

    # feature_names is aligned with vectorizer feature indices.
    keywords = [str(feature_names[i]) for i in top_indices if i < len(feature_names)]
    return keywords

