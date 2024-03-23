import google.generativeai as genai
import abcs
import os

sys_prompt = "System prompt: You are currently summarizing the contents of a chat history between a group of people. Your job is to read the messages which are sent and then write a summary of all that happened in that chat. Some of the messages will be interleaved with data of different types and you will be provided only a text description of the image, and image will be marked by ##<img url='url of image'>## Description of image ##</img>## use this description for additional context."


class GeminiActor(abcs.LLMActor):
    def __init__(self, key) -> None:
        genai.configure(api_key=key)
        self.model = genai.GenerativeModel("gemini-pro")
        self.history_default = [
            {
                "role": "user",
                "parts": [sys_prompt],
            },
            {
                "role": "model",
                "parts": ["Understood."],
            },
            {
                "role": "user",
                "parts": [
                    """
wazupsteve — Yesterday at 21:31
morning when will u leave
we can go same time""",
                    """
infinitasium — Yesterday at 21:31
around 730
720-740
""",
                    """
wazupsteve — Yesterday at 21:31
alright
ill leave around 7.30-7.40
ill either wait at majestic or mysore road?
""",
                    """
infinitasium — Yesterday at 21:32
sure
wait at mysore road
no point waiting at majestic
""",
                    """
wazupsteve — Yesterday at 21:33
alright
""",
                ],
            },
            {
                "role": "model",
                "parts": [
                    "wazupsteve asks infinitasium when they'll be leaving. infinitasium says he'll leave around 730 and wazupsteve leaves at 730. They agree to meet at mysore road."
                ],
            },
        ]
        self.history = self.history_default.copy()

    def send_base(self, text_data, ser_data):
        self.history.append({"role": "user", "parts": text_data + ser_data})
        response = self.model.generate_content(self.history)
        self.history.append(response.candidates[0].content)
        return ''.join(p.text for p in response.candidates[0].content.parts);

    def send_prompt(self, text_data):
        self.history.append(
            {
                "role": "user",
                "parts": ["Answer this question from the previous chat", text_data],
            }
        )
        response = self.model.generate_content(self.history)
        self.history.append(response.candidates[0].content)
        return ''.join(p.text for p in response.candidates[0].content.parts);

    def clean(self):
        self.history = self.history_default.copy()
