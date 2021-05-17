# -*- coding: utf-8 -*-
# @Author: bo.shi
# @Date:   2019-12-30 19:26:53
# @Last Modified by:   bo.shi
# @Last Modified time: 2020-01-01 11:39:23
""" CLUE processors and helpers """

import logging
import os
import torch
import pdb
from random import sample
from .utils import DataProcessor, InputExample, InputFeatures

logger = logging.getLogger(__name__)


def collate_fn(batch):
    """
    batch should be a list of (sequence, target, length) tuples...
    Returns a padded tensor of sequences sorted from longest to shortest,
    """
    all_input_ids, all_attention_mask, all_token_type_ids, all_lens, all_labels = map(torch.stack, zip(*batch))
    max_len = max(all_lens).item()
    all_input_ids = all_input_ids[:, :max_len]
    all_attention_mask = all_attention_mask[:, :max_len]
    all_token_type_ids = all_token_type_ids[:, :max_len]
    return all_input_ids, all_attention_mask, all_token_type_ids, all_labels


def xlnet_collate_fn(batch):
    """
    batch should be a list of (sequence, target, length) tuples...
    Returns a padded tensor of sequences sorted from longest to shortest,
    """
    all_input_ids, all_attention_mask, all_token_type_ids, all_lens, all_labels = map(torch.stack, zip(*batch))
    max_len = max(all_lens).item()
    all_input_ids = all_input_ids[:, -max_len:]
    all_attention_mask = all_attention_mask[:, -max_len:]
    all_token_type_ids = all_token_type_ids[:, -max_len:]
    return all_input_ids, all_attention_mask, all_token_type_ids, all_labels


def clue_convert_examples_to_features(examples, tokenizer,
                                      max_length=512,
                                      task=None,
                                      label_list=None,
                                      output_mode=None,
                                      pad_on_left=False,
                                      pad_token=0,
                                      pad_token_segment_id=0,
                                      mask_padding_with_zero=True):
    """
    Loads a data file into a list of ``InputFeatures``
    Args:
        examples: List of ``InputExamples`` or ``tf.data.Dataset`` containing the examples.
        tokenizer: Instance of a tokenizer that will tokenize the examples
        max_length: Maximum example length
        task: CLUE task
        label_list: List of labels. Can be obtained from the processor using the ``processor.get_labels()`` method
        output_mode: String indicating the output mode. Either ``regression`` or ``classification``
        pad_on_left: If set to ``True``, the examples will be padded on the left rather than on the right (default)
        pad_token: Padding token
        pad_token_segment_id: The segment ID for the padding token (It is usually 0, but can vary such as for XLNet where it is 4)
        mask_padding_with_zero: If set to ``True``, the attention mask will be filled by ``1`` for actual values
            and by ``0`` for padded values. If set to ``False``, inverts it (``1`` for padded values, ``0`` for
            actual values)

    Returns:
        If the input is a list of ``InputExamples``, will return
        a list of task-specific ``InputFeatures`` which can be fed to the model.

    """
    if task is not None:
        processor = clue_processors[task]()
        if label_list is None:
            label_list = processor.get_labels()
            logger.info("Using label list %s for task %s" % (label_list, task))
        if output_mode is None:
            output_mode = clue_output_modes[task]
            logger.info("Using output mode %s for task %s" % (output_mode, task))

    label_map = {label: i for i, label in enumerate(label_list)}

    features = []
    for (ex_index, example) in enumerate(examples):
        if ex_index % 10000 == 0:
            logger.info("Writing example %d" % (ex_index))

        inputs = tokenizer.encode_plus(
            example.text_a,
            example.text_b,
            add_special_tokens=True,
            max_length=max_length
        )
        input_ids, token_type_ids = inputs["input_ids"], inputs["token_type_ids"]

        # The mask has 1 for real tokens and 0 for padding tokens. Only real
        # tokens are attended to.
        attention_mask = [1 if mask_padding_with_zero else 0] * len(input_ids)
        input_len = len(input_ids)
        # Zero-pad up to the sequence length.
        padding_length = max_length - len(input_ids)
        if pad_on_left:
            input_ids = ([pad_token] * padding_length) + input_ids
            attention_mask = ([0 if mask_padding_with_zero else 1] * padding_length) + attention_mask
            token_type_ids = ([pad_token_segment_id] * padding_length) + token_type_ids
        else:
            input_ids = input_ids + ([pad_token] * padding_length)
            attention_mask = attention_mask + ([0 if mask_padding_with_zero else 1] * padding_length)
            token_type_ids = token_type_ids + ([pad_token_segment_id] * padding_length)

        assert len(input_ids) == max_length, "Error with input length {} vs {}".format(len(input_ids), max_length)
        assert len(attention_mask) == max_length, "Error with input length {} vs {}".format(len(attention_mask),
                                                                                            max_length)
        assert len(token_type_ids) == max_length, "Error with input length {} vs {}".format(len(token_type_ids),
                                                                                            max_length)
        if output_mode == "classification":
            label = label_map[example.label]
        elif output_mode == "regression":
            label = float(example.label)
        else:
            raise KeyError(output_mode)

        if ex_index < 20:
            logger.info("*** Example ***")
            logger.info(tokenizer.decode(input_ids))
            logger.info("guid: %s" % (example.guid))
            logger.info("input_ids: %s" % " ".join([str(x) for x in input_ids]))
            logger.info("attention_mask: %s" % " ".join([str(x) for x in attention_mask]))
            logger.info("token_type_ids: %s" % " ".join([str(x) for x in token_type_ids]))
            logger.info("label: %s (id = %d)" % (example.label, label))
            logger.info("input length: %d" % (input_len))

        features.append(
            InputFeatures(input_ids=input_ids,
                          attention_mask=attention_mask,
                          token_type_ids=token_type_ids,
                          label=label,
                          input_len=input_len))
    return features

