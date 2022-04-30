

/**
 * Gets a URL parameter from the query string
 */
 function turkGetParam( name, defaultValue ) { 
    var regexS = "[?&]"+name+"=([^&#]*)"; 
    var regex = new RegExp( regexS ); 
    var tmpURL = window.location.href; 
    var results = regex.exec( tmpURL ); 
    if( results == null ) { 
      return defaultValue; 
    } else { 
      return results[1];    
    } 
 }
 
 /**
  * URL decode a parameter
  */
 function decode(strToDecode)
 {
   var encoded = strToDecode;
   return unescape(encoded.replace(/\+/g,  " "));
 }
 
 
 /**
  * Returns the Mechanical Turk Site to post the HIT to (sandbox. prod)
  */
 export function turkGetSubmitToHost() {
     var defaultHost = "https://www.mturk.com";
     var submitToHost = decode(turkGetParam("turkSubmitTo", defaultHost));
     if (stringStartsWith(submitToHost, "https://")) {
         return submitToHost;
     }
     if (stringStartsWith(submitToHost, "http://")) {
         return submitToHost;
     }
     if (stringStartsWith(submitToHost, "//")) {
         return submitToHost;
     }
     return defaultHost;
 }
 
 export function turkGetAssignmentId() {
   const assignmentID = turkGetParam('assignmentId', "");
   return assignmentID;
 }


 const handleSubmit = (assignmentId, turkSubmitTo, doc_json, summary_json, g_completed) => {
    
    /****************************** MUST ******************************** */
    // const urlParams = new URLSearchParams(window.location.search)
   
    // create the form element and point it to the correct endpoint
    const form = document.createElement('form')
    // form.action = (new URL('mturk/externalSubmit', urlParams.get('turkSubmitTo'))).href
    form.action = turkSubmitTo + "/mturk/externalSubmit"; 
    form.method = 'post'
   
    // attach the assignmentId
    const inputAssignmentId = document.createElement('input')
    inputAssignmentId.name = 'assignmentId'
    // inputAssignmentId.value = urlParams.get('assignmentId')
    inputAssignmentId.value = assignmentId
    inputAssignmentId.hidden = true
    form.appendChild(inputAssignmentId)
    /******************************************************************** */

    /****************************** for you to choose  ******************************** */
    const inputSummaryJson = document.createElement('input')
    inputSummaryJson.name = 'summary_json'
    inputSummaryJson.value = JSON.stringify(summary_json)
    inputSummaryJson.hidden = true
    form.appendChild(inputSummaryJson)
    /******************************************************************** */

    /****************************** MUST ******************************** */
    // attach the form to the HTML document and trigger submission
    document.body.appendChild(form)
    form.submit()
    /******************************************************************** */
  }






/* THIS SHOULD BE WHERE YOU START YOUR APP */
const [assignmentId, SetAssignmentId] = useState("")
const [turkSubmitTo, SetMturkTurkSubmitTo] = useState("https://www.mturk.com")

useEffect(() => {
    const assignment_id = turkGetAssignmentId();
    const turk_submit_to = turkGetSubmitToHost();
    SetAssignmentId(assignment_id)
    SetMturkTurkSubmitTo(turk_submit_to)

}, [])