#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/time.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <string.h>

#define UDP_PORT 8888
#define TARGET_IP "127.0.0.1"

int main(void) {
    int sockfd;
    struct sockaddr_in servaddr;
    struct timeval start, end;
    long elapsed_time = 0;
    int sendCount = 0;

    // 发送时长，单位毫秒
    int time_window = 10000;

    sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sockfd < 0) {
        perror("socket creation failed");
        return 1;
    }

    memset(&servaddr, 0, sizeof(servaddr));
    servaddr.sin_family = AF_INET;
    servaddr.sin_port = htons(UDP_PORT);
    if (inet_pton(AF_INET, TARGET_IP, &servaddr.sin_addr) <= 0) {
        perror("invalid target IP address");
        close(sockfd);
        return 1;
    }

    gettimeofday(&start, NULL);

    while (elapsed_time < time_window) {
        if (sendto(sockfd, "1", 1, 0,
                   (struct sockaddr *)&servaddr,
                   sizeof(servaddr)) < 0) {
            perror("sendto failed");
            close(sockfd);
            return 1;
        }

        sendCount++;

        gettimeofday(&end, NULL);
        elapsed_time = (end.tv_sec - start.tv_sec) * 1000000L +
                       (end.tv_usec - start.tv_usec);
        elapsed_time /= 1000;
    }

    printf("sent %d packets in %d ms\n", sendCount, time_window);

    close(sockfd);
    return 0;
}
