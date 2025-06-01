from collections import Counter
from typing import List, Tuple, Dict
import razdel
import nltk
import math

from nltk.corpus import stopwords
from fastapi import HTTPException, status
from datetime import datetime, UTC

from src.models import Analysis, Metrics
from src.tf_idf.repository import Repository
from src.tf_idf.models import ResultModel

# NLTK initialization
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')
stop_words = set(stopwords.words('russian'))

class TFIDFProcessor:
    def __init__(self):
        self.repository = Repository()

    def tokenize(self, text: str) -> List[str]:
        """Tokenize text using razdel and remove punctuation, digits, and whitespace"""
        # Tokenize using razdel
        tokens = [token.text for token in razdel.tokenize(text.lower())]
        
        # Remove punctuation, digits, whitespace, and empty tokens
        return [
            token for token in tokens 
            if token and 
            not any(char in '.,!?;:()[]{}«»"\'—' for char in token) and
            not any(char.isdigit() for char in token) and
            not token.isspace() and
            not token.isspace() and
            len(token.strip()) > 0 and
            not token.startswith('⁠')  # Remove special empty character
        ]

    def calculate_tf(self, words: List[str]) -> List[Tuple[str, float]]:
        """Calculate Term Frequency for the document words

        Args:
            words (List[str]): List of words from the document

        Returns:
            List[Tuple[str, float]]: List of tuples (word, tf rating)
        """
        if not words:
            return []
            
        total_words = len(words)
        filtered_words = [word for word in words if word not in stop_words]
        
        # Count word frequencies
        word_counts = Counter(filtered_words)
        
        # Calculate TF
        tf = {word: count/total_words for word, count in word_counts.items()}
        return [(word, score) for word, score in tf.items()]

    async def calculate_idf(self, document_words: List[str]) -> Dict[str, float]:
        """Calculate Inverse Document Frequency for words

        Args:
            document_words (List[str]): List of words from the current document

        Returns:
            Dict[str, float]: Dictionary of word -> idf score
        """
        if not document_words:
            return {}
            
        # Get document count for each word
        word_doc_counts = await self.repository.get_word_document_counts(set(document_words))
        total_docs = await self.repository.get_total_documents()
        
        # Calculate IDF using the classic formula with smoothing
        idf_scores = {}
        for word, count in word_doc_counts.items():
            # Use formula: log((total_documents + 1) / (document_count_with_word + 1))
            # Add 1 to both values for smoothing
            idf_scores[word] = math.log((total_docs + 1) / (count + 1))
            
        return idf_scores

    async def process_text(self, filename: str, text: str) -> ResultModel:
        """Process text and calculate TF-IDF scores

        Args:
            filename (str): Name of the file
            text (str): Text content
            max_file_size (int, optional): Maximum file size in bytes. Defaults to 10MB.

        Returns:
            ResultModel: Processing results

        Raises:
            HTTPException: If text is too large or processing fails
        """
        # Создаем запись метрик
        start_time = datetime.now(UTC)
        metrics = Metrics(
            start_time=start_time,
            status="pending"
        )

        try:
            # Extract words using razdel
            document_words = self.tokenize(text)
            total_words = len(document_words)
            filtered_words = [word for word in document_words if word not in stop_words]

            # Calculate TF
            tf = self.calculate_tf(document_words)

            # Create analysis record
            analysis = Analysis(
                filename=filename,
                content=text,  # Add text content to the content field
                total_words=total_words,
                original_text=text,
                filtered_words=filtered_words,
            )

            # Save to database
            analysis = await self.repository.save_result_to_db(analysis, tf)
            
            # Сохраняем метрики с ID анализа
            metrics.analysis_id = analysis.id
            metrics = await self.repository.save_metrics(metrics)

            # Calculate IDF and combine results
            idf = await self.calculate_idf(filtered_words)
            results = [
                (word, tf_rating, idf[word])
                for word, tf_rating in tf
                if word in idf
            ]

            # Sort by IDF in descending order (from highest to lowest)
            results.sort(key=lambda x: x[2], reverse=True)
            
            # Refresh metrics
            end_time = datetime.now(UTC)
            metrics.end_time = end_time
            metrics.processing_time = (end_time - start_time).total_seconds()
            metrics.status = "completed"
            await self.repository.save_metrics(metrics)
            
            return ResultModel(analysis=analysis, results=results)

        except Exception as e:
            # Refresh metricx if error
            if metrics.id:
                end_time = datetime.now(UTC)
                metrics.end_time = end_time
                metrics.processing_time = (end_time - start_time).total_seconds()
                metrics.status = "failed"
                await self.repository.save_metrics(metrics)
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to process text: {str(e)}"
            )
 