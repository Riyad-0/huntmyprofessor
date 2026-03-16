FSA demo

[start] --(send_request (GET login page))--> [Response: login page] --(parse_response)--> [Hidden fields + Cookie]
--(send_request (POST log in))--> [Response: professor search page] --(parse_response)--> [Hidden fields + Cookie]
--(send_request (POST professor name))-> [Response: professor course list page] --(parse_response)--> [Course list]