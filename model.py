import tensorflow as tf
import os

from tensorflow.contrib.rnn import LSTMCell, MultiRNNCell, LSTMStateTuple
from tf_ops import linear, batch_norm
import numpy as np
from tensorflow.contrib.seq2seq.python.ops.helper import CustomHelper

class DementiaBankTextLSTM(object):

    def __init__(self):
        pass

    # def _complex_lstm(self, input):
    #     with tf.variable_scope("sequence_decoder"):
    #         out_cell = MultiRNNCell(
    #             [LSTMCell(self.input_size, state_is_tuple=True) for _ in range(self.num_layers)],
    #             state_is_tuple=True
    #         )
    #         # state = tf.random_normal((self.batch_size, self.input_size))
    #         # initial_state = tuple(LSTMStateTuple(state, state) for state in states)
    #         initial_state = out_cell.zero_state(self.batch_size, tf.float32)
    #         #inputs = tf.random_normal((self.batch_size, tf.reduce_max(self.length), self.input_size))
    #
    #         # dyanmic rnn runs through zeros to max sequence _length
    #         # must ignore subsequent elements in shorter sequences
    #         dec_outs, _ = tf.nn.dynamic_rnn(
    #             out_cell,
    #             inputs=inputs,
    #             initial_state=initial_state,
    #             sequence_length=self.length,
    #             dtype=tf.float32
    #         )
    #         helper = tf.contrib.seq2seq.InferenceHelper(
    #             lambda out: out,
    #             [self.input_size],
    #             tf.float32,
    #             initial_input,
    #             lambda end: [False] * self.batch_size
    #         )
    #         # helper = InferenceHelper(
    #         #     self.batch_size, self.input_size
    #         # )
    #
    #         decoder = tf.contrib.seq2seq.BasicDecoder(
    #             cell=out_cell,
    #             helper=helper,
    #             initial_state=initial_state
    #         )
    #         self.zeros_out, _, _ = tf.contrib.seq2seq.dynamic_decode(
    #            decoder=decoder,
    #            output_time_major=False,
    #            impute_finished=True,
    #            maximum_iterations=tf.reduce_max(self.length))
    #         return dec_outs

    def _build_loss_optimizer(self, pred_y):
        pass
    #
    # def _recognizer(self, xs):
    #     with tf.name_scope("recognizer") as scope:
    #         means_and_vars = []
    #         for i, x in enumerate(xs):
    #             with tf.variable_scope("x_{}".format(i)):
    #                 hidden = tf.nn.softplus(linear(x, self.hidden_size, 'r_x_to_hidden'))
    #                 hidden2 = tf.nn.softplus(linear(hidden, self.hidden_size, 'r_hidden_to_hidden'))
    #                 mean = linear(hidden2, self.latent_size, 'r_hidden_to_mean')
    #                 log_var = linear(hidden2, self.latent_size, 'r_hidden_to_var')
    #                 means_and_vars.append((mean, log_var))
    #         return means_and_vars
    #
    #
    # def _generator(self, zs):
    #     with tf.name_scope("generator") as scope:
    #         reconstructed_xs = []
    #         for i, z in enumerate(zs):
    #             with tf.variable_scope("z_{}".format(i)):
    #                 hidden = tf.nn.dropout(
    #                     tf.nn.softplus(linear(z, self.hidden_size, 'g_z_to_hidden')),
    #                     self.keep_prob
    #                 )
    #                 hidden2 = tf.nn.dropout(
    #                     tf.nn.softplus(linear(hidden, self.hidden_size, 'g_hidden_to_hidden')),
    #                     self.keep_prob
    #                 )
    #                 x_reconstructed = linear(hidden2, self.input_size, 'g_hidden_to_x')
    #                 reconstructed_xs.append(x_reconstructed)
    #         return reconstructed_xs

    # def _rnn_encoder(self, sequence):
    #     with tf.variable_scope("sequence_encoder"):
    #         in_cell = MultiRNNCell(
    #             [
    #                 tf.contrib.rnn.DropoutWrapper(
    #                     LSTMCell(self.input_size, state_is_tuple=True),
    #                     output_keep_prob=self.keep_prob,
    #                     state_keep_prob=self.keep_prob
    #                 ) for _ in range(self.num_layers)
    #             ],
    #             state_is_tuple=True
    #         )
    #
    #         state = tf.random_normal((self.batch_size, self.input_size))
    #         initial_state = (LSTMStateTuple(state, state),) * self.num_layers
    #         #initial_state = in_cell.zero_state(self.batch_size, tf.float32)
    #
    #         # using length we select the last output per sequence which
    #         # represents the sequence encoding
    #         self.length = tf.placeholder(tf.int32, shape=(self.batch_size,), name="lengths")
    #         self.enc_outs, self.enc_state = tf.nn.dynamic_rnn(
    #             in_cell,
    #             inputs=sequence,
    #             initial_state=initial_state,
    #             sequence_length=self.length,
    #             dtype=tf.float32
    #         )
    #         length = tf.squeeze(self.length)
    #
    #         last_c = tf.gather_nd(
    #             self.enc_outs,
    #             tf.stack([tf.range(self.batch_size), length - 1], axis=1)
    #         )
    #         hidden_states = []
    #         for tup in self.enc_state:
    #             last_h = tf.convert_to_tensor(tup.h)
    #             hidden_states.append(last_h)
    #         return hidden_states + [last_c]
    #         #tf.convert_to_tensor(self.enc_state[1].c)
    #
    #
    # def _rnn_decoder(self, states, initial_input):
    #     with tf.variable_scope("sequence_decoder"):
    #         out_cell = MultiRNNCell(
    #             [LSTMCell(self.input_size, state_is_tuple=True) for _ in range(self.num_layers)],
    #             state_is_tuple=True
    #         )
    #         # state = tf.random_normal((self.batch_size, self.input_size))
    #         initial_state = tuple(LSTMStateTuple(state, state) for state in states)
    #         #initial_state = out_cell.zero_state(self.batch_size, tf.float32)
    #         #inputs = tf.random_normal((self.batch_size, tf.reduce_max(self.length), self.input_size))
    #         inputs = tf.concat([
    #             tf.expand_dims(initial_input, 1),
    #             self.batch_input[:, :tf.reduce_max(self.length) - 1, :]
    #         ], axis=1)
    #
    #         zeros = [tf.zeros((self.batch_size, self.input_size)) for _ in range(1000)]
    #
    #         # dyanmic rnn runs through zeros to max sequence _length
    #         # must ignore subsequent elements in shorter sequences
    #         dec_outs, _ = tf.nn.dynamic_rnn(
    #             out_cell,
    #             inputs=inputs,
    #             initial_state=initial_state,
    #             sequence_length=self.length,
    #             dtype=tf.float32
    #         )
    #         helper = tf.contrib.seq2seq.InferenceHelper(
    #             lambda out: out,
    #             [self.input_size],
    #             tf.float32,
    #             initial_input,
    #             lambda end: [False] * self.batch_size
    #         )
    #         # helper = InferenceHelper(
    #         #     self.batch_size, self.input_size
    #         # )
    #
    #         decoder = tf.contrib.seq2seq.BasicDecoder(
    #             cell=out_cell,
    #             helper=helper,
    #             initial_state=initial_state
    #         )
    #         self.zeros_out, _, _ = tf.contrib.seq2seq.dynamic_decode(
    #            decoder=decoder,
    #            output_time_major=False,
    #            impute_finished=True,
    #            maximum_iterations=tf.reduce_max(self.length))
    #         return dec_outs


    # def _build_model(self, sequence_input):
    #     bn = batch_norm(self.batch_size)
    #     states_and_output = self._rnn_encoder(bn(sequence_input))
    #     self.means_and_vars = self._recognizer(states_and_output)
    #     self.zs = []
    #     for i, (mean, var) in enumerate(self.means_and_vars):
    #         tf.summary.histogram("in_mean{}".format(i), mean)
    #         tf.summary.histogram("in_log_var{}".format(i), var)
    #
    #         # # Sample step
    #         epsilon = tf.random_normal(
    #             [self.batch_size, self.latent_size],
    #             0, 1, dtype=tf.float32
    #         )
    #         z = mean + epsilon * tf.sqrt(tf.exp(var))
    #         tf.summary.histogram("z_{}".format(i), z)
    #         self.zs.append(z)
    #         # #
    #
    #     ds = self._generator(self.zs)
    #     self.sequence_output = self._rnn_decoder(ds[:-1], ds[-1])
    #
    #     return self.sequence_output, self.zs
    #
    # def _build_loss_optimizer(self, sequence_output):
    #     with tf.name_scope("optimizer"):
    #         #L2 distance for input to output
    #         dist = self.batch_input - sequence_output
    #         d2 = .5 * dist ** 2
    #         for i in range(2):
    #             tf.summary.image("zeros_feed{}".format(i), tf.expand_dims(self.zeros_out[i], 3), max_outputs=1)
    #         tf.summary.image("input", tf.expand_dims(self.batch_input, 3), max_outputs=1)
    #         tf.summary.image("dist", tf.expand_dims(d2, 3), max_outputs=1)
    #         tf.summary.image("output", tf.expand_dims(sequence_output, 3), max_outputs=1)
    #         tf.summary.image("enc_outs", tf.expand_dims(self.enc_outs, 3), max_outputs=1)
    #         # Calculate a per window loss per example
    #
    #         self.reconstr_loss = 100 * tf.reduce_mean(
    #             tf.reduce_sum(d2, [2, 1]) / tf.cast(self.length, tf.float32) / self.input_size
    #         )
    #
    #         # We want to match p = N(0, 1) with q = N(in_mean, in_var)
    #         # using the KL divergence
    #         self.kl_divergence = 0
    #         for mean, log_var in self.means_and_vars:
    #             self.kl_divergence += .5 * tf.reduce_mean(
    #                 log_var
    #                 + (1 + mean ** 2) / tf.exp(log_var)
    #                 - 1
    #             )
    #         self.kl_divergence /= len(self.means_and_vars)
    #         # Alternatively use the reverse-KL
    #         # self.kl_divergence = .5 * tf.reduce_mean(
    #         #     - self.in_log_var
    #         #     + (self.in_mean ** 2)
    #         #     + tf.exp(self.in_log_var)
    #         #     - 1
    #         # )
    #
    #         # Total loss, could use beta value to play with beta-vae
    #         self.loss = self.reconstr_loss + self.kl_divergence
    #         tvars = tf.trainable_variables()
    #         grads = tf.gradients(self.loss, tvars)
    #         grads, _ = tf.clip_by_global_norm(grads, 1)
    #         # And apply the gradients
    #         optimizer = tf.train.AdamOptimizer(self.learning_rate)
    #         gradients = zip(grads, tvars)
    #         self.train_step = optimizer.apply_gradients(gradients)
    #
    #         tf.summary.scalar("total_loss", self.loss)
    #         tf.summary.scalar("kl_divergence", self.kl_divergence)
    #         tf.summary.scalar("reconstruction_loss", self.reconstr_loss)

