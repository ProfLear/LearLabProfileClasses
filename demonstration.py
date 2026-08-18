'''
This is a demonstration of the class-based profilometry analyzer.

There are 3 basic classes that comprise how this works:
    - the "Sample" class is the parent class
    - the "ArealData" class contains a 2D array, and all relevant information about that (roughness, etc.)
    - the "ArealProcess" class contains information on how the 2D array in an ArealData class was processed. 
    
There should only ever be 1 parent "Sample" class for each sample.
The sample class is created when you load in raw data from the instrument.
It comes with an "ArealData" instance, named "raw".
The "ArealData" class has methods for operating on the data, and will create an instance of the "ArealProcess" within the "ArealData"
Then you can use the "ArealProcess" and "ArealData" classes as verb-noun constructions 
to keep track of how you have processed the data.

For example: 
namedSample.raw.fitRectbiSpline(name = "first_spline")
will create a new "ArealProcess" within the "raw" "ArealData" instance. You can access the result using:
namedSample.raw.first_spline.result

This "result" object is again an "ArealData" object that can be operated on.

Basic usage is as follows:
    1. You create an instance of the "Sample" class.  
        This is the outermost container. It contains information such as:
            - date
            - instrument metadata
            - raw 2D array <-- this is an instance of the "ArealData" class 
    2. The ArealData class primarily holds 2D arrays, and has methods for operating on them.
        Operations result in the creation of an instance of the "ArealProcess" class.
    3. The ArealProcess class contains:
        - details of the process
        - the result of the operation (smoothed / fitted ArealData)
        - the residual of the operation (roughness / high frequency ArealData)
        - information on the parent (ArealData)
'''

#%%
import numpy as np
import learlab_profile_classes as pc

#%%
testData = "../testdata/082924_04_2.75x_1x_100_02.xyz"
# testData = "/Users/benjaminlear/Downloads/260728_PDMS-CB_A_I0.3_S7_P7_HDR.xyz"

#%% 1 Create a sample object from data
testSample = pc.makeSample(file=testData, instrument="zygos")

#%% 2 Plot what the raw data looks like (automatically downsampled if > 1MB for notebook)
testSample.raw.plot()

#%% 3 Get roughness
testSample.raw.getArealRoughness()

#%% 4 Decompose into spline and residual
testSample.raw.fitRectbiSpline(name="first_spline", s_scale=1.0)
testSample.raw.first_spline.plot()

#%% 5 Inspect processing pipeline
testSample.raw.first_spline.result.pipeline()


