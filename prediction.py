import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder
from sklearn import tree
from sklearn.decomposition import PCA
import pickle


df = pd.read_excel('C:\\Users\\LENOVO L460\\Downloads\\ipbl\\datasets\\dgclean.xlsx')

X = df.drop(['Schimers1Lefteye_1', 'Schimers1righteye_1', 'Schimers2Lefteye_1', 'Schimers2righteye_1','onlineplatforms',
            'onlineplatforms', 'Sex', 'Distancekeptbetweeneyesandgadjet', 'levelofgadjetwithrespecttoeyes', 'Duration', 
             'Difficultyinfocusingafterusingscreens', 'frequencyofdryeyes','screenillumination'], axis=1)


y1 = df['Schimers1Lefteye_1'] 
y2 = df['Schimers1righteye_1'] 
y3 = df['Schimers2Lefteye_1'] 
y4 = df['Schimers2righteye_1'] 





X_train1, X_test1, y_train1, y_test1 = train_test_split(X, y1, test_size=0.2, random_state=42)
X_train2, X_test2, y_train2, y_test2= train_test_split(X, y2, test_size=0.2, random_state=42)
X_train3, X_test3, y_train3, y_test3 = train_test_split(X, y3, test_size=0.2, random_state=42)
X_train4, X_test4, y_train4, y_test4 = train_test_split(X, y4, test_size=0.2, random_state=42)


clf1 = DecisionTreeClassifier(random_state=42)
clf2 = DecisionTreeClassifier(random_state=42)
clf3 = DecisionTreeClassifier(random_state=42)
clf4 = DecisionTreeClassifier(random_state=42)


clf1.fit(X_train1, y_train1)
clf2.fit(X_train2, y_train2)
clf3.fit(X_train3, y_train3)
clf4.fit(X_train4, y_train4)

y_pred1 = clf1.predict(X_test1)
y_pred2 = clf2.predict(X_test2)
y_pred3 = clf3.predict(X_test3)
y_pred4 = clf4.predict(X_test4)

accuracy1 = accuracy_score(y_test1, y_pred1)
accuracy2 = accuracy_score(y_test2, y_pred2)
accuracy3 = accuracy_score(y_test3, y_pred3)
accuracy4 = accuracy_score(y_test4, y_pred4)

classifiers = {
    'Schimers1Lefteye': clf1,
    'Schimers1righteye': clf2,
    'Schimers2Lefteye': clf3,
    'Schimers2righteye': clf4
}


filename = 'Eyemodel.pkl'
with open(filename, 'wb') as f:
    pickle.dump(classifiers, f)



