from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore, PineconeEmbeddings
from langchain_text_splitters.character import RecursiveCharacterTextSplitter

import os
from dotenv import load_dotenv

load_dotenv()

    
class PineconeManager():
    """
    In RAG structure, will be used in llm_manager.py to retrieve the most similar k documents as the additional contextual information added to the prompt template
    """

    def __init__(self) -> None:
        self.pc = Pinecone(
            api_key = os.getenv('PINECONE_API_KEY')
        )
        self.embeddings = PineconeEmbeddings(
            model="multilingual-e5-large",
            pinecone_api_key = os.environ['PINECONE_API_KEY']
        )
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size = 500, chunk_overlap = 0)

    def list_namespaces(self, index_name):

        index = self.pc.Index(index_name)

        return [namespace.name for namespace in index.list_namespaces()]
            
    
    def create_index(self, index_name):
        """
        Normally not used as for this application.
        """
        if not self.pc.has_index(index_name):
            self.pc.create_index_for_model(
                name = index_name,
                cloud = "aws",
                region="us-east-1",
                embed = {
                    "model":"multilingual-e5-large",
                    "field_map":{"text": "chunk_text"}
                }
            )

    """
    def list_indexes():
    """

    # * Use the 'easyessay' index
    def insert_docs(self, 
                    texts: str, 
                    namespace: str, 
                    index_name: str):
        
        """
        Note: namespace = LiteratureID. we can use this primary key to merge back to our Google Sheet
        """

        texts_ls = self.text_splitter.split_text(texts)

        metadatas: list[dict] = [{"content": chunk} for chunk in texts_ls]
        ids: list[str]        = [f"{namespace}_{i + 1}" for i in range(len(texts_ls))]

        vectorstores = PineconeVectorStore.from_texts(
            texts_ls, 
            embedding  = self.embeddings,
            index_name = index_name,
            namespace  = namespace,
            ids        = ids,
            metadatas  = metadatas
        )

    def search(self, query, k, namespace: str, index_name: str):

        vector_store = PineconeVectorStore(
            index = self.pc.Index(index_name),  # your Pinecone index
            embedding = self.embeddings,  # your embedding model
            namespace = namespace
        )

        docs = vector_store.similarity_search(
            query = query,
            k = k,
            namespace = namespace
        )

        docs = [
            doc.page_content for doc in docs
        ]

        return docs
    
    def delete_from_pinecone(self, namespace, index_name):
        index = self.pc.Index(index_name)
        index.delete_namespace(namespace = namespace)


def Pinecone_Upsert_RUN(contents, fileid, database_index_name, logger):
    """main function to upsert"""
    PC = PineconeManager()
    PC.insert_docs(
        texts = contents,
        namespace = fileid,
        index_name = database_index_name
    )
    logger.info("Literature has been successfully upserted!")




if __name__ == "__main__":
    print("Initializing pinecone manager...")
    PC              = PineconeManager()
    print("Done!")
    # print("inserting documents...")
    # PC.insert_docs(
    #     texts = "hello I am wally nice to meet you how are you doing? What's your major?",
    #     namespace = "test",
    #     index_name = "easyessay"
    # )

    # print("searching most similar page...")
    # results = PC.search(query = "停車場收入", k = 10, namespace = "LGmZr75V", index_name = "easyessay")
    # print("most similar page:")
    # print(results)

    # print("deleting documents...")
    # results = PC.delete_from_pinecone("guest123-CjEggwuL", "SOcial media", "easyessay")
    # print(results)