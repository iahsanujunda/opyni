from langchain_community.callbacks import get_openai_callback
from langchain_community.document_loaders.text import TextLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.output_parsers.string import StrOutputParser

from opyni.exception import FileLoaderError


def _get_prompt(additional=""):
    baseline_instructions = """
        # instruction
        You are coding assistant whose task is to generate unit test cases based on a python source code.
        Use pytest to write the test cases.
        When mocking is required, use `patch` decorator from `unittest.mock` package.
    """

    additional_instruction = """
        # additional instruction
    """
    return baseline_instructions + additional_instruction + additional


class TestGenerator:
    def __init__(self, api_key, source_file_location):
        if not source_file_location.endswith(".txt"):
            raise ValueError("The source file must be a .txt file")
        self.llm = ChatOpenAI(
            openai_api_key=api_key,
            model="gpt-4o",
        )
        self.source_file_location = source_file_location

    def generate(self, additional_instruction=""):
        try:
            loader = TextLoader(self.source_file_location)
            document = loader.load()
        except Exception as e:
            raise FileLoaderError(
                f"Failed to load the file {self.source_file_location}"
            ) from e

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    _get_prompt(additional=additional_instruction),
                ),
                ("human", "{input}"),
            ]
        )
        parser = StrOutputParser()

        chain = prompt | self.llm | parser

        with get_openai_callback() as cb:
            output = chain.invoke({"input": document})
            print(f"Total Tokens: {cb.total_tokens}")
            print(f"Prompt Tokens: {cb.prompt_tokens}")
            print(f"Completion Tokens: {cb.completion_tokens}")
            print(f"Total Cost (USD): ${cb.total_cost}")

            return output
