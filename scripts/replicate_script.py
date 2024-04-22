import os
import replicate
import json

from PIL import Image
from urllib.request import urlretrieve

os.environ['REPLICATE_API_TOKEN'] = 'my-api-token'

# Comment out the following line if you want to see full logs
model_attr = [
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


'cover_image_url',
'description',
'github_url',
'id',
'license_url',
'name',
'owner',
'paper_url',
'run_count',
'url',
'visibility',

# <replicate.version.Versions object at 0x0000023E5B65BCB0>
# 'versions',

# Deprecated
# 'username',
]


def get_information_of_certain_model(model: replicate.model.Model):
    model_info = {}
    for attr in model_attr:
        model_info[attr] = getattr(model, attr)
    return model_info

models = replicate.collections.get("text-to-image").models
print(len(models))

# Automatic pagination using `replicate.paginate` (recommended)
models = []
for page in replicate.paginate(replicate.models.list):
    collections = [collection for page in replicate.paginate(replicate.collections.list) for collection in page]
    for collection in collections:
        if collection.slug == 'text-to-image':
            models.extend(page.results)
            if len(models) > 10:
                break



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
# class ReplicateWrapper:
#     def __init__(self, api_key):
#         self.__api_key = api_key
#
#     def run(self, model, input_args):
#         model = "lucataco/playground-v2.5-1024px-aesthetic:419269784d9e00c56e5b09747cfc059a421e0c044d5472109e129b746508c365" if model is None else model
#
#         input_args = {
#             "width": 768,
#             "height": 768,
#             "prompt": "Astronaut in a jungle, cold color palette, muted colors, detailed, 8k",
#             "num_outputs": 1,
#             "guidance_scale": 3,
#             "apply_watermark": True,
#             "negative_prompt": "ugly, deformed, noisy, blurry, distorted",
#             "prompt_strength": 0.8,
#             "num_inference_steps": 50,
#             "refine": "expert_ensemble_refiner",
#         } if input_args is None else input_args
#
#         output = replicate.run(
#             model,
#             input=input_args
#         )
#
#         return output
#
# wrapper = ReplicateWrapper("")
# model = 'stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b'
#
# # model.available_scheduler is necessary
# input_args = {
#     "width": 768,
#     "height": 768,
#     "prompt": "masterpiece, best quality",
#     "num_outputs": 1,
#     "guidance_scale": 3,
#     "apply_watermark": True,
#     "negative_prompt": "EasyNegative, (low quality, worst quality:1.4), (bad anatomy), (inaccurate limb:1.2), bad composition, inaccurate eyes, extra digit, fewer digits, (extra arms:1.2)",
#     "prompt_strength": 0.8,
#     "num_inference_steps": 50
# }
#
# output = wrapper.run(model, input_args)
# if output is not None and len(output) > 0:
#     urlretrieve(output[0], "out.png")
#     background = Image.open("out.png")
#
