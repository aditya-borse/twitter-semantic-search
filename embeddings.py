from sentence_transformers import SentenceTransformer
import chromadb, json

model = SentenceTransformer("all-MiniLM-L6-v2")
chroma_client = chromadb.PersistentClient(path='./chroma_data')
file_name = input('Enter json file name: ')

with open(file_name, 'r', encoding='utf-8') as f:
    all_tweets = json.load(f)

collection_name = 'tweets'
try:
    collection = chroma_client.create_collection(name=collection_name)
except Exception as e:
    print(f'collection {collection_name} exists already. using it')
    print(e)
    collection = chroma_client.get_collection(name=collection_name)

cnt = 1
for tweet in all_tweets:
    embedding = model.encode(tweet['text']).tolist()
    metadata = {
        'username': tweet['username'],
        'timestamp': tweet['timestamp'],
        'url': tweet['url'],
        'text': tweet['text']
    }
    collection.add(
        embeddings=[embedding],
        documents=[tweet['text']],
        metadatas=[metadata],
        ids=[tweet['url']]
    )
    print(f'added tweet {cnt}')
    cnt+=1

print(f'added {cnt} tweets to chroma')