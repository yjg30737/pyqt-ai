import os
import replicate
import json

from PIL import Image
from urllib.request import urlretrieve

os.environ['REPLICATE_API_TOKEN'] = 'my_token'

# Replicate에서 일일이 모든 리스트를 로딩하는 것보다는
# 단지 몇 가지 인기있는 모델만 가져오는 것이 좋다.

# 일단 디폴트로 몇 가지 우리가 모델을 추가하고
# 사용자가 직접 지정할 수 있도록 우리가 링크를 제공해 주는 방법을 쓰는 것이 좋다.


# Comment out the following line if you want to see full logs
# model_attr = [
# Information
# 'construct',

# Long ones
# 'copy',
# 'default_example',
# 'dict',
# 'json',
# 'latest_version',
# 'predict',
# 'reload',

# <bound method BaseModel.parse_file of <class 'replicate.model.Model'>>
# 'from_orm',
# 'parse_file',
# 'parse_obj',
# 'parse_raw',
# 'schema',
# 'schema_json',
# 'update_forward_refs',
# 'validate',


# 'cover_image_url',
# 'description',
# 'github_url',
# 'id',
# 'license_url',
# 'name',
# 'owner',
# 'paper_url',
# 'run_count',
# 'url',
# 'visibility',

# <replicate.version.Versions object at 0x0000023E5B65BCB0>
# 'versions',

# Deprecated
# 'username',


# def get_information_of_certain_model(model: replicate.model.Model):
#     model_info = {}
#     for attr in model_attr:
#         model_info[attr] = getattr(model, attr)
#     return model_info
#
# models = replicate.collections.get("text-to-image").models
# print(len(models))
#
# # Automatic pagination using `replicate.paginate` (recommended)
# models = []
# for page in replicate.paginate(replicate.models.list):
#     collections = [collection for page in replicate.paginate(replicate.collections.list) for collection in page]
#     for collection in collections:
#         if collection.slug == 'text-to-image':
#             models.extend(page.results)
#             if len(models) > 10:
#                 break



# Manual pagination

# collections = [collection for page in replicate.paginate(replicate.collections.list) for collection in page if collection.slug == 'text-to-image']


def get_information_of_every_model(col_name):
    model_info_lst = []
    for model in replicate.collections.get(col_name).models:
        model_info = get_information_of_certain_model(model)
        model_info_lst.append(model_info)
    return model_info_lst

# model_info = get_information_of_every_model('text-to-image')
# # Save it as json
# with open('model_info.json', 'w') as f:
#     json.dump(model_info, f)

#
#
#



class ReplicateWrapper:
    def __init__(self, api_key):
        self.__api_key = api_key

    def set_api(self, api_key):
        self.__api_key = api_key

    def get_image_response(self, model, input_args):
        model = "lucataco/playground-v2.5-1024px-aesthetic:419269784d9e00c56e5b09747cfc059a421e0c044d5472109e129b746508c365" if model is None else model

        input_args = {
            "width": 768,
            "height": 768,
            "prompt": "Astronaut in a jungle, cold color palette, muted colors, detailed, 8k",
            "negative_prompt": "ugly, deformed, noisy, blurry, distorted",
        } if input_args is None else input_args

        input_args["num_outputs"] = 1 if "num_outputs" not in input_args else input_args["num_outputs"]
        input_args["guidance_scale"] = 3 if "guidance_scale" not in input_args else input_args["guidance_scale"]
        input_args["apply_watermark"] = True if "apply_watermark" not in input_args else input_args["apply_watermark"]
        input_args["prompt_strength"] = 0.8 if "prompt_strength" not in input_args else input_args["prompt_strength"]
        input_args["num_inference_steps"] = 50 if "num_inference_steps" not in input_args else input_args["num_inference_steps"]
        input_args["refine"] = "expert_ensemble_refiner" if "refine" not in input_args else input_args["refine"]

        output = replicate.run(
            model,
            input=input_args
        )

        return output

# Example usage

# wrapper = ReplicateWrapper("")
# model = 'stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b'
#
# # model.available_scheduler is necessary
# input_args = {
#     "width": 768,
#     "height": 768,
#     "prompt": "masterpiece, best quality, Jessica Chastain, high resolution, 8K, HDR, vampire, evil grin, beautiful girl, detailed hair, beautiful face, ultra detailed eyes, (hyperdetailed:1.15)",
#     "negative_prompt": "EasyNegative, (low quality, worst quality:1.4), (bad anatomy), (inaccurate limb:1.2), bad composition, inaccurate eyes, extra digit, fewer digits, (extra arms:1.2)",
# }
#
# output = wrapper.get_image_response(model, input_args)
# if output is not None and len(output) > 0:
#     urlretrieve(output[0], "out.png")
#     background = Image.open("out.png")
#
