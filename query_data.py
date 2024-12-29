import argparse
# from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_community.llms.ollama import Ollama
from langchain_chroma import Chroma
 
from .get_embedding_function import get_embedding_function
CHROMA_PATH = rf"F:\ollama\rag\chroma"

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---
Note  : give answer only based on question if context not match with question give this answer  "your query not match" only don't give any other sentence if contect doesn't match
Answer the question based on the above context: {question}
"""


def main(query_text,category):
    # Create CLI.
  try :  
    ans = query_rag(query_text ,category)
    return ans
  except Exception as e:
    return {"Error": str(e)}

def query_rag(query_text: str ,category:str):
    # Prepare the DB.
    try :
        embedding_function = get_embedding_function()
        db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function )

        # Search the DB.
        results = db.similarity_search_with_score( query_text, k=5 ,filter={"category" :category} )

        context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
        prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
        prompt = prompt_template.format(context=context_text, question=query_text)
        # print(prompt)

        model = Ollama(model="llama3.1")
        response_text = model.invoke(prompt)
        print(response_text,"This Response Text")
        sources = [doc.metadata for doc, _score in results]
        formatted_response = f"Response: {response_text}\nSources: {sources}"
        print(formatted_response)
        return {"Success":response_text}
    except Exception as e:
       return {"Error": str(e)}