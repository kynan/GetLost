GetLost
=======

Discover paths off the beaten track. Avoiding popular places means a higher
ranked route.

Built at [Urban Data Hack](http://urbandatahack.com) London, Feb 15-16 2014.

Usage
-----
```
GET /route/<from_lat>,<from_lng>/<to_lat>,<to_lng>
```
Response:
```
{
  "route": /* Foot walking directions provided by MapQuest */,
  "hip_rank": /* Array of hipster ranks along the route */,
  "total_rank": /* Accumulated hipster score of the route */
}
```
