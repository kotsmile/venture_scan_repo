from keras import layers, models, optimizers, preprocessing, callbacks


class Model:
    def __init__(self, word_features_dim, binary_features_dim):
        lstm_input_phrase = layers.Input(shape=(None, word_features_dim))
        lstm_input_cont = layers.Input(shape=(None, word_features_dim))
        dense_input = layers.Input(shape=(binary_features_dim,))

        lstm_emb_phrase = layers.LSTM(256)(lstm_input_phrase)
        lstm_emb_phrase = layers.Dense(128, activation='relu')(lstm_emb_phrase)

        lstm_emb_cont = layers.LSTM(256)(lstm_input_cont)
        lstm_emb_cont = layers.Dense(128, activation='relu')(lstm_emb_cont)

        dense_emb = layers.Dense(512, activation='relu')(dense_input)
        dense_emb = layers.Dense(256, activation='relu')(dense_emb)

        x = layers.concatenate([lstm_emb_phrase, lstm_emb_cont, dense_emb])
        x = layers.Dense(128, activation='relu')(x)
        x = layers.Dense(64, activation='relu')(x)
        x = layers.Dense(32, activation='relu')(x)

        main_output = layers.Dense(1, activation='sigmoid')(x)

        self.model = models.Model(inputs=[lstm_input_phrase, lstm_input_cont, dense_input],
                                  outputs=main_output)

        optimizer = optimizers.Adam(lr=0.0001)

        self.model.compile(optimizer=optimizer, loss='binary_crossentropy')

    # y = self.raw_predict(np.array([word_vec, vec, vec, vec, ...]), np.array([binary_vec]))
    def fit(self, x_lstm_phrase, x_lstm_context, x_dense, y,
            val_split=0.25, patience=5, max_epochs=1000, batch_size=32):
        x_lstm_phrase_seq = preprocessing.sequence.pad_sequences(x_lstm_phrase)
        x_lstm_context_seq = preprocessing.sequence.pad_sequences(x_lstm_context)

        self.model.fit([x_lstm_phrase_seq, x_lstm_context_seq, x_dense],
                       y,
                       batch_size=batch_size,
                       epochs=max_epochs,
                       validation_split=val_split,
                       callbacks=[callbacks.EarlyStopping(monitor='val_loss', patience=patience)]
                       )

    def raw_predict(self, x_lstm_phrase, x_lstm_context, x_dense):
        x_lstm_phrase_seq = preprocessing.sequence.pad_sequences(x_lstm_phrase)
        x_lstm_context_seq = preprocessing.sequence.pad_sequences(x_lstm_context)

        y = self.model.predict([x_lstm_phrase_seq, x_lstm_context_seq, x_dense])

        return y

    def predict(self, title, vector_model):
        pass

    def score(self, x_dense_title_test, x_dense_binary_test, y_test):
        pass
        # y = self.raw_predict(x_dense_title_test, x_dense_binary_test)
        # losses_cross_entropy = []
        # for y_true, y_pred in zip(y_test, y):
        #     y_pred = y_pred[0]
        #     loss_cross_entropy = cross_entropy(y_pred, y_true)
        #     losses_cross_entropy.append(loss_cross_entropy)
        # return mean(losses_cross_entropy)
