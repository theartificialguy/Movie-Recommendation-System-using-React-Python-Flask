import React from "react";

function displayMovieName(movie_name) {
  var filetype = ".jpg";
  const image = '/movie_posters/'+movie_name.replace(/ /g, "_")+filetype;
  console.log(image);
  return (
    <div className="movieCard">
      {/* <h3>{movie_name}</h3> */}
      <img src={image} alt={movie_name}></img>
    </div>
  );
}

function displayMovieDetails(movie_details) {
  return Object.entries(movie_details).map(([key, value]) => {
    if (key === "movie_overview") {
      return (
        <div className="movieOverview">
          <h3>Overview</h3>
          <p>{movie_details[key]}</p>
        </div>
      );
    } else if (key === "genre") {
      return movie_details[key].map((val) => {
        return (
          <div className="movieGenre">
            <h4>{val}</h4>
          </div>
        );
      });
    } else if (key === "cast") {
      return movie_details[key].map((val) => {
        return (
          <div className="movieCast">
            <h4>{val}</h4>
          </div>
        );
      });
    }
  });
}

function Movies(props) {
  const movies = props.Rmovies;
  return Object.entries(movies).map(([key, value]) => {
    return (
      <div className="movie">
        <h2>{displayMovieName(key)}</h2>
        <p>{displayMovieDetails(value)}</p>
      </div>
    );
  });
}

export default Movies;
