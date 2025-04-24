import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig
from typing import List, Dict

from model_wrapper import ModelWrapperBase


class SaigaWrapper(ModelWrapperBase):
    """ Wrapper class for IlyaGusev/saiga_yandexgpt_8b """

    def __init__(self, system_prompt: str):
        super().__init__(system_prompt)

        self.system_prompt = system_prompt
        self.MODEL_NAME = "IlyaGusev/saiga_yandexgpt_8b"

        self.model = AutoModelForCausalLM.from_pretrained(
            self.MODEL_NAME,
            torch_dtype=torch.bfloat16,
            device_map="auto"
        )
        self.model.eval()

        self.tokenizer = AutoTokenizer.from_pretrained(self.MODEL_NAME)
        self.generation_config = GenerationConfig.from_pretrained(self.MODEL_NAME)

    def get_response(self, dialog: List[Dict], rag_information: str) -> str:

        messages = dialog.copy()
        messages.append({"role": "system", "content": rag_information + "\n" + self.system_prompt})

        prompt = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

        data = self.tokenizer(prompt, return_tensors="pt", add_special_tokens=False)
        data = {k: v.to(self.model.device) for k, v in data.items()}
        data.pop("token_type_ids", None)
        output_ids = self.model.generate(**data, generation_config=self.generation_config)[0]
        output_ids = output_ids[len(data["input_ids"][0]):]
        output = self.tokenizer.decode(output_ids, skip_special_tokens=True).strip()

        torch.cuda.empty_cache()

        return output
