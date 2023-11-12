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
from cachetools import cached, TTLCache


import matplotlib
matplotlib.use('Agg')

import folium
from folium.plugins import HeatMap, MarkerCluster
from branca.element import Figure

class ClassificationView(LoginRequiredMixin, View):

    def dispatch(self, request, *args, **kwargs):
        # Set the previous page URL in the session
        request.session["prev_page"] = request.path
        return super().dispatch(request, *args, **kwargs)
    
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
    request.session["prev_page"] = request.path
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

    barchart_image = base64.b64encode(chart_buffer.getvalue()).decode('utf-8')
    return barchart_image

@login_required
def process_fileupload(request):
    # Delete the first cache
    cache.delete('context_data')
    input_k = request.POST.get('input_k', '')

    if input_k:
        if input_k.isdigit():
            if int(input_k) <= 13:
                cluster_info = []  # List to store the cluster words
                barchart_image = None
                wordcloud_images = []  # List to store Word Cloud images

                csv_file = request.FILES.get('csv_file', None)

                if not csv_file:
                    return render(request, 'app/fileform.html', {'error': 'File Upload cannot be empty'})
                
                data = pd.read_csv(csv_file)
                content_data = data['content']
                vectorizer = TfidfVectorizer(stop_words='english')
                X = vectorizer.fit_transform(content_data)


                k = 0  # Default value

                if input_k and input_k.isdigit():
                    k = int(input_k)
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
                        barchart_image = create_bar_chart(chart_data)

                        context = {
                            'cluster_info': cluster_info,
                            'barchart_image': barchart_image,
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
    def dispatch(self, request, *args, **kwargs):
        # Set the previous page URL in the session
        request.session["prev_page"] = request.path
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        request.session["prev_page"] = request.path
        cluster = cache.get('context_data')
        if cluster:
            return render(request, 'app/clustering.html', cluster)
        else:
            return render(request, 'app/fileform.html')
    


def create_circle_marker(latVal, longVal, color):
    return folium.Circle(
        location=[latVal, longVal],
        radius=1000,
        color=color,
        weight=2,
        fill=True,
        opacity=0.05
)


def generate_circle_map():
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

    return mapObj._repr_html_()


@login_required
@csrf_exempt
def load_bubble(request):
    # Attempt to retrieve the marker map HTML from the cache
    circle_map_html = cache.get('cached_circle_map')

    if circle_map_html is None:
        # If not found in the cache, generate the circle map HTML
        circle_map_html = generate_circle_map()  # Replace with your circle map generation code

        # Store the generated circle map HTML in the cache with a timeout (e.g., 3600 seconds)
        cache.set('cached_circle_map', circle_map_html, None)

    context = {'map_circle': circle_map_html}

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

    context = {'map': mapObj._repr_html_()}
    
    return JsonResponse(context)







def generate_marker_map():
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
        color           = crime_type_colors[df.iloc[itr]['crime_numeric']]
        crime_type      = df.iloc[itr]['crime']
        title           = df.iloc[itr]['title']
        decoded_title   = unicode_to_text(title)
        location        = df.iloc[itr]['location']
            
        html_popup = f"""
                    <div style="width: 100%; margin-bottom: 1rem; user-select: none; font-family: 'Inter', sans-serif;" >
                        <span style="width: 100%; background-color: {color}; padding-top: 0.25rem; padding-bottom: 0.25rem; padding-left: 0.5rem; padding-right: 0.5rem; letter-spacing: 0.1em; border-radius: 0.5rem; font-size: 0.75rem; color: #ffffff; font-weight: 600;" >{crime_type}</span>
                    </div>

                    <div style="margin-bottom: 1rem;" >
                        <span style="font-size: 0.875rem; font-weight: bold;" >{decoded_title}</span>
                    </div>

                    <div class="mt-4 text-xs text-slate-600 ">

                        <p class="text-xs flex items-center ml-3">
                            <span class='text-sky-600'> {location} </span>
                        </p>

                        <p class="text-xs flex items-center ml-3">
                            <span>Coordinates:</span>
                            <span style="color: #0284C7">{latVal}</span>,  
                            <span style="color: #0284C7">{longVal}</span>
                        </p>
                    </div>
            """
        
        popup_iframe = folium.IFrame(width=200, height=150, html=html_popup)

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


    return mapObj._repr_html_()


def load_marker(request):

    # Attempt to retrieve the marker map HTML from the cache
    marker_map_html = cache.get('cached_marker_map')

    if marker_map_html is None:
        # If not found in the cache, generate the marker map HTML
        marker_map_html = generate_marker_map()  # Replace with your marker map generation code

        # Store the generated marker map HTML in the cache with a timeout (e.g., 3600 seconds)
        cache.set('cached_marker_map', marker_map_html, None)

    context = {'map': marker_map_html}

    return JsonResponse(context)

@csrf_exempt
def load_crime_analytics(request):
    data = pd.read_csv('./static/csv/gmanews.csv')

    # Lowercase and strip
    data['location'] = data['location'].str.lower().str.strip()

    # Filter Quezon City
    qc_data = data[data['location'].str.contains('quezon city', case=False, na=False)]

    # Pie chart visualization
    plt.figure(figsize=(8, 8))
    colors = ['red', '#FFC000', '#FFF5EE', '#93C572', '#1434A4', '#800080'] 
    crime_counts = qc_data['crime'].value_counts()
    plt.pie(crime_counts, labels=crime_counts.index, autopct='%1.1f%%', startangle=140, colors=colors)
    plt.title('Index Crime Counts in Quezon City')

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image1 = base64.b64encode(buffer.read()).decode()
    buffer.close()

    # Extract date info
    qc_data['published_date'] = pd.to_datetime(qc_data['published_date'], format='%m/%d/%Y %H:%M')

    # Extract the year and create new column
    qc_data['year'] = qc_data['published_date'].dt.year

    # Remove year 2018
    qc_data = qc_data[qc_data['year'] != 2018]

    # Stacked Bar chart
    plt.figure(figsize=(10, 6))
    crime_year = qc_data.groupby(['year', 'crime']).size().unstack(fill_value=0)
    crime_year.plot(kind='bar', stacked=True, colormap='Paired', ax=plt.gca())
    plt.title('Distribution of Crime Types in Quezon City per Year')
    plt.xlabel('Year')
    plt.ylabel('Number of Crimes')
    plt.grid(False)
    plt.legend(title='Crime Type', loc='upper right')
    plt.xticks(rotation=0)

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image2 = base64.b64encode(buffer.read()).decode()
    buffer.close()

    context = {
        'image1': "data:image/png;base64,"+image1, 
        'image2': "data:image/png;base64,"+image2
    }

    return JsonResponse(context)

def load_crime_index(request):

    # Assuming 'data' is a DataFrame
    data = pd.read_csv('./static/csv/gmanews.csv')

    # Lowercase and strip the 'location' column
    data['location'] = data['location'].str.lower().str.strip()

    # Filter Quezon City
    qc_data = data[data['location'].str.contains('quezon city', case=False, na=False)]

    # Group filtered data by location and crime type
    grouped_data = qc_data.groupby(['location', 'crime']).size().unstack(fill_value=0)
    grouped_data['Total Index Crime'] = grouped_data.sum(axis=1)

    grouped_data.columns.name = ''
    grouped_data = grouped_data.reset_index()

    # Generate HTML table with Tailwind CSS classes and padding
    table_html = '''
        <table class="table-auto border-collapse border border-slate-400 mx-auto my-5">
            <thead class="border border-slate-400 bg-slate-500 text-white">
                <tr>
                    <th class="p-4">Location</th>
    '''

    # Add crime type columns dynamically
    table_html += "".join(['                <th class="p-4">{}</th>\n'.format(crime_type) for crime_type in grouped_data.columns[1:-1]])

    # Add more columns as needed
    table_html += '                <th class="p-4">Total Index Crime</th>\n'
    table_html += '            </tr>\n        </thead>\n        <tbody>\n'

    # Iterate over rows and add data
    for _, row in grouped_data.iterrows():
        table_html += '            <tr>\n' 
        table_html += '                <td class="p-4 border border-slate-400 capitalize">{}</td>\n'.format(row["location"])
        # Add crime type columns dynamically
        table_html += "".join(['                <td class="p-4 border border-slate-400">{}</td>\n'.format(row[crime_type]) for crime_type in grouped_data.columns[1:-1]])
        # Add more columns as needed
        table_html += '                <td class="p-4 border border-slate-400 font-bold">{}</td>\n'.format(row["Total Index Crime"])
        table_html += '            </tr>\n'

    # Close the HTML table
    table_html += '''
            </tbody>
        </table>
    '''

    # Add Tailwind CSS script to the HTML
    script_code = '''
        <script src="https://cdn.tailwindcss.com"></script>
    '''

    # Concatenate the script with the table HTML
    table_html_with_script = table_html + script_code



    context = {
        'table_html': table_html_with_script
    }

    return JsonResponse(context)

class AnalyticsView(LoginRequiredMixin, View):

    def dispatch(self, request, *args, **kwargs):
        # Set the previous page URL in the session
        request.session["prev_page"] = request.path
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        request.session["prev_page"] = request.path
        return render(request, 'app/analytics.html')
    









        
           

        



















@csrf_exempt
@login_required
def logout_and_clear_sessions(request):
    auth.logout(request)  # Logout the user
    request.session.flush()  # Clear all sessions
    cache.clear()
    return redirect('/login')


