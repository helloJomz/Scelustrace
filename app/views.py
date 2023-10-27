from django.shortcuts import render, redirect
from django.views import View
from django.http import JsonResponse
from django.contrib import auth
from django.contrib.sessions.models import Session
from joblib import load
from sklearn.metrics import classification_report
import pandas as pd
import os
from sklearn.naive_bayes import MultinomialNB
from imblearn.over_sampling import SMOTE


# Create your views here.
class ClassificationView(View):
    def get(self, request):
        return render(request, 'app/classification.html')

    def post(self, request):

        # imports model and features
        tfidf_vectorizer    = load('./scelustrace/static/models/tfidf-vectorizer.joblib')
        nb_classifier       = load('./scelustrace/static/models/naive-bayes.joblib')
        label_encoder       = load('./scelustrace/static/models/label-encoder.joblib')

        content             = request.POST["input_content"]
        input_tfidf         = tfidf_vectorizer.transform([content])
        y_pred              = nb_classifier.predict(input_tfidf)
        y_pred_label        = label_encoder.inverse_transform(y_pred)
        predicted_label     = y_pred_label[0] if y_pred_label else ''

        result = {}  # Default assignment

        if predicted_label == 'Cybercrime':
            result = {
                'predicted_label': 'Cybercrime',
                'bg_color': '#1434A4',
                'desc': 'Refers to an illegal activity committed through the use of computers, mobile phones, or any other device that can be used by means of technology. Some of its various forms are identity theft, hacking websites or networks, spreading fake news, video pornography, infringing copyright, selling illegal items, online scamming, and phishing, in which fraudulent email messages or SMS are used to steal personal information.',
            }
        elif predicted_label == 'Property Crime':
            result = {
                'predicted_label': 'Property Crime',
                'bg_color': '#93C572',
                'desc': 'Pertains to offenses related to property damage, theft, or destruction, such as shoplifting, theft, arson, property damage, and illegal possession of firearms which can result in imprisonment and fines.',
            }
        elif predicted_label == 'Morality Crime':
            result = {
                'predicted_label': 'Morality Crime',
                'bg_color': '#800080',
                'desc': 'Includes violations of accepted social and moral values rather than harm to individuals or property, encompassing crimes like prostitution, bigamy, illegal gambling, illegal drug use, and indecent exposure.',
            }
        elif predicted_label == 'Statutory Crime':
            result = {
                'predicted_label': 'Statutory Crime',
                'bg_color': '#FFC000',
                'desc': 'Refers to acts prohibited for the betterment and protection of society, including driving under the influence (DUI), drug possession, sale or distribution, public intoxication, selling alcohol to minors, driving without a license, reckless driving, hit and run, illegal importation of goods, and illegal parking.'
            }
        elif predicted_label == 'Financial/White Collar Crime':
            result = {
                'predicted_label': 'Financial/White Collar Crime',
                'bg_color': '#FFF5EE',
                'desc': 'Are financially motivated offenses, often occurring in the business world, which, while nonviolent, can inflict substantial financial losses on individuals and businesses. Examples include embezzlement, forgery, fraud, tax evasion, identity theft, public corruption, healthcare fraud, and election law violations.'
            }
        elif predicted_label == 'Violent Crime':
            result = {
                'predicted_label': 'Violent Crime',
                'bg_color': '#DC2626',
                'desc': 'Encompasses actions causing physical harm or emotional distress to individuals, including assault, battery, robbery, child abuse, kidnapping, sexual assault, manslaughter, murder, and violation of safety measures.'
            }

        return JsonResponse(result)


def logout_and_clear_sessions(request):
    auth.logout(request)  # Logout the user
    request.session.flush()  # Clear all sessions
    return redirect('/login')