class CsldcpProcessor(DataProcessor):

    def get_train_examples(self, data_dir,task_label_description):
        """See base class."""
        return self._create_examples(
            self._read_json(os.path.join(data_dir, "train_0.json")), "train",task_label_description)

    def get_dev_examples(self, data_dir,task_label_description):
        """See base class."""
        return self._create_examples(
            self._read_json(os.path.join(data_dir, "dev_0.json")), "dev",task_label_description)

    def get_test_examples(self, data_dir,task_label_description):
        """See base class."""
        return self._create_examples(
            self._read_json(os.path.join(data_dir, "test_public.json")), "test",task_label_description)

    def get_labels(self):
        """See base class."""
        labels = ["entail","not_entail"]
        return labels

    def _create_examples(self, lines, set_type,task_label_description):
        """Creates examples for the training and dev sets."""

        label_sentences_dict={}
        for (i, line) in enumerate(lines):
            text_a = line['content']
            label=line["label"]
            if label not in label_sentences_dict:
                label_sentences_dict[label]=[]
            label_sentences_dict[label].append(text_a)

        index=0
        examples = []
        K=min([len(value) for key,value in label_sentences_dict.items()])
        test_sentences_labels=[]

        for key,value in label_sentences_dict.items():
            if set_type=="test":
                for sentence in value:
                    test_sentences_labels.append(task_label_description[key])
                    for _,label_description in task_label_description.items():
                        text_a=sentence
                        text_b=label_description
                        guid=str(index)
                        examples.append(InputExample(guid=guid, text_a=text_a, text_b=text_b, label="not_entail"))
                        index+=1
            else:
                for sentence in value:
                    text_a=sentence
                    text_b=task_label_description[key]
                    guid=str(index)
                    examples.append(InputExample(guid=guid, text_a=text_a, text_b=text_b, label="entail"))
                    index+=1
                not_this_label_sentences=[]
                for _key,_value in label_sentences_dict.items():
                    if _key!=key:
                        not_this_label_sentences.extend(_value)
                negative_sentences=sample(not_this_label_sentences,8*K)
                for sentence in negative_sentences:
                    text_a=sentence
                    text_b=task_label_description[key]
                    guid=str(index)
                    examples.append(InputExample(guid=guid, text_a=text_a, text_b=text_b, label="not_entail"))
                    index+=1

        return examples,test_sentences_labels

