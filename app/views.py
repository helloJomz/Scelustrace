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
from io import BytesIO
import base64
from wordcloud import WordCloud
import concurrent.futures

import matplotlib
matplotlib.use('Agg')

import folium
from folium.plugins import HeatMap, MarkerCluster
from branca.element import Figure

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


def create_bar_chart(chart_data):
    plt.bar(chart_data.index, chart_data.values, alpha=0.4)
    plt.title('KMeans cluster points')
    plt.xlabel("Cluster number")
    plt.ylabel("Number of points")

    chart_buffer = BytesIO()
    plt.savefig(chart_buffer, format="png")
    plt.close()

    chart_image = base64.b64encode(chart_buffer.getvalue()).decode('utf-8')
    return chart_image

@login_required
def process_fileupload(request):
    # Delete the first cache
    cache.delete('context_data')
    input_k = request.POST.get('input_k', '')

    if input_k:
        if input_k.isdigit():
            if int(input_k) <= 13:
                cluster_info = []  # List to store the cluster words
                chart_image = None
                wordcloud_images = []  # List to store Word Cloud images

                csv_file = request.FILES['csv_file']
                data = pd.read_csv(csv_file)
                content_data = data['content']
                vectorizer = TfidfVectorizer(stop_words='english')
                X = vectorizer.fit_transform(content_data)


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
                    chart_data = data.groupby(['cluster'])['content'].count()
                    chart_image = create_bar_chart(chart_data)

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

                    return redirect('clustering')
            else:
                return render(request, 'app/fileform.html', {'error': 'The Number of K should not exceed 13!'})
        else:
            return render(request, 'app/fileform.html', {'error': 'The Number of K should be numbers only!'})
    else:
        return render(request, 'app/fileform.html', {'error': 'The Number of K should not be empty!'})

    

class ClusteringView(LoginRequiredMixin, View):
    def get(self, request):
        context = cache.get('context_data')
        return render(request, 'app/clustering.html', context)
    




class AnalyticsView(LoginRequiredMixin, View):
    def get(self, request):

        # Load your data from a CSV file
        df = pd.read_csv('./static/csv/gmanews.csv')

        # Filter out rows with missing latitude or longitude
        df = df.dropna(subset=['latitude', 'longitude'])
        
        # Create a Folium map
        mapObj = folium.Map(location=[14.6760, 121.0437], zoom_start=12, max_bounds=True, zoomControl=False)

        fig = Figure(height="100%")
        fig.add_child(mapObj)

        folium.TileLayer('cartodbdark_matter').add_to(mapObj)

        # Create a GeoJSON layer for Quezon City
        folium.GeoJson(
            data='./static/csv/quezoncity_eastern_manila.geojson',
            name='Q.C. Border',
            style_function=lambda x: {
                "color": "brown",
                "weight": 2,
                "fill": False,
            }
        ).add_to(mapObj)

        circle_fg = folium.FeatureGroup(name="Crime Bubble", show=False).add_to(mapObj)

        # Create a MarkerCluster
        marker_cluster = MarkerCluster(name='Circle').add_to(circle_fg)

        # Color list for crime_types
        crime_type_colors = {
            1: "red",    # Violent Crime
            2: "violet", # Property Crime
            3: "green",  # Morality Crime
            4: "purple", # Statutory Crime
            5: "orange", # Financial/White Collar Crime
            6: "pink"    # Cybercrime
        }

        for itr in range(len(df)):
            latVal = df.iloc[itr]['latitude']
            longVal = df.iloc[itr]['longitude']
            color = crime_type_colors[df.iloc[itr]['crime_numeric']]
            
            marker = folium.Circle(
                location=[latVal, longVal],
                radius=1000,
                color=color,
                weight=2,
                fill=True,
                opacity=0.05
            )

            # Add the marker to the MarkerCluster
            marker.add_to(marker_cluster)

        # Add the MarkerCluster to your map
        marker_cluster.add_to(circle_fg)

        circle_legend = """
        <div id="legend" style="position: fixed; bottom: 50px; left: 50px; width: 150px; background-color: white; border: 2px solid grey; z-index: 9999; font-size: 14px;">
            <p style="margin: 10px; text-align: center;">Legend</p>
            <p style="margin: 10px;">Violent Crime <span style="background-color: red; color: white;">&nbsp;&nbsp;&nbsp;&nbsp;</span></p>
            <p style="margin: 10px;">Property Crime <span style="background-color: violet; color: black;">&nbsp;&nbsp;&nbsp;&nbsp;</span></p>
            <p style="margin: 10px;">Morality Crime <span style="background-color: green; color: white;">&nbsp;&nbsp;&nbsp;&nbsp;</span></p>
            <p style="margin: 10px;">Statutory Crime <span style="background-color: purple; color: white;">&nbsp;&nbsp;&nbsp;&nbsp;</span></p>
            <p style="margin: 10px;">Financial/White Collar Crime <span style="background-color: orange; color: white;">&nbsp;&nbsp;&nbsp;&nbsp;</span></p>
            <p style="margin: 10px;">Cybercrime <span style="background-color: pink; color: white;">&nbsp;&nbsp;&nbsp;&nbsp;</span></p>
        </div>
        """

        # Add the legend to the map
        mapObj.add_child(folium.Element(circle_legend))
        circle_fg.add_to(mapObj)

        # Group by latitude and longitude and calculate the total number of crimes
        heatmap_data = df.groupby(['latitude', 'longitude'])['crime_numeric'].sum().reset_index()

        # Create a heatmap using the total number of crimes
        heat_data = [[row['latitude'], row['longitude'], row['crime_numeric']] for index, row in heatmap_data.iterrows()]

        # Add the heatmap layer with the 'overlay' parameter set to True
        heatmap_layer = HeatMap(heat_data, name='Crime Heatmap').add_to(mapObj)
        heatmap_layer.add_to(mapObj)  

        # Add a Layer Control 
        folium.LayerControl(position="topright", collapsed=False).add_to(mapObj)

        context = {'map': mapObj._repr_html_()}

        return render(request, 'app/analytics.html', context)








        
           

        




















@login_required
def logout_and_clear_sessions(request):
    auth.logout(request)  # Logout the user
    request.session.flush()  # Clear all sessions
    cache.clear()
    return redirect('/login')


