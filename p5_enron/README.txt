(c) Ivailo Kassamakov, May 2016

This is the project folder for the P5 project (Identifying fraud at Enron using ML techniques)

* The main project report is p5_enron.pdf. 
  Its Latex sources are also included in p5_enron-latex_source.zip

* All Python explorations, algorithm training and experiments are in the 
  IPython (Jupyter) notebook p5_enron.ipynb

  WARNING: Running the ipynb takes a long time (30 min) due to the RandomForestClassifier code.

* The final chosen algorithm (LogisticRegression) and its training pipeline and
  associated validation code are imported into poi_id.py as required by the project
  rubric.

* All Python2 development for this project was performed in a virtualenv.
  If needed, the virtualenv can be reproduced by running:
  mkdir py2venv
  virtualenv --python2 py2venv
  source py2venv/bin/activate
  pip install -r py2venv-requirements.txt

>> END <<
