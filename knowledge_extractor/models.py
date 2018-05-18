'''
Knowledge extractor module.
'''

import artm
import inspect
import operator
import os
import numpy as np
import pandas as pd

from sklearn.manifold import MDS
from sklearn.metrics import pairwise_distances

from knowledge_extractor.utils import text_prepare

class TopicModel(object):
    def __init__(self, search_guid, doc_guids, num_of_topics=10):
        self.search_guid = search_guid
        self.doc_guids = doc_guids
        self.num_of_topics = num_of_topics
        self.training_done = False

    def is_ready(self):
        return self.training_done

    def get_doc_guids(self):
        return self.doc_guids

    def get_top_words(self, score_name='text_words', count=None):
        top_words = {}
        for topic_name in self.model_artm.topic_names:
            top_words[topic_name] = self.top_tokens_by_topic(score_name, topic_name, count=count)

        return top_words

    def train(self):
        vocabulary_file = self._prepare_texts()
        target_folder = self._get_bigARTM_dir()

        batch_vectorizer = artm.BatchVectorizer(
            data_path=vocabulary_file, data_format='vowpal_wabbit',
            target_folder=target_folder, batch_size=100
        )

        dict_path = self._get_dictionary_path()
        dict_file = '{}.dict'.format(dict_path)

        if os.path.isfile(dict_file):
            os.remove(dict_file)

        my_dictionary = artm.Dictionary()
        my_dictionary.gather(data_path=target_folder, vocab_file_path=vocabulary_file)
        my_dictionary.save(dictionary_path=dict_path)
        my_dictionary.load(dictionary_path=dict_file)

        T = self.num_of_topics
        topic_names=["sbj"+str(i) for i in range(T-1)]+["bcg"]
        
        self.model_artm = artm.ARTM(
            num_topics=T,
            topic_names=topic_names,
            class_ids={"text": 1, "doc_guid": 1},
            dictionary=my_dictionary,
            cache_theta=True
        )

        self.model_artm.initialize(dictionary=my_dictionary)
        self.model_artm.scores.add(artm.TopTokensScore(name="text_words", num_tokens=15, class_id="text"))
        self.model_artm.scores.add(artm.TopTokensScore(name="doc_guid_words", num_tokens=15, class_id="doc_guid"))

        self.model_artm.regularizers.add(artm.SmoothSparsePhiRegularizer(name='SparsePhi', tau=1e5, dictionary=my_dictionary, class_ids="text", topic_names="bcg"))

        self.model_artm.fit_offline(batch_vectorizer=batch_vectorizer, num_collection_passes=30)

        self.model_artm.regularizers.add(
            artm.SmoothSparsePhiRegularizer(
                name='SparsePhi-1e5',
                tau=-1e5,
                dictionary=my_dictionary,
                class_ids="text",
                topic_names=["sbj"+str(i) for i in range(T-1)]
            )
        )

        self.model_artm.fit_offline(batch_vectorizer=batch_vectorizer, num_collection_passes=15)

        self.training_done = True

    def get_topic_profile(self):
        phi_a = self.model_artm.get_phi(class_ids='doc_guid')
        theta = self.model_artm.get_theta()

        p_t = theta.sum(axis=1)
        df_p_t = pd.DataFrame(p_t / p_t.sum(axis=0))
        df_p_t.columns = ['probability']

        topic_profile = pd.DataFrame(index=phi_a.index.copy(), columns=df_p_t.index.copy())
        for a_idx, _ in enumerate(topic_profile.index):
            total = np.sum([phi_a.iloc[a_idx][col] * df_p_t.loc[col]['probability'] for col in topic_profile.columns])
            
            for _, topic in enumerate(topic_profile.columns):     
                prob = (phi_a.iloc[a_idx][topic] * df_p_t.loc[topic]['probability']) / total
                topic_profile.iloc[a_idx][topic] = prob

        mds_cos_clstr = MDS(n_components=2)
        MDS_transformed_cos = mds_cos_clstr.fit_transform(pairwise_distances(topic_profile, metric='cosine'))

        result = []
        for (doc, x, y) in zip(self.doc_guids, MDS_transformed_cos[:, [0]], MDS_transformed_cos[:, [1]]):
            result.append({'doc_guid': doc, 'x': x[0], 'y': y[0]})

        docs_folder = self._get_documents_folder()
        for res in result:
            with open('{}/{}.txt'.format(docs_folder, res['doc_guid']), encoding='utf-8') as doc:
                for line in doc:
                    res['description'] = line
                    break

        return result

    def _prepare_texts(self):
        vocabulary_file = self._get_vocabulary_file_name()
        vocabulary = open(vocabulary_file, 'w')
        docs_folder = self._get_documents_folder()
        for guid in self.doc_guids:
            with open('{}/{}.txt'.format(docs_folder, guid), encoding='utf-8') as doc:
                vocabulary.write('document_{} |text '.format(guid))
                for line in doc:
                    prepared = text_prepare(line)
                    vocabulary.write(prepared)
                vocabulary.write(' |doc_guid {}\n'.format(guid))
                vocabulary.flush()
        vocabulary.close()

        return vocabulary_file

    def _get_bigARTM_dir(self):
        parent_path = os.path.dirname(os.path.dirname(inspect.getfile(self.__class__)))
        dir_path = os.path.join(
            parent_path,
            'bigARTM')

        if not os.path.isdir(dir_path):
            os.makedirs(dir_path)

        return dir_path

    def _get_documents_folder(self):
        parent_path = os.path.dirname(os.path.dirname(inspect.getfile(self.__class__)))
        dir_path = os.path.join(
            parent_path,
            'documents')

        return dir_path

    def _get_dictionary_path(self):
        parent_path = self._get_bigARTM_dir()
        dir_path = os.path.join(
            parent_path,
            'dictionary_{}'.format(self.search_guid))

        return dir_path

    def _get_vocabulary_file_name(self):
        dir_path = self._get_bigARTM_dir()

        file_name = os.path.join(
            dir_path,
            'ALL_TEXT_{}.txt'.format(self.search_guid)
        )

        return file_name

    def top_tokens_by_topic(self, score_name, topic_name, count=None):
        top_tokens = self.model_artm.score_tracker[score_name]
        top_words = list()
        
        if topic_name not in top_tokens.last_tokens \
            or topic_name not in top_tokens.last_weights:
            return []

        for (token, weight) in zip(top_tokens.last_tokens[topic_name],
                                top_tokens.last_weights[topic_name]):
            top_words.append((token, weight))
        if count is None:
            count = len(top_words)
        
        top_words = sorted(top_words,key=operator.itemgetter(1), reverse=True)[:count]
        
        return [x[0] for x in top_words]
