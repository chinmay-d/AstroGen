from huggingface_hub import snapshot_download
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

device = "cuda" if torch.cuda.is_available() else "cpu"
repo_id = "ai4bharat/indictrans2-en-indic-dist-200M"
local_dir = "models/indictrans2-en-indic-dist-200M"

# download full repo without symlinks
# snapshot_download(
#     repo_id=repo_id,
#     local_dir=local_dir,
#     local_dir_use_symlinks=False
# )

# load the tokenizer and model
tokenizer = AutoTokenizer.from_pretrained(local_dir, trust_remote_code=True, local_files_only=True)
model = AutoModelForSeq2SeqLM.from_pretrained(local_dir, trust_remote_code=True, local_files_only=True).to(device)
model.eval() #set the model to eval mode
model.config.use_cache = False #don't let the model use KV cache 

if hasattr(model, "generation_config"):
    model.generation_config.use_cache = False

async def translate(text, *, src_lang, tgt_lang):
    formatted = f"{src_lang} {tgt_lang} {text}"
    inputs = tokenizer(formatted, return_tensors="pt", truncation=True).to(device)
    with torch.inference_mode():
        ids = model.generate(**inputs, num_beams=5, max_length=256, use_cache=False)
    return tokenizer.decode(ids[0], skip_special_tokens=True)


#use
# text = "Hey I like eating pizza. What's your favorite food?"
# res = await translate(text, src_lang="eng_Latn", tgt_lang="hin_Deva")
# print(res)
