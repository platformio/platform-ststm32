/*
 * Copyright (c) 2019, Arm Limited and affiliates.
 * SPDX-License-Identifier: Apache-2.0
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#ifndef WISUN_TEST_CERTIFICATES_H_
#define WISUN_TEST_CERTIFICATES_H_

const uint8_t WISUN_ROOT_CERTIFICATE[] = {
    "-----BEGIN CERTIFICATE-----\r\n"
    "MIIBLzCB1qADAgECAhQooDtB2DFWFsDlkVyeKLkkFq27vTAKBggqhkjOPQQDAjAN\r\n"
    "MQswCQYDVQQDEwJDQTAiGA8wMDAwMDEwMTAwMDAwMFoYDzk5OTkxMjMxMjM1OTU5\r\n"
    "WjANMQswCQYDVQQDEwJDQTBZMBMGByqGSM49AgEGCCqGSM49AwEHA0IABG0ZABD+\r\n"
    "g8Nvc9KBpw/aHhoim9KrqzOYP5qTmZgS8uxM/eqeAJ6vrSivWFT2fxHuzXG+yfvs\r\n"
    "oPNgBJhv/YNhM9KjEDAOMAwGA1UdEwQFMAMBAf8wCgYIKoZIzj0EAwIDSAAwRQIg\r\n"
    "CK00/WNqrLzSt7QtustgbL+kibXBuWFeYBjU5yPbaHECIQD8aFwPt2/oXLOSa7gB\r\n"
    "9nwpA1rsmzCJLvb8ouxQ3uhXbg==\r\n"
    "-----END CERTIFICATE-----"
};

const uint8_t WISUN_SERVER_CERTIFICATE[] = {
    "-----BEGIN CERTIFICATE-----\r\n"
    "MIIBbzCCARUCFHsX/aO/8skZ/3NAQrzQ957H/aNYMAoGCCqGSM49BAMCMA0xCzAJ\r\n"
    "BgNVBAMTAkNBMCIYDzAwMDAwMTAxMDAwMDAwWhgPOTk5OTEyMzEyMzU5NTlaMGMx\r\n"
    "CzAJBgNVBAYTAkZJMQ0wCwYDVQQIDARPdWx1MQ0wCwYDVQQHDARPdWx1MQ0wCwYD\r\n"
    "VQQKDAR0ZXN0MQ0wCwYDVQQDDAR0ZXN0MRgwFgYJKoZIhvcNAQkBFgl0ZXN0QHRl\r\n"
    "c3QwWTATBgcqhkjOPQIBBggqhkjOPQMBBwNCAAQtbrqK+Z2gWz9rgvS4fgkWn1kb\r\n"
    "wERr15kFr7CmNM63gAmMyS08m5/sBYps5XUdIwF+Pz8uYmk4LpSl+o0OLkmaMAoG\r\n"
    "CCqGSM49BAMCA0gAMEUCIDknuOd/stYYgK3oztxspnKBHoOO8UcUB3PH2AfIq24e\r\n"
    "AiEA8OMJ44i3TKToinV1IATm81mqu+5pBqYu4RtX0E/xP88=\r\n"
    "-----END CERTIFICATE-----"
};

const uint8_t WISUN_SERVER_KEY[] = {
    "-----BEGIN EC PRIVATE KEY-----\r\n"
    "MHcCAQEEIEvbJ9SG/qeud6z3oRb+sROxk6/HWHQWtcucDFq3grzooAoGCCqGSM49\r\n"
    "AwEHoUQDQgAELW66ivmdoFs/a4L0uH4JFp9ZG8BEa9eZBa+wpjTOt4AJjMktPJuf\r\n"
    "7AWKbOV1HSMBfj8/LmJpOC6UpfqNDi5Jmg==\r\n"
    "-----END EC PRIVATE KEY-----"
};

const uint8_t WISUN_CLIENT_CERTIFICATE[] = {
    "-----BEGIN CERTIFICATE-----\r\n"
    "MIIBbzCCARUCFHsX/aO/8skZ/3NAQrzQ957H/aNZMAoGCCqGSM49BAMCMA0xCzAJ\r\n"
    "BgNVBAMTAkNBMCIYDzAwMDAwMTAxMDAwMDAwWhgPOTk5OTEyMzEyMzU5NTlaMGMx\r\n"
    "CzAJBgNVBAYTAkZJMQ0wCwYDVQQIDARPdWx1MQ0wCwYDVQQHDARPdWx1MQ0wCwYD\r\n"
    "VQQKDAR0ZXN0MQ0wCwYDVQQDDAR0ZXN0MRgwFgYJKoZIhvcNAQkBFgl0ZXN0QHRl\r\n"
    "c3QwWTATBgcqhkjOPQIBBggqhkjOPQMBBwNCAARIJ0hVdYmPsTFmY3glVAzE6dRE\r\n"
    "6Vp3rEUwqKqfMaJWvxd8EszaMP6PUwn4bprMkUPRmISTe8T17K8ZSRi8gun7MAoG\r\n"
    "CCqGSM49BAMCA0gAMEUCIQCtQwnVemwlIUoXeMZ1WE3JHj9XAIbxg2lweRJ91XaV\r\n"
    "VgIgDyft6+GF3u31VmTljTMAZZcCNRXDP0eNha+gB0TlGhY=\r\n"
    "-----END CERTIFICATE-----"
};

const uint8_t WISUN_CLIENT_KEY[] = {
    "-----BEGIN EC PRIVATE KEY-----\r\n"
    "MHcCAQEEIOxOq1xL+Hv5hg6Zg41pVXpkjLTkZxXrBHJcExTUMAftoAoGCCqGSM49\r\n"
    "AwEHoUQDQgAESCdIVXWJj7ExZmN4JVQMxOnUROlad6xFMKiqnzGiVr8XfBLM2jD+\r\n"
    "j1MJ+G6azJFD0ZiEk3vE9eyvGUkYvILp+w==\r\n"
    "-----END EC PRIVATE KEY-----"
};

#endif /* WISUN_TEST_CERTIFICATES_H_ */
