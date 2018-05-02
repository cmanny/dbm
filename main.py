from dementiabank import DementiaBankData
from model import DementiaBankAudioLSTM

if __name__ == "__main__":
    test = False

    dbd = DementiaBankData()

    # textmodel = DementiaBankTextLSTM('textmodel')
    audiomodel = DementiaBankAudioLSTM(
        'audiomodel',
        batch_size=32,
        num_layers=1,
        input_size=1024,
        hidden_size=1024,
        sequence_lengths=None,
        learning_rate=0.001,
        save_path="ckpt/default",
        keep_prob=0.9
    )

    if False:
        # textmodel.load()
        audiomodel.load()
    else:
        # textmodel.train(dbd.batch_generator(32, subset='train'))
        audiomodel.train(
            dbd.batch_generator(32,
                subset='train',
                audio_parameters=(2048, 2048, 4)
            ), 1000
        )

    # textmodel.save()
    audiomodel.save()

    # Test

    if test:
        # textmodel.eval(dbd.batch_generator(32, subset='test'))
        audiomodel.eval(dbd.batch_generator(32, subset='test'))
