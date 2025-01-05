from sentence_transformers import SentenceTransformer
import chromadb, os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY=os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

chroma_client = chromadb.PersistentClient(path='./chroma_data')
collection = chroma_client.get_collection(name='tweets')
model = SentenceTransformer('all-MiniLM-L6-v2')

gemini_model = genai.GenerativeModel('gemini-1.5-flash')

def search_tweets(query, top_k=5):
    query_embedding = model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    formatted_results = []
    for i in range(len(results['ids'][0])):
        formatted_results.append({
            'id': results['ids'][0][i],
            'text': results['documents'][0][i],
            'metadata': results['metadatas'][0][i],
            'distance': results['distances'][0][i]
        })

    return formatted_results

def generate_response(query, search_results, prompt_template):
    context = ""

    for result in search_results:
        context += f"Username: {result['metadata']['username']}\n"
        context += f"URL: {result['metadata']['url']}\n"
        context += f"Text: {result['text']}\n\n"
    
    full_prompt = prompt_template.format(query=query, context=context)
    response = gemini_model.generate_content(full_prompt)
    
    ans_start_idx = response.text.find("Answer")
    if ans_start_idx == -1:
        ans_start_idx = 0
    else:
        ans_start_idx += len("Answer:")
    
    answer_text = response.text[ans_start_idx:].strip()

    relevant_urls = []
    for result in search_results:
        if result['metadata']['url'] in answer_text:
            relevant_urls.append(result['metadata']['url'])
        
    return response.text, relevant_urls

def rewrite_query(query):
    prompt = f"""
    Rewrite the following user query to be more consise and focused suitable for a semantic search on a vector database:
    
    User Query: {query}

    Consise Query:
    """
    response = gemini_model.generate_content(prompt)
    return response.text.strip()

if __name__ == '__main__':
    query = input('Enter search query: ')

    rewritten_query = rewrite_query(query)
    print(f'Rewritten query: {rewritten_query}')

    search_results = search_tweets(rewritten_query)

    prompt_template = """
    You are a helpful assistant that answers questions based on provided context 
    from tweets. 
    
    Query: {query}
    
    Context:
    {context}
    
    Answer consisely, including the URLs of the most relevant tweets in your answer:
    """

    response, relevant_urls = generate_response(query, search_results, prompt_template)
    print("\nGenerated Response: ")
    print(response)

    if relevant_urls:
        print("\nRelevant URLs:")
        for url in relevant_urls:
            print(url)