class EprstmtProcessor(DataProcessor):

    def get_train_examples(self, data_dir,task_label_description):
        """See base class."""
        return self._create_examples(
            self._read_json(os.path.join(data_dir, "train_0.json")), "train",task_label_description)

    def get_dev_examples(self, data_dir,task_label_description):
        """See base class."""
        return self._create_examples(
            self._read_json(os.path.join(data_dir, "dev_0.json")), "dev",task_label_description)

    def get_test_examples(self, data_dir,task_label_description):
        """See base class."""
        return self._create_examples(
            self._read_json(os.path.join(data_dir, "test_public.json")), "test",task_label_description)

    def get_labels(self):
        """See base class."""
        labels = ["entail","not_entail"]
        return labels

    def _create_examples(self, lines, set_type,task_label_description):
        """Creates examples for the training and dev sets."""

        label_sentences_dict={}
        for (i, line) in enumerate(lines):
            text_a = line['sentence']
            label=line["label"]
            if label not in label_sentences_dict:
                label_sentences_dict[label]=[]
            label_sentences_dict[label].append(text_a)

        index=0
        examples = []
        K=min([len(value) for key,value in label_sentences_dict.items()])
        test_sentences_labels=[]

        for key,value in label_sentences_dict.items():
            if set_type=="test":
                for sentence in value:
                    test_sentences_labels.append(task_label_description[key])
                    for _,label_description in task_label_description.items():
                        text_a=sentence
                        text_b=label_description
                        guid=str(index)
                        examples.append(InputExample(guid=guid, text_a=text_a, text_b=text_b, label="not_entail"))
                        index+=1
            else:
                for sentence in value:
                    text_a=sentence
                    text_b=task_label_description[key] #这表达了正面的情感
                    guid=str(index)
                    examples.append(InputExample(guid=guid, text_a=text_a, text_b=text_b, label="entail"))
                    index+=1
                not_this_label_sentences=[]
                for _key,_value in label_sentences_dict.items():
                    if _key!=key:
                        not_this_label_sentences.extend(_value)
                negative_sentences=sample(not_this_label_sentences,K)
                for sentence in negative_sentences:
                    text_a=sentence
                    text_b=task_label_description[key]
                    guid=str(index)
                    examples.append(InputExample(guid=guid, text_a=text_a, text_b=text_b, label="not_entail"))
                    index+=1

        return examples,test_sentences_labels


class BustmProcessor(DataProcessor):

    def get_train_examples(self, data_dir,task_label_description):
        """See base class."""
        return self._create_examples(
            self._read_json(os.path.join(data_dir, "train_0.json")), "train",task_label_description)

    def get_dev_examples(self, data_dir,task_label_description):
        """See base class."""
        return self._create_examples(
            self._read_json(os.path.join(data_dir, "dev_0.json")), "dev",task_label_description)

    def get_test_examples(self, data_dir,task_label_description):
        """See base class."""
        return self._create_examples(
            self._read_json(os.path.join(data_dir, "test_public.json")), "test",task_label_description)

    def get_labels(self):
        """See base class."""
        labels = ["entail","not_entail"]
        return labels

    def _create_examples(self, lines, set_type,task_label_description):
        """Creates examples for the training and dev sets."""

        label_sentences_dict={}
        test_sentences_labels=[]
        examples = []
        for (i, line) in enumerate(lines):
            text_a = line['sentence1']
            text_b=line["sentence2"]
            label=line["label"]
            guid=str(i)
            if label=="1":
                examples.append(InputExample(guid=guid, text_a=text_a, text_b=text_b, label="entail"))
            else:
                examples.append(InputExample(guid=guid, text_a=text_a, text_b=text_b, label="not_entail"))
            if set_type=="test":
                test_sentences_labels.append(task_label_description[label])

        return examples,test_sentences_labels

