#include "mbed.h"
#include "mbed_trace.h"

#ifndef DEVICE_TRNG
#error "mbed-os-example-tls-socket requires a device which supports TRNG"
#else

const char cert[] = \
    "-----BEGIN CERTIFICATE-----\n"
    "MIIDdzCCAl+gAwIBAgIEAgAAuTANBgkqhkiG9w0BAQUFADBaMQswCQYDVQQGEwJJ\n"
    "RTESMBAGA1UEChMJQmFsdGltb3JlMRMwEQYDVQQLEwpDeWJlclRydXN0MSIwIAYD\n"
    "VQQDExlCYWx0aW1vcmUgQ3liZXJUcnVzdCBSb290MB4XDTAwMDUxMjE4NDYwMFoX\n"
    "DTI1MDUxMjIzNTkwMFowWjELMAkGA1UEBhMCSUUxEjAQBgNVBAoTCUJhbHRpbW9y\n"
    "ZTETMBEGA1UECxMKQ3liZXJUcnVzdDEiMCAGA1UEAxMZQmFsdGltb3JlIEN5YmVy\n"
    "VHJ1c3QgUm9vdDCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAKMEuyKr\n"
    "mD1X6CZymrV51Cni4eiVgLGw41uOKymaZN+hXe2wCQVt2yguzmKiYv60iNoS6zjr\n"
    "IZ3AQSsBUnuId9Mcj8e6uYi1agnnc+gRQKfRzMpijS3ljwumUNKoUMMo6vWrJYeK\n"
    "mpYcqWe4PwzV9/lSEy/CG9VwcPCPwBLKBsua4dnKM3p31vjsufFoREJIE9LAwqSu\n"
    "XmD+tqYF/LTdB1kC1FkYmGP1pWPgkAx9XbIGevOF6uvUA65ehD5f/xXtabz5OTZy\n"
    "dc93Uk3zyZAsuT3lySNTPx8kmCFcB5kpvcY67Oduhjprl3RjM71oGDHweI12v/ye\n"
    "jl0qhqdNkNwnGjkCAwEAAaNFMEMwHQYDVR0OBBYEFOWdWTCCR1jMrPoIVDaGezq1\n"
    "BE3wMBIGA1UdEwEB/wQIMAYBAf8CAQMwDgYDVR0PAQH/BAQDAgEGMA0GCSqGSIb3\n"
    "DQEBBQUAA4IBAQCFDF2O5G9RaEIFoN27TyclhAO992T9Ldcw46QQF+vaKSm2eT92\n"
    "9hkTI7gQCvlYpNRhcL0EYWoSihfVCr3FvDB81ukMJY2GQE/szKN+OMY3EU/t3Wgx\n"
    "jkzSswF07r51XgdIGn9w/xZchMB5hbgF/X++ZRGjD8ACtPhSNzkE1akxehi/oCr0\n"
    "Epn3o0WC4zxe9Z2etciefC7IpJ5OCBRLbf1wbWsaY71k5h+3zvDyny67G7fyUIhz\n"
    "ksLi4xaNmjICq44Y3ekQEe5+NauQrz4wlHrQMz2nZQ/1/I6eYs9HRCwBXbsdtTLS\n"
    "R9I4LtD+gdwyah617jzV/OeBHRnDJELqYzmp\n"
    "-----END CERTIFICATE-----";


int main(void)
{
    char *buffer = new char[256];
    nsapi_size_or_error_t result;
    nsapi_size_t size;
    const char query[] = "GET / HTTP/1.1\r\nHost: ifconfig.io\r\nConnection: close\r\n\r\n";

    mbed_trace_init();

    printf("TLSSocket Example.\n");
    printf("Mbed OS version: %d.%d.%d\n\n", MBED_MAJOR_VERSION, MBED_MINOR_VERSION, MBED_PATCH_VERSION);

    NetworkInterface *net = NetworkInterface::get_default_instance();

    if (!net) {
        printf("Error! No network inteface found.\n");
        return 0;
    }

    printf("Connecting to network\n");
    result = net->connect();
    if (result != NSAPI_ERROR_OK) {
        printf("Error! net->connect() returned: %d\n", result);
        return result;
    }

    printf("Connecting to ifconfig.io\n");
    SocketAddress addr;
    result = net->gethostbyname("ifconfig.io", &addr);
    if (result != NSAPI_ERROR_OK) {
	printf("Error! DNS resolution for ifconfig.io failed with %d\n", result);
    }
    addr.set_port(443);

    TLSSocket *socket = new TLSSocket;
    result = socket->open(net);
    if (result != NSAPI_ERROR_OK) {
        printf("Error! socket->open() returned: %d\n", result);
        return result;
    }

    socket->set_hostname("ifconfig.io");

    result = socket->set_root_ca_cert(cert);
    if (result != NSAPI_ERROR_OK) {
        printf("Error: socket->set_root_ca_cert() returned %d\n", result);
        return result;
    }

    result = socket->connect(addr);
    if (result != NSAPI_ERROR_OK) {
        printf("Error! socket->connect() returned: %d\n", result);
        goto DISCONNECT;
    }

    // Send a simple http request
    size = strlen(query);
    result = socket->send(query, size);
    if (result != size) {
        printf("Error! socket->send() returned: %d\n", result);
        goto DISCONNECT;
    }

    // Receieve an HTTP response and print out the response line
    while ((result = socket->recv(buffer, 255)) > 0) {
        buffer[result] = 0;
        printf("%s", buffer);
    }
    printf("\n");

    if (result < 0) {
        printf("Error! socket->recv() returned: %d\n", result);
        goto DISCONNECT;
    }


DISCONNECT:
    delete[] buffer;
    // Close the socket to return its memory
    socket->close();
    delete socket;

    // Bring down the network interface
    net->disconnect();
    printf("Done\n");
}
#endif
