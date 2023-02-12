# Confidence for the predicted results

Goal : The goal of this study is to find some confidence in the predictions made during the Inference phase of the whole process.

#### Inference Phase:

![](sample%20Images/Inf.png)

#### Data Formatting

At the time of inference, we receive dump file (zip file) via mqtt broker. Once the data is transferred to the edge, images are read from the dump file. Each dump file contains three images from three different exposure settings. At the time of data preprocessing, theses three images are fused to a single image using exposure fusion algorithm followed by resizing the image and converting it to a tensor. Once the input is formatted, all the models are loaded. 

​     

#### Model Loading

 ![](sample%20Images/model.png)

The model used for this project is an ensemble model. The basic structure of the model is divided into two parts-body and head. The body of the model comprises of convolutional block which further consist of four sub-blocks of convolutional layers , activation function (ReLU) and Max pooling layer. Once trained, this part is kept fixed for the whole process. The head is consist of four dense layers and three dropout layers. There are multiple heads in the process and during training all the heads are trained one after another with the fixed body weights.

So, at the inference time we load all this different sub-models (body+head) and get prediction from each head. For example, for 10 sub-models we have 10 predictions (radius, x_coordinate, y_coordinate). Final prediction is the weighted average of all these predictions where weights are the loss score saved from training phase. 

For the confidence of this ensembled prediction, the variation in the set of all the predictions made by different heads is checked. For this mean, median and mode of this set is calculated and from the observation made by different experiments, we conclude that if mean, median and mode are close enough( difference between maximum and minimum of three should be less than 5 pixels) to each other than it is a good prediction else the prediction is not trust worthy.

This observation is build upon the idea of the normal distribution. 

![](sample%20Images/dis.png)

  If Mean=Mode=Median, this represents the normal distribution and best one for our process. Else the distribution is skewed and prediction might be random from all the heads. 

![](sample%20Images/algo.png)

So, at the time of inference, along with the ensemble prediction we get indication factor of the prediction which tells us if this should be trusted or not. 

Experiments for this study is coded in the file ***\topics\nozzleControl\training\main\testScore.py** 