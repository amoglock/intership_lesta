import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer



class TFIDFProcessor:
    def __init__(self):
        self.count_vectorizer = CountVectorizer()
        self.tfidf_vectorizer = TfidfVectorizer()

        self.token_pattern = r"(?u)\b\w{2,}\b"

    async def document_statistics(self, current_doc_content, collection_texts):
        """ """

        try:
            doc_index = collection_texts.index(current_doc_content)
        except ValueError:
            raise ValueError("Документ не найден в коллекции после предобработки")

        count_vec, tf_current = await self.calculate_document_tf(doc_index, collection_texts)
        idf = await self.calculate_idf(collection_texts=collection_texts)

        # Получаем все слова
        feature_names = count_vec.get_feature_names_out()

        # Собираем результаты
        result = []
        for word, tf in zip(feature_names, tf_current):
            if tf > 0:  # Только слова из документа
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

        # Сортировка по убыванию TF-IDF
        return {"tfidf": sorted(result, key=lambda x: x["tfidf"], reverse=True)}
    
    async def collection_statictics(self, collection_texts):
        """ """
        combined_text = ' '.join(collection_texts)
        count_vec, tf_combined = await self.calculate_collection_tf(combined_text)
        idf = await self.calculate_idf(collection_texts=collection_texts)

        # Получаем все слова
        feature_names = count_vec.get_feature_names_out()

        # Собираем результаты
        result = []
        for word, tf in zip(feature_names, tf_combined):
            if tf > 0:  # Только слова из документа
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

        # Сортировка по убыванию TF-IDF
        return {"tfidf": sorted(result, key=lambda x: x["tfidf"], reverse=True)}


    
    async def calculate_document_tf(self, doc_index, collection_texts: str, ):
        """ """
        # TF (CountVectorizer)
        count_vec = CountVectorizer(token_pattern=self.token_pattern)
        tf_matrix = count_vec.fit_transform(collection_texts)
        tf_current = tf_matrix[doc_index].toarray()[0]
        return count_vec, tf_current
    
    async def calculate_collection_tf(self, collection_texts):
        """ """
        count_vec = CountVectorizer(token_pattern=self.token_pattern)
        tf_matrix = count_vec.fit_transform([collection_texts])
        tf_combined = tf_matrix.toarray()[0]
        return count_vec, tf_combined

    async def calculate_idf(self, collection_texts):
        """ """
        # IDF (TfidfVectorizer)
        tfidf_vec = TfidfVectorizer(
            token_pattern=self.token_pattern,
            norm=None,  # Отключаем нормализацию для чистых значений
            use_idf=True,
            smooth_idf=False,
        )
        tfidf_vec.fit(collection_texts)
        idf = tfidf_vec.idf_
        return idf
