import json
from typing import List, Dict, Tuple, Callable

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import BaseTool

from models.llm_base import BaseLLM
from models.llm_gpt import num_tokens_from_messages
from models.local_llm import LocalLLMChat 

class Llama2(BaseLLM):
    def __init__(
        self,
        system_prompt: str = "",
        model: str = "llama3.3",
        api_key: str = "",
        endpoint: str = "http://dvt-aiml.wv.mentorg.com:4000/v1/chat/completions",
        temperature: float = 0.4,
        top_p: float = 1,
        max_gen_len: int = 600,
        best_iter_buffer_resetting: str = "STABLE",
        compress_msg_algo: str = "best 3",
        prioritise_harder_bins: bool = True,  # not needed if compress_msg_algo as "Successful Difficult Responses"
    ):
        super().__init__(system_prompt, best_iter_buffer_resetting, prioritise_harder_bins)
        self.model_name = model
        self.generator = LocalLLMChat(model=model, api_key=api_key, endpoint=endpoint)
        self.temperature = temperature
        self.top_p = top_p
        self.max_gen_len = max_gen_len

        # conversation state
        self.messages: List[List[Dict[str, str]]] = [[]]
        self.recent_msgs: List[Dict[str, str]] = []
        if self.system_prompt:
            self.messages[-1].append({"role": "system", "content": self.system_prompt})

        # select compression algorithm
        self.compress_msg_algo: Callable[[], List[Dict[str, str]]] = \
            self.__resolve_msg_compress_algo(compress_msg_algo)

    def __resolve_msg_compress_algo(self, compress_msg_algo: str) -> Callable:
        if compress_msg_algo in ["best 3", "Successful Responses", "Successful Difficult Responses"]:
            return self.__best_3
        elif compress_msg_algo in ["best 2 recent 1", "Mixed Recent and Successful Responses"]:
            return self.__best_2_recent_1
        elif compress_msg_algo in ["recent 3", "Recent Responses"]:
            return self.__recent_3
        else:
            methods = ["recent 3", "best 3", "best 2 recent 1", "Recent Responses", \
                       "Mixed Recent and Successful Responses", "Successful Responses", \
                       "Successful Difficult Responses"]
            raise ValueError(
                f"Invalid conversation compression algorithm {compress_msg_algo}. " \
                f"Please use one of the following methods: {methods}"
            )

    def __str__(self):
        return self.model_name

    def __call__(self, prompt: str) -> Tuple[str, Tuple[int, int, int]]:
        self._compress_conversation()
        # append user prompt
        self.messages[-1].append({"role": "user", "content": prompt})
        self.recent_msgs.append({"role": "user", "content": prompt})

        # convert history to LangChain messages
        chat_messages = self._convert_history(self.messages[-1])
        ai_message = self.generator.invoke(chat_messages)
        response = ai_message.content 

        # append assistant response
        self.messages[-1].append({"role": "assistant", "content": response})
        self.recent_msgs.append({"role": "assistant", "content": response})
        self.total_msg_cnt += 1

        # token counting
        input_token = num_tokens_from_messages(
            [m for m in self.messages[-1][:-1]]
        )
        output_token = num_tokens_from_messages(
            [self.messages[-1][-1]]
        )
        total_token = input_token + output_token

        return response, (input_token, output_token, total_token)

    def _convert_history(
        self,
        history: List[Dict[str, str]]
    ) -> List:
        """
        Convert internal message dicts to LangChain message objects.
        """
        msgs = []
        for entry in history:
            role = entry.get("role")
            content = entry.get("content", "")
            if role == "system":
                msgs.append(SystemMessage(content=content))
            elif role == "user":
                msgs.append(HumanMessage(content=content))
            elif role == "assistant":
                msgs.append(AIMessage(content=content))
            elif role == "tool":
                msgs.append(ToolMessage(
                    tool_call_id=entry.get("tool_call_id", None),
                    content=content
                ))
        return msgs

    def _compress_conversation(self):
        if (
            self.best_iter_buffer_resetting in ["STABLE", "CLEAR"]
            and len(self.messages[-1]) < 4 + 2 * Llama2.REMAIN_ITER_NUM
        ):
            return
        if self.messages[-1] and self.messages[-1][0]["role"] == "system":
            init = self.messages[-1][:3]
        else:
            init = self.messages[-1][:2]
        self.messages[-1] = init + self.compress_msg_algo()

    def __best_3(self) -> List[Dict[str, str]]:
        return self._select_successful(n_best=3)

    def __best_2_recent_1(self) -> List[Dict[str, str]]:
        best = self._select_successful(n_best=2)
        recent = self.recent_msgs[-2:]
        return best + recent

    def __recent_3(self) -> List[Dict[str, str]]:
        return self.messages[-1][-6:]

    def reset(self):
        self.messages = [[]]
        if self.system_prompt:
            self.messages[-1].append({"role": "system", "content": self.system_prompt})
        if self.best_iter_buffer_resetting == "CLEAR":
            self.best_messages.clear()
