import pandas as pd
import numpy as np
from sklearn.metrics import roc_curve

def net_gain_curve(y_true, y_score, tp_gain, fp_cost, tn_gain=0., fn_cost=0., p_1=None):

    """Calculate net gain curve of a classifier for each possible threshold, 
    given a gain-cost matrix associated with each element of the confusion matrix.
    
    Parameters
    ----------
    y_true : list or array of binary (1/0)
        Real value of the target variable for each data point 
    y_score : list or array of float, shape (,len(y_true))
        Score assigned by the classifier to each data point (higher scores mean higher confidence 
        in target variable being 1)
    tp_gain: float
        Profit or gain from correctly prediciting that a positive data point is positive.
        It must be > 0.
    fp_cost: float
        Loss from incorrectly predicting that a negative data point is positive.
        It must be > 0. 
    tn_gain: float, optional (default = 0.)
        Profit or gain from correctly prediciting that a negative data point is negative.
        It must be > 0.
    fn_cost: float, optional (default = 0.)
        Loss from incorrectly predicting that a positive data point is negative.
        It must be > 0. 
    p_1: float, optional (default = None)
        Prior for class 1 (positive class). If None, the function calculates it
        from y_true. 
        It must be between 0 and 1.
            
    Returns
    -------
    expected_net_gain_series : Series, shape (,len(fpr))
        Series containing the net gain expected by using the classifier 
        as a function of the classifier's cut-off (Series' index is the proportion 
        of the total population classified as positive)
    optimal_threshold : float (range: 0-1)
        Proportion of the total population classified as positive that yields
        the highest net gain
    """
    
    # calculate false and true positive rates for each threshold in the classifier
    fpr,tpr, _ = roc_curve(y_true,y_score)
    # derive true and false negative rates from false and true positive rates,
    # to get the complete confusion matrix at each threshold
    tnr = 1. - fpr
    fnr = 1. - tpr
    
    # if the prior for class 1 was not provided, calculate it from the test data
    if p_1 is None:
        p_1 = np.mean(y_true)

    # use the complete confusion matrix to calculate expected net gain at
    # each threshold  
    net_gain = p_1*(tpr*tp_gain - fnr*fn_cost) + \
              (1. - p_1)*(tnr*tn_gain - fpr*fp_cost)
    # calculate percentage of total population that is classified as positive 
    # for each value of the threshold (to be used as index in the Pandas Series)
    tot_predicted_positives = (1 - p_1)*fpr + p_1*tpr

    expected_net_gain_series = pd.Series(net_gain,index=tot_predicted_positives)
    optimal_threshold = expected_net_gain_series.idxmax()

    return [expected_net_gain_series, optimal_threshold]