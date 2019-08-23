# Starter for deploying f2s model on [Render](https://render.com)

Semantic Segmentation Platform on Forest Wildfire

Proposed Forest Fire to Semantic Segmentation (F2S) Platform is a cloud artificial intelligence solution for high-volume satellite data in forest wildfire detection. F2S shall provide easy to use high resolution burnt area calculations and visualizations to professionals within forestry and insurance. The current F2S functional prototype is based on optical satellite data, but a model for radar-based satellite data is being developed.

Available technologies in forest wildfire detection include aircrafts, cameras, satellites and drones. Different platforms have different image formats based on the different wavelengths, which vice versa makes the universal cloud processing difficult, not to mention the multi-source fusion.
 
F2S would provide a rapid response platform for uploading ROI image and then analyzing the input source to get final burnt area information.

Step1: we apply Google Earth Engine Python API to generate the train images and labels.  After confirming the region of interest, we could get the available Sentinel-2 images in a specific day during the fire or after the fire. Through the batch-downloading algorithm developed by us, it becomes every easy to generate the Geotiff or PNG format images including any bands we want. About the labels, we use the delta normalized burnt ratio to threshold the burnt area and then constrain it  within the released  official burnt region by authorities. Usually, the large wildfire would make the Sentinel-2 image huge volume. To speed the train process, we clip the ROI which contains burnt and unburnt into 300*300 pixels. The pixel resolution is 20 meters same with Sentinel-2. 

Step2: The fastai library simplifies training fast and accurate neural nets using modern best practices.  We download the pre-trained resnet18 model and then apply the dynamic Unet architecture to train the semantic segmentation. Finally we could export the model as pkl file and then it will be uploaded into Google Drive. Since it is bigger than 100 Megabytes. We also need the google cloud platform to help generate downloaded link. 

Step 3 is to customize the web app based on GitHub Starter specific for fastai model. And then the app will be connected with the Deployment tool Render web service which will watch the updates in GitHub.

All the processing is finished in cloud platform. ESDL cloud server supports the computation of Step 1 and 2. Cloud Web Service and GitHub makes the web deployment successful. 

* The model could be downloaded in server.py
* test images could be downloaded in Test_images folder
* GEE download algorithm can be found in the repostory (GEE_batch_download)

