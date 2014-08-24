#ifndef _COMMUNICATION_H
#define _COMMUNICATION_H

#include "Arduino.h"
#include "behaviour.h"

boolean receive_msg(byte recv_data_buff[], byte send_data_buff[])
void send_msg(byte data_buff[])
void parse_msg(byte data_buff[])
void compose_reply(byte data_buff[], byte front_signature, byte back_signature)

#endif
