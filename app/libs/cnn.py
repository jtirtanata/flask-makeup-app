import json
from keras.models import model_from_json
user_dim = 14
rating_dim = 843
encoding_dim = int(rating_dim/12)
batch_size = 64
PATH = "app/libs/models/"
def loss_func(y_true, y_pred):
    temp = np.dot(y_true, y_pred)
    temp_true = y_true.nonzero_values()
    temp_pred = temp.nonzero_values()
    temp_pred = temp_pred / temp_true
    loss = T.mean((temp_pred - temp_true)**2)
    return loss
# create the base pre-trained model

def save(model, tags, prefix):
    model.save_weights(prefix+".h5")
    # serialize model to JSON
    model_json = model.to_json()
    with open(prefix+".json", "w") as json_file:
        json_file.write(model_json)
    with open(prefix+"-labels.json", "w") as json_file:
        json.dump(tags, json_file)


def load(prefix):
    prefix = PATH + prefix
    # load json and create model
    with open(prefix+".json") as json_file:
        model_json = json_file.read()
    model = model_from_json(model_json)
    # load weights into new model
    model.load_weights(prefix+".h5")
    with open(prefix+"-labels.json") as json_file:
        tags = json.load(json_file)
    return model, tags
