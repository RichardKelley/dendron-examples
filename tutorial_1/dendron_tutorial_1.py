import dendron
from dendron.actions.causal_lm_action import CausalLMActionConfig, CausalLMAction
from dendron.conditions.completion_condition import CompletionConditionConfig, CompletionCondition
from dendron.controls import Sequence, Fallback
from dendron import NodeStatus

import torch

from piper import PiperVoice

from transformers import BarkModel, BarkProcessor
from optimum.bettertransformer import BetterTransformer
from spacy.lang.en import English 
import time
import numpy as np
import sounddevice as sd

class MoreToSay(dendron.ConditionNode):
    def __init__(self, speech_input_key="speech_in"):
        super().__init__("more_to_say")
        self.speech_input_key = speech_input_key

    def tick(self):
        if self.blackboard[self.speech_input_key] != []:
            return dendron.NodeStatus.SUCCESS
        else:
            return dendron.NodeStatus.FAILURE

class TimeToThink(dendron.ConditionNode):
    """
    PRE:
        blackboard[human_input_key] should be set
    POST:
    """
    def __init__(self, human_input_key = "latest_human_input"):
        super().__init__("time_to_think")
        self.human_input_key = human_input_key
        self.last_human_input = None
    
    def tick(self):
        human_input = self.blackboard[self.human_input_key]
        if self.last_human_input is not None and human_input != self.last_human_input:
            status = NodeStatus.SUCCESS
        else:
            status = NodeStatus.FAILURE

        self.last_human_input = human_input
        return status

'''
# I was surprised to learn that there is no emoji for an easter egg. 🤷‍♂️
import pyttsx3
class TTSAction(dendron.ActionNode):
    def __init__(self, name):
        super().__init__(name)
        self.engine = pyttsx3.init()
    
    def tick(self):
        try:
            input_text = self.blackboard["speech_in"].pop(0)
            self.engine.say(input_text)
            self.engine.runAndWait()
        
        except Exception as e:
            print("Speech generation exception: ", e)
            return dendron.NodeStatus.FAILURE
        
        return dendron.NodeStatus.SUCCESS
'''

'''
# Here's another option that doesn't work as well as Piper. From the first version of the tutorial
class TTSAction(dendron.ActionNode):
    def __init__(self, name):
        super().__init__(name)
        self.processor = BarkProcessor.from_pretrained("suno/bark-small", torch_dtype=torch.bfloat16, attn_implementation="flash_attention_2")
        self.model = BarkModel.from_pretrained("suno/bark-small").to("cuda")
        self.model = self.model.to_bettertransformer() #BetterTransformer.transform(self.model, keep_original_model=False)
        self.model.enable_cpu_offload()

    def tick(self):
        try:
            input_text = self.blackboard["speech_in"]
            inputs = self.processor(text=input_text, voice_preset="v2/en_speaker_9", return_tensors="pt").to("cuda")
            self.blackboard["speech_out"] = self.model.generate(**inputs, do_sample = True, fine_temperature = 0.4, coarse_temperature = 0.8).cpu().numpy()
            self.blackboard["speech_in"] = []
        except Exception as e:
            print("Speech generation exception: ", e)
            return dendron.NodeStatus.FAILURE
        
        return dendron.NodeStatus.SUCCESS

def play_speech(self):
    num_utterances = self.blackboard["speech_out"].shape[0]
    
    for i in range(num_utterances):
        sd.play(self.blackboard["speech_out"][i,:], self.model.generation_config.sample_rate)
        sd.wait()
'''

class TTSAction(dendron.ActionNode):
    def __init__(self, name):
        super().__init__(name)
        self.voice = PiperVoice.load("en_US-danny-low.onnx", config_path="en_US-danny-low.onnx.json", use_cuda=False)
        
    def tick(self):
        input_text = self.blackboard["speech_in"]
        try:
            self.blackboard["speech_out"] = [list(self.voice.synthesize_stream_raw(x, sentence_silence=0.1))[0] for x in input_text]
            self.blackboard["speech_in"] = []
        except Exception as e:
            print("Speech generation exception: ", e)
            return dendron.NodeStatus.FAILURE

        return dendron.NodeStatus.SUCCESS

def play_speech(self):
    num_utterances = len(self.blackboard["speech_out"])

    for i in range(num_utterances):
        audio = np.frombuffer(self.blackboard["speech_out"][i], dtype=np.int16)
        a = (audio - 32768) / 65536
        sd.play(a, 16000)
        sd.wait()

class SentenceSplitter(dendron.ActionNode):
    def __init__(self, in_key="speech_in"):
        super().__init__("sentence_splitter")
        self.in_key = in_key
        self.splitter = English()
        self.splitter.add_pipe("sentencizer")

    def tick(self):
        latest_text = self.blackboard[self.in_key].pop()
        if len(latest_text) > 64:
            sentences = self.splitter(latest_text).sents
            for s in sentences:
                s_prime = str(s).strip()
                if len(s_prime) > 0:
                    self.blackboard[self.in_key].append(s_prime)
        else:
            self.blackboard[self.in_key].append(latest_text)
        return NodeStatus.SUCCESS

class SayGoodbye(dendron.ActionNode):
    def __init__(self):
        super().__init__("say_goodbye")

    def tick(self):
        if self.blackboard["all_done"]:
            self.blackboard["speech_in"].append("Goodbye!")
            return NodeStatus.SUCCESS

def chat_to_str(self, chat):
    return self.tokenizer.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)

def str_to_chat(self, str):
    key = "GPT4 Correct Assistant:"
    idx = str.rfind(key)
    response = str[idx+len(key):]
    chat = self.blackboard[self.input_key]
    chat.append({"role" : "GPT4 Correct Assistant", "content" : response})
    return chat
    
def set_next_speech(self):
    text_output = self.blackboard["out"][-1]["content"]
    self.blackboard["speech_in"].append(text_output)

def farewell_success_fn(completion):
    """
    Return SUCCESS if the conversation is done.
    """
    if completion == "yes":
        return NodeStatus.SUCCESS
    else:
        return NodeStatus.FAILURE

def farewell_pretick(self):
    last_input = self.blackboard["latest_human_input"]
    chat = [{"role": "user", "content": f"""The last thing the human said was "{last_input}". Is the user saying Goodbye?"""}]
    self.blackboard[self.input_key] = self.tokenizer.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)

def farewell_posttick(self):
    if self.status == NodeStatus.SUCCESS:
        self.blackboard["all_done"] = True

