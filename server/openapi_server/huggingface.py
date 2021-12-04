import numpy as np
import torch
from typing import Union, List, Optional

from transformers import AutoTokenizer as at, \
    AutoModelForTokenClassification as amc, TokenClassificationPipeline
from transformers.pipelines import AggregationStrategy


# In-Vocab IDs for special tokens ([CLS], [SEP]) used by BERT
CLS_ID = 101
SEP_ID = 102


class SlidingWindowNERPipeline(TokenClassificationPipeline):
    """Modified version of TokenClassificationPipeline that uses a sliding
    window approach to fit long texts into the limited position embeddings of a
    transformer.
    """

    def __init__(self, window_length: Optional[int] = None,
                 stride: Optional[int] = None, *args, **kwargs):
        super(SlidingWindowNERPipeline, self).__init__(
            *args, **kwargs, aggregation_strategy=AggregationStrategy.FIRST)
        self.window_length = window_length or self.tokenizer.model_max_length
        if stride is None:
            self.stride = self.window_length // 2
        elif stride == 0:
            self.stride = self.window_length
        elif 0 < stride <= self.window_length:
            self.stride = stride
        else:
            raise ValueError("`stride` must be a positive integer no greater "
                             "than `window_length`")

    def __call__(self, inputs: Union[str, List[str]], **kwargs):
        """
        Classify each token of the text(s) given as inputs.

        Args:
            inputs (:obj:`str` or :obj:`List[str]`):
                One or several texts (or one list of texts) for token classification.

        Return:
            A list or a list of list of :obj:`dict`: Each result comes as a list of dictionaries (one for each token in
            the corresponding input, or each entity if this pipeline was instantiated with an aggregation_strategy)
            with the following keys:

            - **word** (:obj:`str`) -- The token/word classified.
            - **score** (:obj:`float`) -- The corresponding probability for :obj:`entity`.
            - **entity** (:obj:`str`) -- The entity predicted for that token/word (it is named `entity_group` when
              `aggregation_strategy` is not :obj:`"none"`.
            - **index** (:obj:`int`, only present when ``aggregation_strategy="none"``) -- The index of the
              corresponding token in the sentence.
            - **start** (:obj:`int`, `optional`) -- The index of the start of the corresponding entity in the sentence.
              Only exists if the offsets are available within the tokenizer
            - **end** (:obj:`int`, `optional`) -- The index of the end of the corresponding entity in the sentence.
              Only exists if the offsets are available within the tokenizer
        """

        _inputs, offset_mappings = self._args_parser(inputs, **kwargs)

        answers = []
        num_labels = self.model.num_labels

        for i, sentence in enumerate(_inputs):

            # Manage correct placement of the tensors
            with self.device_placement():

                tokens = self.tokenizer(
                    sentence,
                    padding=True,
                    return_attention_mask=False,
                    return_tensors=self.framework,
                    return_special_tokens_mask=True,
                    add_special_tokens=False,
                    return_offsets_mapping=self.tokenizer.is_fast
                )
                if self.tokenizer.is_fast:
                    offset_mapping = \
                        tokens.pop("offset_mapping").cpu().numpy()[0]
                elif offset_mappings:
                    offset_mapping = offset_mappings[i]
                else:
                    offset_mapping = None

                special_tokens_mask = \
                    tokens.pop("special_tokens_mask").cpu().numpy()[0]

                if self.framework == "tf":
                    raise ValueError("SlidingWindowNERPipeline does not "
                                     "support TensorFlow models.")
                # Forward inference pass
                with torch.no_grad():
                    tokens = self.ensure_tensor_on_device(**tokens)

                    # Get logits (i.e. tag scores)
                    entities = np.zeros(tokens['input_ids'].shape[1:] +
                                        (num_labels,))
                    writes = np.zeros(entities.shape)
                    for start in range(
                            0, tokens['input_ids'].shape[1] - 1,
                            self.stride):
                        end = start + self.window_length - 2
                        window_input_ids = torch.cat([
                            torch.tensor([[CLS_ID]]),
                            tokens['input_ids'][:, start:end],
                            torch.tensor([[SEP_ID]])
                        ], dim=1)
                        window_logits = self.model(
                            input_ids=window_input_ids)[0][0].cpu().numpy()
                        entities[start:end] += window_logits[1:-1]
                        writes[start:end] += 1
                    # Old way for getting logits under PyTorch
                    # entities = self.model(**tokens)[0][0].cpu().numpy()
                    input_ids = tokens["input_ids"].cpu().numpy()[0]
                    entities = entities / writes

                    scores = np.exp(entities) / np.exp(entities).sum(
                        -1, keepdims=True)
                    pre_entities = self.gather_pre_entities(
                        sentence, input_ids, scores, offset_mapping,
                        special_tokens_mask)
                    grouped_entities = self.aggregate(
                        pre_entities, self.aggregation_strategy)
                    # Filter anything that is in self.ignore_labels
                    entities = [
                        entity
                        for entity in grouped_entities
                        if entity.get("entity", None) not in self.ignore_labels
                        and entity.get("entity_group", None) not in
                        self.ignore_labels
                    ]
                    answers.append(entities)

        if len(answers) == 1:
            return answers[0]
        return answers


class HuggingFace:
    def __init__(self):
        self.tokenizer = at.from_pretrained("hf")
        self.model = amc.from_pretrained("hf")
        with open('hf/name.txt') as name_file:
            self.name = name_file.read()
        self.nlp = SlidingWindowNERPipeline(model=self.model,
                                            tokenizer=self.tokenizer)

    def get_entities(self, sample_text, labels):
        if sample_text == '':
            return []
        ner_results = self.nlp(sample_text)
        ner_results = [r for r in ner_results if
                       any(label in r['entity_group'] for label in labels)]
        return ner_results

    def get_name(self):
        return self.name


huggingFace = HuggingFace()
