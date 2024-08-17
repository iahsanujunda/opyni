import enum
import logging
import os

from langchain_community.callbacks import get_openai_callback
from langchain_community.document_loaders.text import TextLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.output_parsers.string import StrOutputParser
from rich import get_console
from rich.markdown import Markdown

import opyni.configuration as config
from opyni.exception import FileLoaderError

console = get_console()
_logger = logging.getLogger("rich")


@enum.unique
class ReturnCode(enum.IntEnum):
    """Return codes for Pynguin to signal result."""

    OK = 0
    """Symbolises that the execution ended as expected."""

    FAILED = 1
    """Symbolises that the execution failed."""


def run_opyni() -> ReturnCode:
    try:
        _logger.info("Test generation starting...")
        _logger.debug(f"input file to process: {config.configuration.input_file}")

        generator = TestGenerator(
            api_key=os.getenv("OPENAI_API_KEY"),
            source_file_location=config.configuration.input_file,
        )
        output = generator.generate()
        markdown = Markdown(output)
        console.print(markdown)

        _logger.info("Test generation ended!")
        return ReturnCode.OK
    except Exception as error:
        _logger.error(error)
        return ReturnCode.FAILED


def _get_prompt(additional="No extra instruction"):
    baseline_instructions = """
        # instruction
        You are coding assistant whose task is to generate unit test cases based on a python source code.
        Use pytest to write the test cases.
        When mocking is required, use `patch` decorator from `unittest.mock` package.
        If the mocked object need to be used in multiple test cases, make it into fixtures, take
        extra care of the scope of the fixtures.
    """

    additional_instruction = """
        # additional instruction
    """
    return baseline_instructions + additional_instruction + additional


class TestGenerator:
    def __init__(self, api_key, source_file_location):
        if not source_file_location.endswith(".py"):
            raise ValueError("The source file must be a .py file")
        self.llm = ChatOpenAI(
            openai_api_key=api_key,
            model="gpt-4o-mini",
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
            _logger.info(f"Total Tokens: {cb.total_tokens}")
            _logger.info(f"Prompt Tokens: {cb.prompt_tokens}")
            _logger.info(f"Completion Tokens: {cb.completion_tokens}")
            _logger.info(f"Total Cost (USD): ${cb.total_cost}")

            return output