# Training

class DementiaBankAudioLSTM(object):

    def __init__(self,
                model_name,
                batch_size=32,
                # latent_size=32,
                num_layers=1,
                input_size=512,
                hidden_size=128,
                sequence_lengths=None,
                learning_rate=0.001,
                save_path="ckpt/default",
                keep_prob=0.9):
        # self.latent_size = latent_size
        self.num_layers = num_layers
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.keep_prob = keep_prob
        self.save_path = save_path
        self.target_size = 8

        self.batch_input = tf.placeholder(
            tf.float32,
            shape=(None, None, input_size),
            name="batch_input"
        )
        self.targets = tf.placeholder(
            tf.float32,
            shape=(None, self.target_size),
            name="batch_targets"
        )
        pred_y = self._build_model(self.batch_input)
        self._build_loss_optimizer(pred_y, self.targets)


        # Launch the session
        self.sess = tf.InteractiveSession()
        self.summary_op = tf.summary.merge_all()

        init = tf.global_variables_initializer()
        self.sess.run(init)
        self.saver = tf.train.Saver(tf.global_variables(), max_to_keep=100)
        self.summary_writer = tf.summary.FileWriter(save_path, self.sess.graph)

    def _build_model(self, inputs):
        lstm_out = self._simple_lstm(inputs)
        return self._proj_layer(lstm_out)

    def _simple_lstm(self, sequences):
        with tf.variable_scope("sequence_encoder"):
            bn = batch_norm(self.batch_size)

            in_cell = MultiRNNCell(
                [
                    # tf.contrib.rnn.DropoutWrapper(
                        LSTMCell(self.input_size, state_is_tuple=True)
                    #     output_keep_prob=self.keep_prob,
                    #     state_keep_prob=self.keep_prob
                    # ) for _ in range(self.num_layers)
                ],
                state_is_tuple=True
            )

            # state = tf.random_normal((self.batch_size, self.input_size))
            # initial_state = (LSTMStateTuple(state, state),) * self.num_layers
            initial_state = in_cell.zero_state(self.batch_size, tf.float32)

            # using length we select the last output per sequence which
            # represents the sequence encoding
            self.length = tf.placeholder(tf.int32, shape=(self.batch_size,), name="lengths")
            self.enc_outs, self.enc_state = tf.nn.dynamic_rnn(
                in_cell,
                inputs=bn(sequences),
                initial_state=initial_state,
                sequence_length=self.length,
                dtype=tf.float32
            )
            return tf.gather_nd(
                self.enc_outs,
                tf.stack([tf.range(self.batch_size), self.length - 1], axis=1)
            )

    def _proj_layer(self, enc_out):
        ok = linear(enc_out, self.target_size, 'r_x_to_target')
        return ok

    def _build_loss_optimizer(self, y_p, y_t):
        with tf.name_scope("optimizer"):
            #L2 distance for input to output
            self.y_p = y_p
            dist = y_p - y_t
            d2 = .5 * dist ** 2
            self.loss = tf.reduce_sum(d2) / self.batch_size / 8
            tvars = tf.trainable_variables()
            grads = tf.gradients(self.loss, tvars)
            grads, _ = tf.clip_by_global_norm(grads, 3)
            # And apply the gradients
            optimizer = tf.train.AdamOptimizer(self.learning_rate)
            gradients = zip(grads, tvars)
            self.train_step = optimizer.apply_gradients(gradients)
            tf.summary.scalar("total_loss", self.loss)

    def _train_batch(self, sequences, targets, length, i):
        print(targets)
        summary, opt, loss, y_p = self.sess.run(
            (self.summary_op, self.train_step, self.loss, self.y_p),
            feed_dict={
                self.batch_input: sequences,
                self.length: length,
                self.targets: targets
            }
        )
        self.summary_writer.add_summary(summary, i)
        print(y_p)
        return loss

    def train(self, batch, num_batches):
        for j in range(num_batches):
            spectrogram, scores = zip(*next(batch))
            # Now we have k, v pairs that must go into a tensor
            lengths = np.empty(self.batch_size, dtype=np.int64)
            for i, x in enumerate(spectrogram):
                lengths[i] = x.shape[0]
            sequences = np.zeros((self.batch_size, max(lengths), self.input_size))
            targets = np.zeros((self.batch_size, 8))
            if np.isnan(sequences).any():
                print("Oh WHAT")
            for i in range(self.batch_size):
                sequences[i, :lengths[i], :] = np.nan_to_num(spectrogram[i][:, :])
                targets[i, :] = scores[i]
            np.set_printoptions(threshold=np.nan)
            if np.isnan(sequences).any():
                print("OH NO")
            loss = self._train_batch(
                sequences,
                targets,
                lengths,
                j
            )
            print("Step: {}, Loss: {}".format(j, loss))

    def eval(self):
        pass

    def load(self, file_path):
        self.saver.restore(self.sess, file_path)

    def save(self, i):
        self.saver.save(self.sess, self.save_path, global_step=i)


if __name__ == "__main__":
    dbal = DementiaBankAudioLSTM()
    dbal.save()
