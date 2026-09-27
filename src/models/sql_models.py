import torch
import torch.nn as nn
import torch.nn.functional as F

class SQLCNN(nn.Module):
    def __init__(self, vocab_size, embed_dim=128, num_filters=100, filter_sizes=[3, 4, 5], dropout=0.5):
        super(SQLCNN, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.convs = nn.ModuleList([
            nn.Conv1d(in_channels=embed_dim, out_channels=num_filters, kernel_size=k) 
            for k in filter_sizes
        ])
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Linear(len(filter_sizes) * num_filters, 1)
        
    def forward(self, x):
        embedded = self.embedding(x).permute(0, 2, 1) 
        conved = [F.relu(conv(embedded)) for conv in self.convs]
        pooled = [F.max_pool1d(c, c.shape[2]).squeeze(2) for c in conved]
        cat = self.dropout(torch.cat(pooled, dim=1))
        return self.fc(cat)

class SQLLSTM(nn.Module):
    def __init__(self, vocab_size, embed_dim=128, hidden_dim=64, num_layers=2, dropout=0.5):
        super(SQLLSTM, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.lstm = nn.LSTM(embed_dim, hidden_dim, num_layers=num_layers, 
                            batch_first=True, dropout=dropout, bidirectional=True)
        self.dropout = nn.Dropout(dropout)
        # Multiply hidden_dim by 2 because it is a bidirectional LSTM
        self.fc = nn.Linear(hidden_dim * 2, 1)
        
    def forward(self, x):
        embedded = self.embedding(x)
        # lstm_out shape: (batch, seq_len, hidden_dim * 2)
        lstm_out, (hidden, cell) = self.lstm(embedded)
        # Extract the output of the final time step
        final_hidden = torch.cat((hidden[-2,:,:], hidden[-1,:,:]), dim=1)
        dropped = self.dropout(final_hidden)
        return self.fc(dropped)