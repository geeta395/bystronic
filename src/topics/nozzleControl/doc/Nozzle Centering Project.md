**Goal** : To find nozzle attributes (radius and center), given nozzle image datasets.

**Sample dataset: (synthetic + real)**

![](sample%20Images/syn.jpg)

![](sample%20Images/real.jpg)

Synthetic data: 

For synthetic data , we generated plan circular images and added noise  and random cutouts.

**Overall Layout:** 

![](sample%20Images/layOut.png)

**Steps:**

**Part1:** Generate synthetic images and apply augmentation (noise and cutout) on the synthetic data. Prepare the model with different heads as shown in the figure and save weights for every head. We are using ensemble transfer learning for this . The idea is to fix the body of the model (convolutional block) and creating several heads to finally ensemble all the predictions using weighted average method where weights are proportionate to the loss function value for each head. 

**Part2:**

1) Get real data from Azure.

2) Process data: This includes exposure fusion, resizing and data labelling using label studio.

3) Augment data: This includes apply different filters to real images, we used random combinations of flipping,rotation,zoom ,shift and random cutout.

4) Transfer the weights from synthetic data model, optimize and train it for real dataset.  

5) Save model with all heads for inference.

**Data Preprocessing:**

![](sample%20Images/DP.png)

For data preprocessing, we focused mainly on exposure fusion and resizing. Every zip file include three images of the nozzle with different exposure settings. As an input to the model, we fuse these three images together to make one which is well exposed and we used exposure fusion technique for that. After getting fused images we did the labeling part using label studio. 

**Data Augmentation**

![](sample%20Images/DA.png)

After preprocessing, we now have fused images with their respective labels. We apply data augmentation on fused images to make the model robust. For it, we randomly select filters from horizontal and vertical flip, rotation with angle 5 degrees, random cutouts , zooming and shifting. So we build a generator in the pipeline, which randomly generate different filter combinations  for each image and augment data.

**Model** 

![](sample%20Images/model.png)

We use two fold model for this. The first fold is the body of the model which consist of convolutional layers and max pooling layers and the second fold is called head. In the first phase we train the complete model on the dataset and tune it to get maximum possible accuracy. In second phase, we freeze the body of the model and only train the head. Since head consist of dense layers with random dropout layers so every time we train the head we encounter different weights with slightly different output values. Finally, we ensemble the predictions using weighted average method, where weights are proportionate to the loss value for each head. Lastly, models with different heads are saved for the inference.

**Inference** 

![](sample%20Images/Inf.png)  

At the time of the inference, we get the zip file  from machine via mqtt broker. Once the data is transferred, we read the three images from the zip, preprocess it with fusion and resizing. Then we load all the models and get their predictions separately and finally ensemble them using the saved loss values as weights. 

**Results so far:**

Best results:

![](sample%20Images/best.jpg)

Worst Results:

![](sample%20Images/worst.jpg)



**First training without ensemble: (For noisy images)**

![](sample%20Images/accurcy.png) 

**First training without ensemble: (images without noise)**

![](sample%20Images/accurcy1.png)

**Conclusion:**

Adding noisy to the images hurts accuracy of the model a lot.

**For noisy data, final training with ensemble:**

We used four heads to get the predictions. If the prediction falls under allowedPixel limit (i.e. error of 5 pixels) then we score that prediction 1 else 0. Finally average is taken over that score.  When score is 0 all heads predicted it wrong, when score is 0.25 1 head predict it right and 3 predicted it wrong, similarly when score is 1 all heads predicted it right. For final prediction we take weighted average of head predictions where weights are proportionate to the loss function value for each head. 

![](sample%20Images/confidenceScore.png)

**Final accuracy after ensemble, with noisy images:**

![accurcyEn](sample%20Images/accurcyEn.png)

Accuracy increases from 73% to 84%, using ensemble method.

**Final Training with cut-out but without noise (Ensemble)**

![accurcyEn](sample%20Images/accurcyEnCut.png)

![](sample%20Images/confidenceScoreCut.png)

**Visualization of prediction over individual image:**

![](sample%20Images/predictedRadius.png)

Green dots represent the predictions from different heads, red represents true label and yellow represents the ensemble prediction. Two blue line indicates permissible limits of the correct prediction.