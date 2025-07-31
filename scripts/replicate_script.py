import os
import replicate
import json

from PIL import Image
from urllib.request import urlretrieve

from scripts.common import download_image_as_base64


def get_information_of_every_model(col_name):
    model_info_lst = []
    for model in replicate.collections.get(col_name).models:
        model_info = get_information_of_certain_model(model)
        model_info_lst.append(model_info)
    return model_info_lst


class ReplicateWrapper:
    def __init__(self, api_key):
        self.__api_key = api_key
        self.request_and_set_api(api_key)

    def request_and_set_api(self, api_key):
        """
        True all the time
        There is no way to know if the api key is valid or not
        :param api_key:
        :return:
        """
        self.__api_key = api_key
        os.environ["REPLICATE_API_TOKEN"] = self.__api_key
        return True

    def is_available(self):
        return True if self.__api_key is not None else False

    def get_image_response(self, model, input_args):
        try:
            model = (
                "lucataco/playground-v2.5-1024px-aesthetic:419269784d9e00c56e5b09747cfc059a421e0c044d5472109e129b746508c365"
                if model is None
                else model
            )

            input_args = (
                {
                    "width": 768,
                    "height": 768,
                    "prompt": "Astronaut in a jungle, cold color palette, muted colors, detailed, 8k",
                    "negative_prompt": "ugly, deformed, noisy, blurry, distorted",
                }
                if input_args is None
                else input_args
            )

            input_args["num_outputs"] = (
                1 if "num_outputs" not in input_args else input_args["num_outputs"]
            )
            input_args["guidance_scale"] = (
                3
                if "guidance_scale" not in input_args
                else input_args["guidance_scale"]
            )
            input_args["apply_watermark"] = (
                True
                if "apply_watermark" not in input_args
                else input_args["apply_watermark"]
            )
            input_args["prompt_strength"] = (
                0.8
                if "prompt_strength" not in input_args
                else input_args["prompt_strength"]
            )
            input_args["num_inference_steps"] = (
                50
                if "num_inference_steps" not in input_args
                else input_args["num_inference_steps"]
            )
            input_args["refine"] = (
                "expert_ensemble_refiner"
                if "refine" not in input_args
                else input_args["refine"]
            )

            output = replicate.run(model, input=input_args)

            if output is not None and len(output) > 0:
                return download_image_as_base64(output[0])
            else:
                raise Exception("No output")
        except Exception as e:
            raise e
