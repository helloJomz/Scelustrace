from django.shortcuts import render, redirect
from django.views import View
from django.http import JsonResponse
from django.contrib import auth
from .models import ListOfCrimes
from joblib import load
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import io
import matplotlib.pyplot as plt
import base64

class ClassificationView(LoginRequiredMixin, View):
    def get(self, request):
        list_of_crimes = ListOfCrimes.objects.all()
        
        return render(request, 'app/classification.html', context={'data':list_of_crimes})

    def post(self, request):

        # imports model and features
        tfidf_vectorizer    = load('./static/models/tfidf-vectorizer.joblib')
        nb_classifier       = load('./static/models/naive-bayes.joblib')
        label_encoder       = load('./static/models/label-encoder.joblib')

        content             = request.POST["input_content"]
        input_tfidf         = tfidf_vectorizer.transform([content])
        y_pred              = nb_classifier.predict(input_tfidf)
        y_pred_label        = label_encoder.inverse_transform(y_pred)
        predicted_label     = y_pred_label[0] if y_pred_label else ''

        result = {}  
        list_of_crimes = ListOfCrimes.objects.all()

        for crime in list_of_crimes:
            if crime.label_crime == predicted_label:
                result = {
                    'predicted_label': crime.label_crime,
                    'bg_color': crime.bg_color,
                    'desc': crime.desc
                }
        return JsonResponse(result)
    


class ClusteringView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'app/clustering.html')
    
    def post(self, request):
        cluster_info = [] #list to store the cluster words
        dataset_info = {} #dict to store the dataset info
        chart_image = None
        wordcloud_images = []  #list to store Word Cloud images 

        if request.method == 'POST':
            csv_file = request.FILES['csv_file']
            data = pd.read_csv(csv_file)
            content_data = data['content']
            vectorizer = TfidfVectorizer(stop_words='english')
            X = vectorizer.fit_transform(content_data)

            k = int(request.POST.get('input_k', 0))
            if k > 0:
                model = KMeans(n_clusters=k, init='k-means++', max_iter=300, n_init=1, random_state=462)
                model.fit(X)

                data['cluster'] = model.labels_

                #loop for cluster result w/ 30 feature words
                for i in range(k):
                    order_centroids = model.cluster_centers_.argsort()[:, ::-1]
                    terms = vectorizer.get_feature_names_out()
                    cluster_words = [terms[j] for j in order_centroids[i, :30]]
                    cluster_info.append((f'Cluster {i}', cluster_words))

                    # wordcloud result
                    wordcloud = WordCloud(width=400, height=400, background_color='white')
                    wordcloud.generate_from_text(' '.join(cluster_words))

                    # save the word cloud as a base64-encoded image
                    image_data = io.BytesIO()
                    wordcloud.to_image().save(image_data, format="PNG")
                    image_base64 = base64.b64encode(image_data.getvalue()).decode('utf-8')
                    wordcloud_images.append((f'Cluster {i}', image_base64))

                # create and save the bar chart of cluster points
                plt.bar([x for x in range(k)], data.groupby(['cluster'])['content'].count(), alpha=0.4)
                plt.title('KMeans cluster points')
                plt.xlabel("Cluster number")
                plt.ylabel("Number of points")

                # save the chart as a bytes-like object
                chart_buffer = io.BytesIO()
                plt.savefig(chart_buffer, format="png")
                plt.close()

                # convert the chart to base64 and encode it as a string
                chart_image = base64.b64encode(chart_buffer.getvalue()).decode('utf-8')

            # store dataset information
            dataset_info['dataset_name'] = csv_file.name
            dataset_info['row_count'] = len(data)
            dataset_info['column_names'] = data.columns.tolist()

        return render(request, 'kmeans.html', {'cluster_info': cluster_info, 'dataset_info': dataset_info, 'chart_image': chart_image, 'wordcloud_images': wordcloud_images})




















@login_required
def logout_and_clear_sessions(request):
    auth.logout(request)  # Logout the user
    request.session.flush()  # Clear all sessions
    return redirect('/login')


