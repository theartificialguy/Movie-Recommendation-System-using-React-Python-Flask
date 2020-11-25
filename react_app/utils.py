import os
import json
import requests
import numpy as np
import pandas as pd
from tmdbv3api import TMDb
from tmdbv3api import Movie
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer

data = pd.read_csv("data/movie_dataset.csv")

selected_features = ['index', 'title', 'genres', 'keywords', 'cast', 'director']

df = data[selected_features]

df = df.fillna("")

def combine_rows(row):
    combined_feature = row['genres']+" "+row['keywords']+" "+row['cast']+" "+row['director']
    return combined_feature

df["combined_features"] = df.apply(combine_rows, axis=1)

def find_cosine_similarity(features):
    cv = CountVectorizer() #vector representation
    count_mat = cv.fit_transform(features) #matrix of number count of each word
    cosine_sim = cosine_similarity(count_mat) #2D NxN coeff. matrix of cosine angles
    return cosine_sim

def get_title_from_index(index):
    try:
        title = df[df.index == index]["title"].values[0]
        return title
    except Exception as e:
        return "Sorry, Movie not found! Try another."

def get_index_from_title(title):
    try:
        return df[df.title == title]["index"].values[0]
    except Exception as e:
        return -1

tmdb = TMDb()
tmdb_movie = Movie()

tmdb.api_key = "5f79eea93c345aa0aaeb66e60b0765bd"

CONFIG_PATTERN = 'http://api.themoviedb.org/3/configuration?api_key={}'.format(tmdb.api_key)

url = CONFIG_PATTERN.format(key=tmdb.api_key)
r = requests.get(url)
config = r.json()

base_url = config['images']['base_url']
sizes = config['images']['poster_sizes']

def size_str_to_int(x):
    return float("inf") if x == 'original' else int(x[1:])

max_image_size = max(sizes, key=size_str_to_int)

def get_new_movie_data(correct_movie_name):
    
    # Getting Title -> correct_movie_name
    movie_id = correct_movie_name.id
    
    # Getting Genre
    response1 = requests.get('https://api.themoviedb.org/3/movie/{}?api_key={}'.format(movie_id,tmdb.api_key))
    json_data1 = response1.json()
    genres = [json_data1['genres'][i]['name'] for i in range(len(json_data1['genres']))]

    # Getting Director
    response2 = requests.get('https://api.themoviedb.org/3/movie/{} \
                             /credits?api_key={}'.format(movie_id, tmdb.api_key))
    
    json_data2 = response2.json()

    directors = []
    for nested_dict in json_data2['crew']:
        if nested_dict['department'] == 'Directing':
            directors.append(nested_dict['name'])

    # Getting Cast
    cast = []
    for nested_dict in json_data2['cast']:
        cast.append(nested_dict['name'])

    # Getting Keywords
    response3 = requests.get('https://api.themoviedb.org/3/movie/{} \
                             /keywords?api_key={}'.format(movie_id, tmdb.api_key))

    json_data3 = response3.json()

    keywords = []
    for nested_dict in json_data3['keywords']:
        keywords.append(nested_dict['name'])

    data = {'index': int(df.index[-1]),
            'title': str(correct_movie_name),
            'genres': genres,
            'keywords': keywords,
            'cast': cast,
            'director': directors}
    
    new_record = pd.DataFrame.from_dict(data, orient='index')
    new_record = new_record.transpose()
    
    # converting list of strings to string
    for col in ['genres','keywords','cast','director']:
        new_record[col] = new_record[col].apply(' '.join)
    
    new_record['combined_features'] = new_record.apply(combine_rows, axis=1)

    return new_record

def get_movie_details(movie_name):

    movie_id = tmdb_movie.search(movie_name)[0].id

    #movie poster
    IMG_PATTERN = 'http://api.themoviedb.org/3/movie/{}/images?api_key={}'.format(movie_id, tmdb.api_key)
    image_response = requests.get(IMG_PATTERN.format(key=tmdb.api_key,imdbid=movie_id))
    api_response = image_response.json()
    posters = api_response['posters']
    rel_path = posters[0]['file_path']
    image_url = "{0}{1}{2}".format(base_url, max_image_size, rel_path)

    #saving images server side
    save_path = '/home/yash/Desktop/end-to-end-projects/movie recommendation/react_app/my-app/public/movie_posters/'
    filetype = "jpg"
    filename = '{0}.{1}'.format(movie_name.replace(" ", "_"), filetype) 
    if filename in os.listdir(save_path):
        print("[INFO] Image already present in directory!")
    else:
        with open(save_path+filename,'wb') as w:
            r = requests.get(image_url, stream=True)
            if not r.ok:
                print(r)
            for block in r.iter_content(1024):
                if not block:
                    break
                w.write(block)

    #about movie 
    details = tmdb_movie.details(movie_id)

    #genre
    response1 = requests.get('https://api.themoviedb.org/3/movie/{}?api_key={}'.format(movie_id,tmdb.api_key))
    json_data1 = response1.json()
    genres = [json_data1['genres'][i]['name'] for i in range(len(json_data1['genres']))]

    #cast
    response2 = requests.get('https://api.themoviedb.org/3/movie/{} \
                             /credits?api_key={}'.format(movie_id, tmdb.api_key))
    
    json_data2 = response2.json()

    cast = []
    for nested_dict in json_data2['cast']:
        cast.append(nested_dict['name'])

    data = {
        "image_url": image_url,
        "movie_overview": details.overview,
        "genre": genres,
        "cast": cast[:5] #getting only top 5 cast from a whole list
    }

    return data

def get_recommendation(user_movie_input, df=df):
    
    cosine_sim = find_cosine_similarity(df['combined_features'])

    try:
        correct_movie_name = tmdb_movie.search(user_movie_input)
        print("Corrected movie name: ", correct_movie_name[0])
    
    except Exception as e:
        return ["No movie found named '{}', Please try a different movie".format(user_movie_input)]
    
    movie_index = get_index_from_title(str(correct_movie_name[0]))

    if movie_index == -1:
        # If movie index is not found in our data
        # Generate that movie data and append to df, find cosine similarity again and repeat the process
        new_record = get_new_movie_data(correct_movie_name[0])
        df = df.append(new_record, ignore_index=True)
        cosine_sim = find_cosine_similarity(df['combined_features'])
        movie_index = get_index_from_title(str(correct_movie_name[0]))

    similar_movies = list(enumerate(cosine_sim[movie_index]))

    # firstMovie = sorted(similar_movies, key=lambda x:x[1], reverse=True)[0]
    sorted_similar_movies = sorted(similar_movies, key=lambda x:x[1], reverse=True)[1:]
    
    i=0
    movies = []
    for element in sorted_similar_movies:
        movies.append(get_title_from_index(element[0]))
        if i>5:
            break
        i=i+1

    final_data = {}
    for movie in movies:
        data_object = get_movie_details(movie)
        final_data[movie] = data_object

    return final_data