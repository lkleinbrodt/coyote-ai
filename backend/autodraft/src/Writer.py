from llama_index.core import VectorStoreIndex
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core import PromptTemplate
from llama_index.core.response_synthesizers import TreeSummarize
from llama_index.core.tools import QueryEngineTool
from llama_index.agent.openai import OpenAIAgent
from llama_index.core import Response
import os


class Writer:

    def __init__(self, index: VectorStoreIndex):
        self.index = index

        self.retriever = VectorIndexRetriever(
            self.index,
            similarity_top_k=10,
        )

        qa_prompt = PromptTemplate(
            (
                "You are a helpful assistant who is helping to fill out a report for a non-profit. The report is a pre-application form for a grant."
                "Currently you are working on the following prompt: "
                "```{query_str}```"
                "While doing your research on this, you've found the following information. Note that this is not the only information you have, but it is relevant to the prompt."
                "Extract as much information as you can from the context, and use it to write a response to the prompt."
                "Context information from multiple sources is below."
                "-----------------"
                "{context_str}"
                "----------------"
                "Given the information from multiple sources and not prior knowledge, write a response to the following prompt. Pretend you are actually filling out the form, so you should not give a pre-amble or conclusion, just respond to the prompt."
                "Prompt: {query_str}"
                "Response: "
            )
        )

        # TODO: can provide our own templates here
        self.streaming_response_synthesizer = TreeSummarize(
            summary_template=qa_prompt, streaming=True
        )

        self.response_synthesizer = TreeSummarize(
            summary_template=qa_prompt, streaming=False
        )

        self.query_engine = RetrieverQueryEngine(
            retriever=self.retriever, response_synthesizer=self.response_synthesizer
        )

        query_engine_tools = [
            QueryEngineTool.from_defaults(
                query_engine=self.query_engine,
                name="QueryEngine",
                description="Answers questions you have about the prompt. Works best with full, natural langugage questions.",
            )
        ]

        self.agent = OpenAIAgent.from_tools(
            tools=query_engine_tools,
            verbose=True,
            max_function_calls=10,
            system_prompt="You are a helpful assistant. Ask several questions to QueryEngine to better understand the prompt and then draft a response. Reply using only the information you received from QueryEngine and no prior knowledge.",
        )

    def write(self, query: str, streaming=False) -> Response:
        nodes = self.retriever.retrieve(query)
        if streaming:
            return self.streaming_response_synthesizer.synthesize(query, nodes)
        else:
            return self.response_synthesizer.synthesize(query, nodes)

    def chat(self, query: str):
        query += ". Ask clarifying questions to QueryEngine if needed."
        return self.agent.chat(query)
