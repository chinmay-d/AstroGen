import torch
from sentence_transformers import SentenceTransformer
from torch.nn.functional import cosine_similarity

model_path = "models/nomic-ai/nomic-embed-text-v1"
embedding_model = SentenceTransformer(model_path, trust_remote_code=True, device="cpu")


async def load_documents(file_path="astrology_FAQs.txt"):
    """
    This function loads the astrology faqs file as a pair of question and answer as a single document.
    Returns a list
    """
    documents = list()
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # each block will be q and a
    blocks = content.strip().split("\n\n")

    for block in blocks:
        block = block.strip()
        if block:  
            documents.append(block)

    return documents


async def create_embeddings(text):
    return embedding_model.encode(text)


async def get_top_k(query, embeddings, docs, top_k=2):
    query_embedding = embedding_model.encode(query, convert_to_tensor=True) # query -> (D, ); embeddings -> (N, D)

    if not isinstance(embeddings, torch.Tensor):
        embeddings = torch.tensor(embeddings)

    simi = cosine_similarity(query_embedding.unsqueeze(0), embeddings, dim=1)
    top_k_scores, top_k_indices = torch.topk(simi, k=top_k)

    sentences = list()
    for i, top_k_index in enumerate(top_k_indices):
        item = (docs[top_k_index], top_k_scores[i])
        sentences.append(item)

    sentences = sorted(sentences, key=lambda x: x[1], reverse=True)
    # for sent in sentences:
    #     print(f"Score: {sent[1]}\nSentence: {sent[0]}")
    
    return sentences


async def run_RAG(query: str):
    docs = await load_documents()

    embeddings = [await create_embeddings(text) for text in docs]

    res = await get_top_k(query, embeddings, docs)

    return res


