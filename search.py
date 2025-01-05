from sentence_transformers import SentenceTransformer
import chromadb

chroma_client = chromadb.PersistentClient(path='./chroma_data')
collection = chroma_client.get_collection(name='tweets')
model = SentenceTransformer('all-MiniLM-L6-v2')

def search_tweets(query, top_k=5):
    query_embedding = model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    return results

if __name__ == '__main__':
    query = input('Enter search query: ')
    search_results = search_tweets(query)
    print(search_results)