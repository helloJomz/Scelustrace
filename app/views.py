from django.shortcuts import render, redirect
from django.views import View
from django.http import JsonResponse
from django.contrib import auth
from .models import ListOfCrimes
from joblib import load
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.http import HttpResponseRedirect

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import io
import matplotlib.pyplot as plt
import base64
from wordcloud import WordCloud
import concurrent.futures

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
    
@login_required
def load_fileupload(request):
    return render(request, 'app/fileform.html')


def generate_wordcloud(cluster_words, cluster_number):
    wordcloud = WordCloud(width=400, height=400, background_color='white')
    wordcloud.generate_from_text(' '.join(cluster_words))
    image_data = io.BytesIO()
    wordcloud.to_image().save(image_data, format="PNG")
    image_base64 = base64.b64encode(image_data.getvalue()).decode('utf-8')
    return f'Cluster {cluster_number}', image_base64

@login_required
def process_fileupload(request):
    # Check if the context data is cached
    cached_context = cache.get('context_data')
    if cached_context:
        request.session['cache_status'] = True
        return redirect('clustering')

    cluster_info = []  # List to store the cluster words
    chart_image = None
    wordcloud_images = []  # List to store Word Cloud images

    csv_file = request.FILES['csv_file']
    data = pd.read_csv(csv_file)
    content_data = data['content']
    vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform(content_data)

    input_k = request.POST.get('input_k', '')
    k = 0  # Default value

    if input_k and input_k.isdigit():
        k = int(input_k)

    chart_image = None
    wordcloud_images = []

    if k > 0:
        # Check if the clustering model is cached
        cached_model = cache.get('kmeans_model')
        if not cached_model:
            model = KMeans(n_clusters=k, init='k-means++', max_iter=300, n_init=1, random_state=462)
            model.fit(X)
            # Cache the clustering model
            cache.set('kmeans_model', model, None)
        else:
            model = cached_model

        data['cluster'] = model.labels_

        # Loop for cluster result w/ 30 feature words
        for i in range(k):
            order_centroids = model.cluster_centers_.argsort()[:, ::-1]
            terms = vectorizer.get_feature_names_out()
            cluster_words = [terms[j] for j in order_centroids[i, :30]]
            cluster_info.append((f'Cluster {i}', cluster_words))

        # Word cloud generation (parallel processing)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            wordcloud_futures = [executor.submit(generate_wordcloud, cluster_info[i][1], i) for i in range(k)]

        wordcloud_images = [future.result() for future in wordcloud_futures]

        # Create and save the bar chart of cluster points
        plt.bar([x for x in range(k)], data.groupby(['cluster'])['content'].count(), alpha=0.4)
        plt.title('KMeans cluster points')
        plt.xlabel("Cluster number")
        plt.ylabel("Number of points")

        # Save the chart as a bytes-like object
        chart_buffer = io.BytesIO()
        plt.savefig(chart_buffer, format="png")
        plt.close()

        # Convert the chart to base64 and encode it as a string
        chart_image = base64.b64encode(chart_buffer.getvalue()).decode('utf-8')

        context = {
            'cluster_info': cluster_info,
            'chart_image': chart_image,
            'wordcloud_images': wordcloud_images,
            'dataset_name': csv_file.name,
            'col_count': data.shape[1] - 1,
            'row_count': data.shape[0],
        }

        # Cache the context data
        cache.set('context_data', context, None)
        request.session['cache_status'] = True

    return redirect('clustering')
    

class ClusteringView(LoginRequiredMixin, View):
    def get(self, request):
        context = cache.get('context_data', {})
        return render(request, 'app/clustering.html', context)

        
           

        




















@login_required
def logout_and_clear_sessions(request):
    auth.logout(request)  # Logout the user
    request.session.flush()  # Clear all sessions
    cache.delete('context_data')
    return redirect('/login')


