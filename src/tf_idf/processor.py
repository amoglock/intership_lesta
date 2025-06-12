from typing import List
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

from src.core.config import settings


class TFIDFProcessor:
    """
    A class for processing text documents using TF-IDF (Term Frequency-Inverse Document Frequency) analysis.

    This class provides methods to calculate document and collection statistics using TF-IDF metrics,
    which helps identify the most important words in documents and collections.
    """

    def __init__(self):
        """
        Initialize the TFIDFProcessor with vectorizers and configuration settings.
        """
        self.count_vectorizer = CountVectorizer()
        self.tfidf_vectorizer = TfidfVectorizer()

        self.token_pattern = r"(?u)\b\w{4,}\b"
        self.top_words_count = settings.TOP_WORDS_COUNT

    async def document_statistics(
        self, collection_content: List[str], document_content: str = None
    ):
        """
        Calculate TF-IDF statistics for a single document within a collection.

        Args:
            collection_content (List[str]): List of all documents in the collection
            document_content (str, optional): The document to analyze. Defaults to None.

        Returns:
            List[dict]: List of dictionaries containing word statistics (word, tf, idf, tfidf)
                       sorted by IDF in descending order, limited to top_words_count
        """
        count_vec, tf_stats = await self.calculate_tf(document_content)
        idf = await self.calculate_idf(collection_texts=collection_content)

        # Get all words
        feature_names = count_vec.get_feature_names_out()

        # Collect results
        result = []
        for word, tf in zip(feature_names, tf_stats):
            if tf > 0:  # Only words from the document
                word_idx = np.where(feature_names == word)[0][0]
                word_idf = idf[word_idx]
                result.append(
                    {
                        "word": word,
                        "tf": float(tf),
                        "idf": float(word_idf),
                        "tfidf": float(tf * word_idf),
                    }
                )
        # Sort by IDF in descending order
        sorted_result = sorted(result, key=lambda x: x["idf"], reverse=True)
        top_words = sorted_result[: self.top_words_count]
        return top_words

    async def collection_statictics(self, collection_texts):
        """
        Calculate TF-IDF statistics for an entire collection of documents.

        Args:
            collection_texts (List[str]): List of documents in the collection

        Returns:
            dict: Dictionary containing TF-IDF statistics for the collection,
                 sorted by TF-IDF score in descending order
        """
        combined_text = " ".join(collection_texts)
        count_vec, tf_combined = await self.calculate_tf(combined_text)
        idf = await self.calculate_idf(content=collection_texts)

        # Get all words
        feature_names = count_vec.get_feature_names_out()

        # Collect results
        result = []
        for word, tf in zip(feature_names, tf_combined):
            if tf > 0:  # Only words from the document
                word_idx = np.where(feature_names == word)[0][0]
                word_idf = idf[word_idx]
                result.append(
                    {
                        "word": word,
                        "tf": float(tf),
                        "idf": float(word_idf),
                        "tfidf": float(tf * word_idf),
                    }
                )

        # Sort by TF-IDF in descending order
        return {"tfidf": sorted(result, key=lambda x: x["tfidf"], reverse=True)}

    async def calculate_tf(self, content: str):
        """
        Calculate Term Frequency (TF) for a single document.

        Args:
            content (str): The document text

        Returns:
            tuple: (CountVectorizer, numpy.ndarray) - Vectorizer and TF values for the document
        """
        count_vec = CountVectorizer(token_pattern=self.token_pattern)
        tf_matrix = count_vec.fit_transform([content])
        tf_combined = tf_matrix.toarray()[0]
        return count_vec, tf_combined

    async def calculate_idf(self, collection_texts: List[str]):
        """
        Calculate Inverse Document Frequency (IDF) for a collection of documents.

        Args:
            collection_texts (List[str]): List of documents in the collection

        Returns:
            numpy.ndarray: IDF values for each term in the vocabulary
        """
        # Calculate IDF using TfidfVectorizer
        tfidf_vec = TfidfVectorizer(
            token_pattern=self.token_pattern,
            norm=None,  # Disable normalization for raw values
            use_idf=True,
            smooth_idf=False,
        )
        tfidf_vec.fit(collection_texts)
        idf = tfidf_vec.idf_
        return idf
