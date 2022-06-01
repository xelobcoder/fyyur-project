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


  let createDomElements = (data) => {
    // check if the data is an array 
    let isArray = Array.isArray(data) ? true : false;
    if (isArray && data.length > 0) {
      let DOM = data.map(element => {
         let htmlDoc = function(){
           return (`
           <div class ="col-sm-3">
              <div class="tile tile-show">
                  <img src="${element.artist_image_link}" alt="Artist Image" />
                  <h5><a href="/artists/${element.artist_id}">${element.artist_name}</a></h5>
                  <p>upcoming shows: ${element.upcoming_shows}</p>
              </div>
           </div> 
           `)
         }
          return htmlDoc();
      }).join("");
      let container = document.getElementById("recently-listed-artist");
      container.innerHTML = DOM;
    } else{
      // do not display recent shows
      let head_display = document.querySelectorAll("#listed-head")[0];

      head_display.style.display = 'none';
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
    createDomElements(data);
  })
  .catch ( (err) => {
    console.log(err);
  })
 

  // get the data from the API
  let API_ENDPOINT_2 = '/recently-listed-venue';

  fetchData_venue = fetch(API_ENDPOINT_2,{
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
    if(Array.isArray(data) && data.length > 0){
      let DOM = data.map(element => {
        let htmlDoc = function(){
          return (`
          <div class ="col-sm-3">
             <div class="tile tile-show">
                 <img src="${element.venue_image_link}" alt="Venue Image" />
                 <h5><a href="/venues/${element.venue_id}">${element.venue_name}</a></h5>
                 <p>upcoming shows: ${element.upcoming_shows}</p>
             </div>
          </div> 
          `)
        }
         return htmlDoc();
     }).join("");
     let container = document.getElementById("recently-listed-venue");
      container.innerHTML = DOM;
    } else {
      // do not display recently listed venues

      let container = document.querySelectorAll("#listed-head")[1];

      container.style.display = "none";
    }
  }
  ).catch ( (err) => {
    console.log(err);
  }
  )

}