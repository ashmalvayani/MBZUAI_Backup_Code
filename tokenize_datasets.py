import os
from transformers import AutoTokenizer
import pandas as pd
from tqdm import tqdm

folder_path = "/mnt/beegfs/fahad.khan/StarCoderData/star_coder_files"
tokenizer = AutoTokenizer.from_pretrained("LLM360/Amber")

filenames = os.listdir(folder_path)
filenames.sort()

total_tokens = 0
for path_ in filenames:
    path = os.path.join(folder_path, path_)
    print(path)
    df = pd.read_csv(path, lineterminator='\n')
    texts = df.content

    flag = False
    input_ids = []
    tokens_len = 0
    for text in tqdm(texts):
        try:
            input_id = tokenizer(text, return_tensors="pt").input_ids
            tokens = input_id[0].tolist()
            tokens.pop(0)
            input_ids.append(tokens)
            tokens_len += len(tokens)
        except:
            print(path_, "Causing error. Check manually")
            flag=True
            break
    
    if flag==False:
        print(f"Number of tokens in {path_} : {tokens_len}")
        total_tokens += tokens_len

        chunk_size = 2049
        input_ids = [input_ids[i:i + chunk_size] for i in range(0, len(input_ids), chunk_size)]
        if len(input_ids[-1])!=2049:
            input_ids.pop()

        df2 = pd.DataFrame()
        df2["token_ids"] = input_ids
        df2["source"] = ["starcoder"] * len(df2)

        file_name = f"Converted_Tokenized/{path_.replace('csv','jsonl')}"
        df2.to_json(f"{file_name}", orient="records", indent=None)

print(f"Total Number of Tokens comibed = {total_tokens}")
