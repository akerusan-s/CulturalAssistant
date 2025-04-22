import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig
from typing import List, Dict

from model_wrapper import ModelWrapperBase


class DeepSeekWrapper(ModelWrapperBase):
    """ Wrapper class for deepseek-ai/deepseek-llm-7b-chat """

    def __init__(self, system_prompt: str):
        super().__init__(system_prompt)
        self.model_name = "deepseek-ai/deepseek-llm-7b-chat"
        self.system_prompt = system_prompt
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(self.model_name,
                                                          torch_dtype=torch.bfloat16,
                                                          device_map="auto")
        self.model.generation_config = GenerationConfig.from_pretrained(self.model_name)
        self.model.generation_config.pad_token_id = self.model.generation_config.eos_token_id

    def get_response(self, dialog: List[Dict], rag_information: str) -> str:

        messages = dialog.copy()
        messages.append({"role": "system", "content": rag_information + "\n" + self.system_prompt})

        input_tensor = self.tokenizer.apply_chat_template(messages, add_generation_prompt=True, return_tensors="pt")
        outputs = self.model.generate(input_tensor.to(self.model.device), max_new_tokens=200)

        result = self.tokenizer.decode(outputs[0][input_tensor.shape[1]:], skip_special_tokens=True)
        return result
