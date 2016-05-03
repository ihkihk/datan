#!/usr/bin/python

import sys
import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time

from sklearn.pipeline import Pipeline
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import NearestNeighbors
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import f_classif, SelectKBest
from sklearn.preprocessing import StandardScaler, Imputer, MinMaxScaler, PolynomialFeatures
from sklearn.decomposition import PCA, KernelPCA
from sklearn.grid_search import GridSearchCV
from sklearn.cross_validation import cross_val_score, StratifiedKFold, StratifiedShuffleSplit
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_curve, auc

sys.path.append("./tools/")


from feature_format import featureFormat, targetFeatureSplit
from tester import dump_classifier_and_data

### Task 1: Select what features you'll use.
### features_list is a list of strings, each of which is a feature name.
### The first feature must be "poi".
features_list = ['poi',
        'salary',
        'to_messages',
        'deferral_payments',
        'total_payments',
        'exercised_stock_options',
        'bonus',
        'restricted_stock',
        'shared_receipt_with_poi',
        'restricted_stock_deferred',
        'total_stock_value',
        'expenses',
        'from_messages',
        'other',
        'from_this_person_to_poi',
        'deferred_income',
        'long_term_incentive',
        'from_poi_to_this_person'] # You will need to use more features

### Load the dictionary containing the dataset
with open("final_project_dataset.pkl", "r") as data_file:
    data_dict = pickle.load(data_file)

record_names = data_dict.keys()
print "Number of records: ", len(record_names)
features = data_dict[record_names[0]].keys()
print "Number of features in each record: ", len(features)

# Convert to pandas
data_df = pd.DataFrame.from_dict(data_dict, orient='index', dtype=np.float)

### Task 2: Remove outliers
print "Removing outliers"
df_cleaned = data_df.drop(['TOTAL', 'LOCKHART EUGENE E'])

# Remove unwanted features
print "Removing unwanted features"
del(df_cleaned['email_address'])
del(df_cleaned['loan_advances'])
del(df_cleaned['director_fees'])



### Task 3: Create new feature(s)
### Store to my_dataset for easy export below.
print "Creating new features: total_gains, from_poi_messages_ration, shared_poi_messages_ratio"
df_cleaned['total_gains'] = df_cleaned['total_stock_value'] + df_cleaned['total_payments']
df_cleaned['from_poi_messages_ratio'] = df_cleaned['from_poi_to_this_person'] / df_cleaned['to_messages']
df_cleaned['shared_poi_messages_ratio'] = df_cleaned['shared_receipt_with_poi'] / df_cleaned['to_messages']

features_list.extend(['total_gains', 'from_poi_messages_ratio', 'shared_poi_messages_ratio'])

### Impute missing values
print "Imputing missing values"
df_cleaned = df_cleaned.fillna(df_cleaned.median())

my_dataset = df_cleaned.to_dict('index')

### Extract features and labels from dataset for local testing
data = featureFormat(my_dataset, features_list, sort_keys = True)
labels, features = targetFeatureSplit(data)

### Imputing missing values
#imputer = Imputer(strategy='median')
#features = imputer.fit_transform(features)

### Task 4: Try a varity of classifiers
### Please name your classifier clf for easy export below.
### Note that if you want to do PCA or other multi-stage operations,
### you'll need to use Pipelines. For more info:
### http://scikit-learn.org/stable/modules/pipeline.html

# Provided to give you a starting point. Try a variety of classifiers.

### Task 5: Tune your classifier to achieve better than .3 precision and recall
### using our testing script. Check the tester.py script in the final project
### folder for details on the evaluation method, especially the test_classifier
### function. Because of the small size of the dataset, the script uses
### stratified shuffle split cross validation. For more info:
### http://scikit-learn.org/stable/modules/generated/sklearn.cross_validation.StratifiedShuffleSplit.html

# Example starting point. Try investigating other evaluation techniques!
#from sklearn.cross_validation import train_test_split
#features_train, features_test, labels_train, labels_test = \
#    train_test_split(features, labels, test_size=0.3, random_state=42)

def print_clf_scores(clf, X, y, n_iter=1000):
    ccv = StratifiedShuffleSplit(y, n_iter=n_iter, random_state=42)
    print "Recall:    ", cross_val_score(clf, X, y, cv=ccv, scoring='recall').mean()
    print "Precision: ", cross_val_score(clf, X, y, cv=ccv, scoring='precision').mean()
    print "F1 score:  ", cross_val_score(clf, X, y, cv=ccv, scoring='f1').mean()
    print "Accuracy:  ", cross_val_score(clf, X, y, cv=ccv, scoring='accuracy').mean()
    print "ROC_AUC:   ", cross_val_score(clf, X, y, cv=ccv, scoring='roc_auc').mean()

