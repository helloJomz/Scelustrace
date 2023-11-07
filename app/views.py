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
from concurrent.futures import ThreadPoolExecutor
from django.views.decorators.csrf import csrf_exempt


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
    


def create_circle_marker(latVal, longVal, color):
    return folium.Circle(
        location=[latVal, longVal],
        radius=1000,
        color=color,
        weight=2,
        fill=True,
        opacity=0.05
)


@csrf_exempt
def load_bubble(request):
    df = pd.read_csv('./static/csv/gmanews.csv')

    # Filter out rows with missing latitude or longitude
    df = df.dropna(subset=['latitude', 'longitude'])
    
    # Create a Folium map
    mapObj = folium.Map(location=[14.6760, 121.0437], zoom_start=12, max_bounds=True, zoomControl=False, tiles='cartodbpositron')

    fig = Figure(height="100%")
    fig.add_child(mapObj)

    # Add a light mode tile layer
    folium.TileLayer('cartodbdark_matter').add_to(mapObj)

    # Create a Feature Group
    circle_fg = folium.FeatureGroup(name="Crime Bubble", show=True).add_to(mapObj)

    # Create a MarkerCluster
    circle_cluster = MarkerCluster(name='Circle').add_to(circle_fg)

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

    
    # Color list for crime_types
    crime_type_colors = {
        1: "red",    # Violent Crime
        2: "violet", # Property Crime
        3: "green",  # Morality Crime
        4: "blue",   # Statutory Crime
        5: "orange", # Financial/White Collar Crime
        6: "pink"    # Cybercrime
    }

    num_workers = 4  # Adjust this value based on your system's capabilities

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        circle_markers = list(executor.map(
            create_circle_marker,
            df['latitude'],
            df['longitude'],
            df['crime_numeric'].map(crime_type_colors)
        ))

    for circle_marker in circle_markers:
        circle_marker.add_to(circle_cluster)

    folium.LayerControl(position="topright", collapsed=False).add_to(mapObj)

    context = {'map': mapObj._repr_html_()}
    
    return JsonResponse(context)

@csrf_exempt
def load_heatmap(request):
    df = pd.read_csv('./static/csv/gmanews.csv')

    # Filter out rows with missing latitude or longitude
    df = df.dropna(subset=['latitude', 'longitude'])
    
    # Create a Folium map
    mapObj = folium.Map(location=[14.6760, 121.0437], zoom_start=12, max_bounds=True, zoomControl=False, tiles='cartodbpositron')

    fig = Figure(height="100%")
    fig.add_child(mapObj)

    # Add a light mode tile layer
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

    # Group by latitude and longitude and calculate the total number of crimes
    heatmap_data = df.groupby(['latitude', 'longitude'])['crime_numeric'].sum().reset_index()

    # Create a heatmap using the total number of crimes
    heat_data = [[row['latitude'], row['longitude'], row['crime_numeric']] for index, row in heatmap_data.iterrows()]

    # Add the heatmap layer with the 'overlay' parameter set to True
    heatmap_layer = HeatMap(heat_data, name='Crime Heatmap').add_to(mapObj)
    heatmap_layer.add_to(mapObj) 

    folium.LayerControl(position="topright", collapsed=False).add_to(mapObj)

    context = {'map': mapObj._repr_html_()}
    
    return JsonResponse(context)


