import fetchStats from "../fetchStats.js";
function fetchstat(uuid, username) {
    return fetchStats(uuid, username);
}

fetchstat(process.argv[2], process.argv[3]).then(result => {
    console.log(JSON.stringify(result));
    process.exit(0);
}).catch(error => {
    console.error("Error:", error);
    process.exit(1);
});