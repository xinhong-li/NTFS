import torch
import torch.nn as nn
import torch.nn.functional as F

from bert import BertModel, BertConfig

class BertForSequenceClassification(nn.Module):

    def __init__(self, num_classes, config, tf_checkpoint_path=None):
        super(BertForSequenceClassification, self).__init__()

        self.num_classes = num_classes
        self.bert_model = BertModel(config)
        self.bert_model.from_tf_checkpoint(tf_checkpoint_path)

        self.linear = nn.Linear(self.bert_model.hidden_size, num_classes)
        self.dropout = nn.Dropout(0.1)

    def forward(self, inp):
        token_idxs, position_idxs, token_type_idxs = inp
        # all of shape (batch_size, seq_len)

        _, pooled_first_token_output = self.bert_model(token_idxs, position_idxs, token_type_idxs)
        # (batch_size, hidden_size)

        x = self.linear(self.dropout(pooled_first_token_output))
        # (batch_size, num_classes)
        return x

    def predict(self, inp):
        x = self.forward(inp)
        # (batch_size, num_classes)

        pred_classes = torch.argmax(F.softmax(x, dim=-1), dim=-1)
        # (batch_size)
        
        return pred_classes

class BertForSequenceLabeling(nn.Module):

    def __init__(self, num_classes, config, tf_checkpoint_path=None):
        super(BertForSequenceLabeling, self).__init__()

        self.num_classes = num_classes
        self.bert_model = BertModel(config)
        self.bert_model.from_tf_checkpoint(tf_checkpoint_path)

        self.linear = nn.Linear(self.bert_model.hidden_size, num_classes)
        self.dropout = nn.Dropout(0.1)

    def forward(self, inp):
        token_idxs, position_idxs, token_type_idxs = inp
        # all of shape (batch_size, seq_len)

        sequence_output, _ = self.bert_model(token_idxs, position_idxs, token_type_idxs)
        # (batch_size, seq_len, hidden_size)

        x = self.linear(self.dropout(sequence_output))
        # (batch_size, seq_len, num_classes)
        return x

    def predict(self, inp):
        x = self.forward(inp)
        # (batch_size, seq_len, num_classes)

        pred_labels = torch.argmax(F.softmax(x, dim=-1), dim=-1)
        # (batch_size, seq_len)
        
        return pred_labels

class BertForQuestionAnswering(nn.Module):

    def __init__(self, config, tf_checkpoint_path=None):
        super(BertForQuestionAnswering, self).__init__()

        self.bert_model = BertModel(config)
        self.bert_model.from_tf_checkpoint(tf_checkpoint_path)

        self.linear = nn.Linear(self.bert_model.hidden_size, 2)

        # QA no dropout in official implementation?
        # self.dropout = nn.Dropout(0.1)

    def forward(self, inp):
        token_idxs, position_idxs, token_type_idxs = inp
        # all of shape (batch_size, seq_len)

        sequence_output, _ = self.bert_model(token_idxs, position_idxs, token_type_idxs)
        # (batch_size, hidden_size)

        # x = self.linear(self.dropout(sequence_output))
        x = self.linear(sequence_output)
        # (batch_size, seq_len, 2)

        return x[:, :, 0], x[:, :, 1]

    def predict(self, inp):
        prob_start, prob_end = self.forward(inp)
        # (batch_size, seq_len)

        pred_start_idxs = torch.argmax(F.softmax(prob_start, dim=-1), dim=-1)
        pred_end_idxs = torch.argmax(F.softmax(prob_end, dim=-1), dim=-1)
        # (batch_size)
        
        return pred_start_idxs, pred_end_idxs


if __name__ == '__main__':

     # Usage
    config = BertConfig(json_path='../../bert_checkpoints/chinese-bert_chinese_wwm_L-12_H-768_A-12/bert_config.json')

    model_sc = BertForSequenceClassification(num_classes=5, config=config, tf_checkpoint_path='../../bert_checkpoints/chinese-bert_chinese_wwm_L-12_H-768_A-12/bert_model.ckpt')
    model_sl = BertForSequenceLabeling(num_classes=5, config=config, tf_checkpoint_path='../../bert_checkpoints/chinese-bert_chinese_wwm_L-12_H-768_A-12/bert_model.ckpt')
    model_qa = BertForQuestionAnswering(config=config, tf_checkpoint_path='../../bert_checkpoints/chinese-bert_chinese_wwm_L-12_H-768_A-12/bert_model.ckpt')

    token_idxs = torch.LongTensor([[100, 1, 2, 101, 3, 4, 101]])
    position_idxs = torch.LongTensor([[ 0 ,  1 ,  2 ,  3 ,  4 ,  5 ,  6 ]])
    token_type_idxs = torch.LongTensor([[ 0 ,  0 ,  0 ,  0 ,  1 ,  1 ,  1 ]])

    inp = token_idxs, position_idxs, token_type_idxs

    out = model_sc(inp)
    pred = model_sc.predict(inp)
    print (f'[Sequence Classification]\nout: {out.shape}, pred: {pred.shape}')

    out = model_sl(inp)
    pred = model_sl.predict(inp)
    print (f'[Sequence Labeling]\nout: {out.shape}, pred: {pred.shape}')

    out_s, out_e = model_qa(inp)
    pred_s, pred_e = model_qa.predict(inp)
    print (f'[Question Answering]\nout_s: {out_s.shape}, out_e: {out_e.shape}, pred_s: {pred_s.shape}, pred_e: {pred_e.shape}')
 