@csrf_exempt
def load_marker(request):
    df = pd.read_csv('./static/csv/gmanews.csv')

    # Filter out rows with missing latitude or longitude
    df = df.dropna(subset=['latitude', 'longitude'])
    
    # Create a Folium map
    mapObj = folium.Map(location=[14.6760, 121.0437], zoom_start=12, max_bounds=True, zoomControl=False, tiles='cartodbpositron')

    fig = Figure(height="100%")
    fig.add_child(mapObj)

    #Feature Group
    marker_fg = folium.FeatureGroup(name="Crime Marker", show=True).add_to(mapObj)

    #Markercluster
    marker_cluster = MarkerCluster(name='Marker').add_to(marker_fg)

    # Add a light mode tile layer
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

    # Color list for crime_types
    crime_type_colors = {
        1: "red",    # Violent Crime
        2: "violet", # Property Crime
        3: "green",  # Morality Crime
        4: "blue",   # Statutory Crime
        5: "orange", # Financial/White Collar Crime
        6: "pink"    # Cybercrime
    }

    def unicode_to_text(x):
        return x.encode('ascii', 'ignore').decode('utf-8')

    # Function to create a marker
    def create_marker(itr):
        latVal          = df.iloc[itr]['latitude']
        longVal         = df.iloc[itr]['longitude']
        imgUrl          = df.iloc[itr]['img_url']
        color           = crime_type_colors[df.iloc[itr]['crime_numeric']]
        crime_type      = df.iloc[itr]['crime']
        title           = df.iloc[itr]['title']
        decoded_title   = unicode_to_text(title)
        content         = df.iloc[itr]['content']
        newsUrl         = df.iloc[itr]['news_url']
        location        = df.iloc[itr]['location']
            
        html_popup = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <script src='https://cdn.tailwindcss.com'></script>
                    <link href='https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap' rel='stylesheet'>
                    <link href='https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600&display=swap' rel='stylesheet'>
                    <link rel='stylesheet' href='https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200' />
                    <link rel='stylesheet' href='./static/css/main.css'>
                    
                </head>
                <body>
                    <div class='mb-2 select-none flex justify-between items-center font-inter'>
                        <span class='bg-{color}-400 py-1 px-2 font-space rounded-lg text-xs text-white font-semibold'>{crime_type}</span>
                        <span class="text-xs text-slate-400" >#{itr}</span>
                    </div>

                    <div class='mb-3'>
                        <span class="w-full font-inter text-sm font-bold" >{decoded_title}</span>
                    </div>

                    <div class='w-[25rem] h-[13rem]'>
                        <div class='w-full h-full flex gap-3'>
                            <img src='{imgUrl}' alt='logo' class='w-1/2 h-full select-none'>
                            <div class='overflow-y-scroll h-full'>
                                <p class='text-xs font-inter'>{content}</p>
                            </div>
                        </div>
                    </div>

                    <div class='flex space-x-2 font-inter my-3' >
                        <p class='m-0 p-0 text-xs'> source: </p>
                        <a class='text-xs truncate underlined text-sky-600' href='{newsUrl}' target='_blank'>{newsUrl}</a>
                    </div>

                    <div class="mt-4 text-xs text-slate-600 ">

                        <p class="text-xs flex items-center ml-3">
                            <span class="material-symbols-outlined text-xl mr-1"> location_on </span> 
                            <span class='mr-2'> Location: </span>
                            <span class='text-sky-600'> {location} </span>
                        </p>

                        <p class="text-xs flex items-center ml-3">
                            <span class="material-symbols-outlined text-xl mr-1"> share_location </span> 
                            <span class='mr-2'> Coordinates: </span>
                            <span class='text-sky-600'> {latVal} </span>,  
                            <span class='text-sky-600'> {longVal} </span>
                        </p>

                    </div>

                </body>
                </html>
            """
        
        popup_iframe = folium.IFrame(width=400, height=400, html=html_popup)

        marker_marker = folium.Marker(
            location=[latVal, longVal],
            icon=folium.Icon(
                color=color,
                icon="handcuffs",
                prefix="fa",  # To specify the icon library (e.g., Font Awesome)
                icon_color="white",  # Color of the custom icon
            ),
            tooltip=crime_type,
            popup=folium.Popup(popup_iframe),
            icon_size=(40, 40),
        )

        marker_marker.add_to(marker_cluster)

    # Use ThreadPoolExecutor for parallel marker creation
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(create_marker, range(len(df)))

    #Add a Layer Control 
    folium.LayerControl(position="topright", collapsed=False).add_to(mapObj)

    context = {'map': mapObj._repr_html_()}
    
    return JsonResponse(context)




class AnalyticsView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'app/analytics.html')








        
           

        




















@login_required
def logout_and_clear_sessions(request):
    auth.logout(request)  # Logout the user
    request.session.flush()  # Clear all sessions
    cache.clear()
    return redirect('/login')