def get_logreg_model():
    n_jobs = 1 # Set to -1 to use all CPU
    scoring = 'recall' # Better adapted to unbalanced feature classes

    print "Logistic Regression"
    print "==================="

    clf = Pipeline([#('poly', PolynomialFeatures(interaction_only=True)),
                    ('kbest', SelectKBest()), 
                    ('scaler', MinMaxScaler()), 
                    ('pca', PCA()), 
                    ('logreg', LogisticRegression(penalty='l2', class_weight='balanced', 
                                              solver='liblinear', random_state=123))])

    poly_degree = [1, 2]
    n_components = [2, 3, 4, 5, 6, 7]
    Cs = np.logspace(-4, 2, 4)
    k = [12, 14, 16, 18, 'all']

    print "Starting training..."
    cv = StratifiedShuffleSplit(labels, n_iter=50, random_state=42)
    grid_search = GridSearchCV(clf, dict(#poly__degree=poly_degree, 
                                         pca__n_components=n_components, 
                                         kbest__k=k, logreg__C=Cs), 
                               cv=cv, error_score=0, scoring=scoring, n_jobs=n_jobs)
    grid_search.fit(features, labels)
    print "Training finished"

    print "Best score achieved by GridSearch: ", grid_search.best_score_
    best_k = grid_search.best_params_['kbest__k']
    if best_k == 'all':
            best_k = len(features[0])
    print "\tKBest k: ", best_k
    print "\tPCA n_components: ", grid_search.best_params_['pca__n_components']
    print "\tLogReg C: ", grid_search.best_params_['logreg__C']

    clf = grid_search.best_estimator_

    print_clf_scores(clf, features, labels)

    return clf

def get_randforest_model():
    n_jobs = -1 # Set to -1 to use all CPU
    scoring = 'recall' # Better adapted to unbalanced feature classes

    clf = Pipeline([#('poly', PolynomialFeatures(include_bias=False, interaction_only=True)),
                    ('kbest', SelectKBest()), 
                    ('scaler', MinMaxScaler()), 
                    ('pca', PCA()), 
                    ('rf', RandomForestClassifier(n_estimators=10, n_jobs=n_jobs, 
                            random_state=123, class_weight='balanced'))])
    poly_degree = [1, 2]
    n_components = [2, 3, 4]
    min_samples_split = [1, 2, 3, 4]
    min_samples_leaf = [2, 3, 4]
    k = [16, 18, 20]
    
    cv = StratifiedShuffleSplit(labels, n_iter=10, random_state=42)
    grid_search = GridSearchCV(clf, dict(#poly__degree=poly_degree, 
                                         pca__n_components=n_components, 
                                         kbest__k=k, 
                                         rf__min_samples_split=min_samples_split,
                                         rf__min_samples_leaf=min_samples_leaf), 
                               cv=cv, error_score=0, scoring=scoring, n_jobs=n_jobs)
    grid_search.fit(features, labels)
    
    print "Best score achieved by GridSearch: ", grid_search.best_score_
    print "Best parameters found by GridSearch:"
    print "\tPolyFeatures degree: ", grid_search.best_params_['poly__degree']
    print "\tKBest k: ", grid_search.best_params_['kbest__k']
    print "\tPCA n_components: ", grid_search.best_params_['pca__n_components']
    print "\tRandomForest min_samples_split: ", grid_search.best_params_['rf__min_samples_split']
    print "\tRandomForest min_samples_leaf:  ", grid_search.best_params_['rf__min_samples_leaf']

    return grid_search.best_estimator_

def get_svc_model():
    n_jobs = -1 # Set to -1 to use all CPU
    scoring = 'recall' # Better adapted to unbalanced feature classes

    clf = Pipeline([('poly', PolynomialFeatures(include_bias=False, interaction_only=True)),
                    ('kbest', SelectKBest()), 
                    ('scaler', StandardScaler()), 
                    ('pca', PCA()), 
                    ('svc', SVC(kernel='rbf', random_state=123, class_weight='balanced'))])

    poly_degree = [1, 2]
    n_components = [2, 3, 4]
    Cs = [0.01, 0.1, 1, 10]
    gamma = ['auto']
    k = [6, 8, 10, 12, 14, 16]

    cv = StratifiedShuffleSplit(labels, n_iter=30, random_state=42)
    grid_search = GridSearchCV(clf, dict(poly__degree=poly_degree, 
                                        pca__n_components=n_components, 
                                        kbest__k=k, 
                                        svc__gamma=gamma,
                                        svc__C=Cs), 
                               cv=cv, error_score=0, scoring=scoring, n_jobs=n_jobs)
    grid_search.fit(features, labels)
    
    print "Best parameters found by GridSearch:"
    print "\tPolyFeatures degree: ", grid_search.best_params_['poly__degree']
    print "\tKBest k: ", grid_search.best_params_['kbest__k']
    print "\tPCA n_components: ", grid_search.best_params_['pca__n_components']
    print "\tSVC gamma: ", grid_search.best_params_['svc__gamma']
    print "\tSVC C: ", grid_search.best_params_['svc__C']
    
    return grid_search.best_estimator_

t = time.time()
clf = get_logreg_model()
#clf = get_randforest_model()
#clf = get_svc_model()
print "Elapsed training time [s]: ", time.time()-t 

### Task 6: Dump your classifier, dataset, and features_list so anyone can
### check your results. You do not need to change anything below, but make sure
### that the version of poi_id.py that you submit can be run on its own and
### generates the necessary .pkl files for validating your results.

dump_classifier_and_data(clf, my_dataset, features_list)

