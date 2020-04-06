Description
===========

Kimsufi is a subbrand of OVH which offers "budget" dedicated servers in Montreal and France.  Certain server configurations can be hard to come by and when availability does open up, they are quickly allocated.  This AWS Lambda function notifies the user by SMS when their specific configuration becomes available.

How to use
==========

1. Create a Python 3.8 Lambda function in AWS with permissions to send SMS messages using SNS service.

2. Determine the server configuration you want to monitor.  To do this you need to visit Kimsufi's server availability list page (//www.kimsufi.com/ca/en/servers.xml), and try to determine the mapping based on the order links.  For example (KS-12, Montreal): https://www.kimsufi.com/ca/en/order/kimsufi.xml?reference=1804sk23

The above reference identifier (1804sk23), here is a mapping as of this point in time:

Config | Montreal | France
KS-1 | 1804sk12 | 1801sk12
KS-2 | 1804sk13 | 1801sk13
KS-3 | 1804sk14 | 1801sk14
Ks-4 | 1804sk15 | 1801sk15
KS-5 | 1804sk16 | 1801sk16
KS-6 | 1804sk17 | 1801sk17
KS-7 | 1804sk18 | 1801sk18
KS-8 | 1804sk19 | 1801sk19
KS-9 | 1804sk20 | 1801sk20
KS-10 | 1804sk21 | 1801sk21
KS-11 | 1804sk22 | 1801sk22
KS-12 | 1804sk23 | 1801sk23

3. Create a CloudWatch Rule in AWS that run's on a schedule (of your choosing), configured to execute your Lambda function with a JSON string passed to it that includes your desired config and SMS enabled phone number to be notified at:

{
  "server": "1804sk23",
  "phone": "+15555555555"
}
