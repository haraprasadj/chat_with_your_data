from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.embeddings import LlamaCppEmbeddings, GPT4AllEmbeddings
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain.vectorstores import DocArrayInMemorySearch
from langchain.document_loaders import TextLoader, PyPDFLoader, PyPDFDirectoryLoader
from langchain.chains import RetrievalQA,  ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from langchain.llms import LlamaCpp, GPT4All
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

def load_db(file_path, chain_type, k):
    #######
    # define embedding
    
    # # OpenAI embeddings
    # embeddings = OpenAIEmbeddings()
   
    # # Llama-CPP embeddings
    # # too slow to create embeddings
    # embeddings = LlamaCppEmbeddings(model_path="models/ggml-model-q4_0.bin")
    #### Model downloaded from https://huggingface.co/Pi3141/alpaca-native-7B-ggml/blob/main/ggml-model-q4_0.bin
   
    # GPT4All embeddings
    embeddings = GPT4AllEmbeddings()

    # choose llm

    # OpenAI
    llm=ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)

    # # Llama cpp python
    # # too slow to query
    # # https://huggingface.co/models?sort=modified&search=ggml
    # llm=LlamaCpp(model_path="models/llama-7b.ggmlv3.q5_0.bin", verbose=True, n_ctx=4096)

    # # GPT4All
    # # too slow to query - https://github.com/hwchase17/langchain/issues/5016
    # # Callbacks support token-wise streaming
    # callbacks = [StreamingStdOutCallbackHandler()]
    # # Verbose is required to pass to the callback manager
    # llm = GPT4All(model="./models/orca-mini-3b.ggmlv3.q4_0.bin", callbacks=callbacks, verbose=True, n_threads=4)

    ##########

    # PROCESS

    # load documents
    loader = PyPDFDirectoryLoader(file_path)
    documents = loader.load()

    # split documents
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    docs = text_splitter.split_documents(documents)

    # create vector database from data
    db = DocArrayInMemorySearch.from_documents(docs, embeddings)

    # define retriever
    retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": k})

    # create a chatbot chain. Memory is managed externally.

    qa = ConversationalRetrievalChain.from_llm(
        llm=llm, 
        chain_type=chain_type, 
        retriever=retriever, 
        return_source_documents=True,
        return_generated_question=True,
    )

    return qa 