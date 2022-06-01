window.parseISOString = function parseISOString(s) {
  var b = s.split(/\D+/);
  return new Date(Date.UTC(b[0], --b[1], b[2], b[3], b[4], b[5], b[6]));
};


// get the recently linked shows wrapper

//  get the url of the visited page
let baseurl = window.location;

// compare it to the home page
// if it is the home page, show the recently linked shows

if (baseurl == "http://127.0.0.1:5000/") {
  // display the container parent element
  let parent = document.getElementById("merit");

  parent.style.display = "block";
  // api end point
  let API_ENDPOINT = '/recently-listed-artist';


  // create our dom elements for appending


  let createDomElements = (data,container) => {
    // check if the data is an array 
    let isArray = Array.isArray(data) ? true : false;
    if (isArray && data.length > 0) {
      let DOM = data.map(element => {
         let htmlDoc = function(){
           return (`
           <div class ="col-sm-3">
              <div class="tile tile-show">
                  <img src="${element.artist_image_link}" alt="Artist Image" />
                  <h5><a href="/artists/${element.artist.id}">${name}</a></h5>
                  <p>upcoming shows: ${element.upcoming_shows}</p>
              </div>
           </div> 
           `)
         }
          return htmlDoc();
      }).join("");
      container.innerHTML = DOM;
    }
  }

  // get the data from the API

  let fetchData_artist = fetch(API_ENDPOINT,{
    method: 'GET',
    headers: {
      'Content-Type': 'application/json'
    }
  })

  // parse the data

  fetchData_artist.then ( response => {
    return response.json();
  })
  .then( (data )=> {
    let container = document.getElementById("recently-listed-artist");
    createDomElements(data,container);
  })
  .catch ( (err) => {
    console.log(err);
  })

  // get the data from the recently linked venues API

  let API_ENDPOINT_venue = '/recently-listed-venue';

  fetchData_venue = fetch(API_ENDPOINT_venue,{
    method: 'GET',
    headers: {
      'Content-Type': 'application/json'
    }
  })

  // parse the data

  fetchData_venue.then ( response => {
    return response.json();
  }
  ).then( (data )=> {
    createDomElements(data,"venue","venue","img","container");
  }
  ).catch ( (err) => {
    console.log(err);
  }
  )

}