import os
from transformers import AutoModelForTokenClassification as amc, AutoTokenizer as at


MODEL_NAME = os.getenv('MODEL_NAME', 'dslim/bert-base-NER')
LOCAL_DIRECTORY = 'hf'

# Save tokenizer
tokenizer = at.from_pretrained(MODEL_NAME)
tokenizer.save_pretrained(LOCAL_DIRECTORY)

# Save model
model = amc.from_pretrained(MODEL_NAME)
model.save_pretrained(LOCAL_DIRECTORY)

# Save model name
with open(os.path.join(LOCAL_DIRECTORY, 'name.txt'), 'w') as name_file:
    name_file.write(MODEL_NAME)
