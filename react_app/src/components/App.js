import React, { useState } from "react";
import Movies from "./Movies";
import Footer from "./Footer";

function App() {
  //defining react state hooks
  const [movieName, setMovieName] = useState("");
  const [newOver, setNewOver] = useState(false);
  const [ptag, setPtag] = useState({ ptag1: "", ptag2: "" });
  const [movies, setMovies] = useState([]);

  //defining button event functions

  //function for submission handling
  function HandleClick(event) {
    //to prevent reloading the page after submitting the form
    event.preventDefault();

    setPtag({
      ptag1: `Results for "` + movieName + `" . . .`,
      ptag2: "Recommended for you ..."
    });

    //sending data to backend
    console.log("Making request to backend ...");

    fetch("http://127.0.0.1:5000/result", {
      method: "POST",
      cache: "no-cache",
      headers: {
        content_type: "application/json"
      },
      body: JSON.stringify({"movie_name": movieName})
    })
      .then((response) => {
        return response.json();
      })
      .then((data) => {
        setMovies(data);
      });
    console.log("data recieved from server =>");
    console.log(movies);
  }

  function handleOver() {
    setNewOver(true);
  }

  function handleOut() {
    setNewOver(false);
  }

  function handleChange(event) {
    const mn = event.target.value;
    setMovieName(mn);
  }

  return (
    <div className="container">
      <h1>Hello there !</h1>
      <form onSubmit={HandleClick}>
        <input
          name="mName"
          type="text"
          onChange={handleChange}
          placeholder="Enter Movie Name"
          value={movieName}
        />

        <button
          type="submit"
          onMouseOver={handleOver}
          onMouseOut={handleOut}
          style={{ backgroundColor: newOver ? "grey" : "white" }}
        >
          Search
        </button>
      </form>
      <p>{ptag.ptag1}</p>
      <h2>{ptag.ptag2}</h2>
      <Movies Rmovies={movies} />

      <Footer />
    </div>
  );
}

export default App;