class TnewsProcessor(DataProcessor):
    """Processor for the TNEWS data set (CLUE version)."""

    def get_train_examples(self, data_dir,task_label_description):
        """See base class."""
        return self._create_examples(
            self._read_json(os.path.join(data_dir, "train_0.json")), "train",task_label_description)

    def get_dev_examples(self, data_dir,task_label_description):
        """See base class."""
        return self._create_examples(
            self._read_json(os.path.join(data_dir, "dev_0.json")), "dev",task_label_description)

    def get_test_examples(self, data_dir,task_label_description):
        """See base class."""
        return self._create_examples(
            self._read_json(os.path.join(data_dir, "test_public.json")), "test",task_label_description)

    def get_labels(self):
        """See base class."""
        labels = ["entail","not_entail"]
        return labels

    def _create_examples(self, lines, set_type,task_label_description):
        """Creates examples for the training and dev sets."""

        label_sentences_dict={}
        for (i, line) in enumerate(lines):
            text_a = line['sentence']
            label_desc=line["label_desc"]
            if label_desc not in label_sentences_dict:
                label_sentences_dict[label_desc]=[]
            label_sentences_dict[label_desc].append(text_a)

        index=0
        examples = []
        K=max([len(value) for key,value in label_sentences_dict.items()])
        test_sentences_labels=[]

        for key,value in label_sentences_dict.items():
            if set_type=="test":
                for sentence in value:
                    test_sentences_labels.append(task_label_description[key])
                    for _,label_description in task_label_description.items():
                        text_a=sentence
                        text_b=label_description
                        guid=str(index)
                        examples.append(InputExample(guid=guid, text_a=text_a, text_b=text_b, label="not_entail"))
                        index+=1
            else:
                for sentence in value:
                    text_a=sentence
                    text_b=task_label_description[key]# 这是一条科技新闻
                    guid=str(index)
                    examples.append(InputExample(guid=guid, text_a=text_a, text_b=text_b, label="entail"))
                    index+=1
                not_this_label_sentences=[]
                for _key,_value in label_sentences_dict.items():
                    if _key!=key:
                        not_this_label_sentences.extend(_value)
                negative_sentences=sample(not_this_label_sentences,8*K)
                for sentence in negative_sentences:
                    text_a=sentence
                    text_b=task_label_description[key]
                    guid=str(index)
                    examples.append(InputExample(guid=guid, text_a=text_a, text_b=text_b, label="not_entail"))
                    index+=1

        return examples,test_sentences_labels


class IflytekProcessor(DataProcessor):
    """Processor for the IFLYTEK data set (CLUE version)."""

    def get_train_examples(self, data_dir,task_label_description):
        """See base class."""
        return self._create_examples(
            self._read_json(os.path.join(data_dir, "train_0.json")), "train",task_label_description)

    def get_dev_examples(self, data_dir,task_label_description):
        """See base class."""
        return self._create_examples(
            self._read_json(os.path.join(data_dir, "dev_0.json")), "dev",task_label_description)

    def get_test_examples(self, data_dir,task_label_description):
        """See base class."""
        return self._create_examples(
            self._read_json(os.path.join(data_dir, "test_public.json")), "test",task_label_description)

    def get_labels(self):
        """See base class."""
        labels = ["entail","not_entail"]
        return labels

    def _create_examples(self, lines, set_type,task_label_description):
        """Creates examples for the training and dev sets."""

        label_sentences_dict={}
        for (i, line) in enumerate(lines):
            text_a = line['sentence']
            label_desc=line["label_des"]
            if label_desc not in label_sentences_dict:
                label_sentences_dict[label_desc]=[]
            label_sentences_dict[label_desc].append(text_a)

        index=0
        examples = []
        K=max([len(value) for key,value in label_sentences_dict.items()])
        test_sentences_labels=[]

        for key,value in label_sentences_dict.items():
            if set_type=="test":
                for sentence in value:
                    test_sentences_labels.append(task_label_description[key])
                    for _,label_description in task_label_description.items():
                        text_a=sentence
                        text_b=label_description
                        guid=str(index)
                        examples.append(InputExample(guid=guid, text_a=text_a, text_b=text_b, label="not_entail"))
                        index+=1
            else:
                for sentence in value:
                    text_a=sentence
                    text_b=task_label_description[key]
                    guid=str(index)
                    examples.append(InputExample(guid=guid, text_a=text_a, text_b=text_b, label="entail"))
                    index+=1
                not_this_label_sentences=[]
                for _key,_value in label_sentences_dict.items():
                    if _key!=key:
                        not_this_label_sentences.extend(_value)
                negative_sentences=sample(not_this_label_sentences,8*K)
                for sentence in negative_sentences:
                    text_a=sentence
                    text_b=task_label_description[key]
                    guid=str(index)
                    examples.append(InputExample(guid=guid, text_a=text_a, text_b=text_b, label="not_entail"))
                    index+=1

        return examples,test_sentences_labels


class OcnliProcessor(DataProcessor):
    """Processor for the CMNLI data set (CLUE version)."""

    def get_train_examples(self, data_dir):
        """See base class."""
        return self._create_examples(
            self._read_json(os.path.join(data_dir, "train.json")), "train")

    def get_dev_examples(self, data_dir):
        """See base class."""
        return self._create_examples(
            self._read_json(os.path.join(data_dir, "dev.json")), "dev")

    def get_test_examples(self, data_dir):
        """See base class."""
        return self._create_examples(
            self._read_json(os.path.join(data_dir, "test.json")), "test")

    def get_labels(self):
        """See base class."""
        return ["contradiction", "entailment", "neutral"]

    def _create_examples(self, lines, set_type):
        """Creates examples for the training and dev sets."""
        examples = []
        for (i, line) in enumerate(lines):
            guid = "%s-%s" % (set_type, i)
            text_a = line["sentence1"]
            text_b = line["sentence2"]
            label = str(line["label"]) if set_type != 'test' else 'neutral'
            if label.strip()=='-':
                continue
            examples.append(
                InputExample(guid=guid, text_a=text_a, text_b=text_b, label=label))
        return examples

class CslProcessor(DataProcessor):
    """Processor for the CSL data set (CLUE version)."""

    def get_train_examples(self, data_dir):
        """See base class."""
        return self._create_examples(
            self._read_json(os.path.join(data_dir, "train.json")), "train")

    def get_dev_examples(self, data_dir):
        """See base class."""
        return self._create_examples(
            self._read_json(os.path.join(data_dir, "dev.json")), "dev")

    def get_test_examples(self, data_dir):
        """See base class."""
        return self._create_examples(
            self._read_json(os.path.join(data_dir, "test.json")), "test")

    def get_labels(self):
        """See base class."""
        return ["0", "1"]

    def _create_examples(self, lines, set_type):
        """Creates examples for the training and dev sets."""
        examples = []
        for (i, line) in enumerate(lines):
            guid = "%s-%s" % (set_type, i)
            text_a = " ".join(line['keyword'])
            text_b = line['abst']
            label = str(line['label']) if set_type != 'test' else '0'
            examples.append(
                InputExample(guid=guid, text_a=text_a, text_b=text_b, label=label))
        return examples

clue_tasks_num_labels = {
    'iflytek': 116,
    'ocnli': 3,
    'csl': 2,
    'csldcp': 67,
    'tnews': 15,
    'eprstmt': 2,
    'bustm': 2,
}

clue_processors = {
    'tnews': TnewsProcessor,
    'iflytek': IflytekProcessor,
    'ocnli': OcnliProcessor,
    'csl': CslProcessor,
    'csldcp': CsldcpProcessor,
    'eprstmt': EprstmtProcessor,
    'bustm': BustmProcessor,
}

clue_output_modes = {
    'tnews': "classification",
    'iflytek': "classification",
    'ocnli': "classification",
    'csl': "classification",
    'csldcp': "classification",
    'eprstmt': "classification",
    'bustm': "classification",
}