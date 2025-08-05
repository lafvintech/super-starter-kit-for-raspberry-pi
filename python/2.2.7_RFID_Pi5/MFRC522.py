#!/usr/bin/env python3
# -*- coding: utf8 -*-
#
#    MFRC522-Python
#    A simple Python implementation for the MFRC522 NFC Card Reader for the Raspberry Pi.
#    Original Author: Mario Gomez <mario.gomez@teubi.co>
#    Modified by: Daniel Perron
#
#    -------------------------------------------------------------------------------------
#    Repository: https://github.com/danjperron/MFRC522-python
#    Modified by: LAFVIN
#    Date: 2025/8/5
#    -------------------------------------------------------------------------------------
#    Further modified for educational purposes (2024).
#    Modifications:
#    - Integrated modern Python practices including Type Hinting for all methods.
#    - Refactored C-style loops to be more Pythonic.
#    - Renamed methods to follow snake_case convention for better readability.
#    - Added backward compatibility aliases for original method names.
#    - Cleaned up debug print statements from I/O functions.
#
#    License:
#    This modified version is also licensed under the GNU Lesser General Public License v3.0.
#    Please refer to the original license for more details.

import spidev
from typing import List, Tuple, Optional

DEBUG = False

class MFRC522:
    # --- Constants ---
    MAX_LEN = 16

    # --- Command Definitions ---
    PCD_IDLE       = 0x00
    PCD_AUTHENT    = 0x0E
    PCD_RECEIVE    = 0x08
    PCD_TRANSMIT   = 0x04
    PCD_TRANSCEIVE = 0x0C
    PCD_RESETPHASE = 0x0F
    PCD_CALCCRC    = 0x03

    # --- PICC Command Definitions ---
    PICC_REQIDL     = 0x26
    PICC_REQALL     = 0x52
    PICC_ANTICOLL1  = 0x93
    PICC_ANTICOLL2  = 0x95
    PICC_ANTICOLL3  = 0x97
    PICC_AUTHENT1A  = 0x60
    PICC_AUTHENT1B  = 0x61
    PICC_READ       = 0x30
    PICC_WRITE      = 0xA0
    PICC_DECREMENT  = 0xC0
    PICC_INCREMENT  = 0xC1
    PICC_RESTORE    = 0xC2
    PICC_TRANSFER   = 0xB0
    PICC_HALT       = 0x50

    # --- Status Codes ---
    MI_OK       = 0
    MI_NOTAGERR = 1
    MI_ERR      = 2

    # --- Register Definitions ---
    # Page 0: Command and Status
    CommandReg     = 0x01
    CommIEnReg     = 0x02
    DivlEnReg      = 0x03
    CommIrqReg     = 0x04
    DivIrqReg      = 0x05
    ErrorReg       = 0x06
    Status1Reg     = 0x07
    Status2Reg     = 0x08
    FIFODataReg    = 0x09
    FIFOLevelReg   = 0x0A
    WaterLevelReg  = 0x0B
    ControlReg     = 0x0C
    BitFramingReg  = 0x0D
    CollReg        = 0x0E
    
    # Page 1: Command
    ModeReg        = 0x11
    TxModeReg      = 0x12
    RxModeReg      = 0x13
    TxControlReg   = 0x14
    TxAutoReg      = 0x15
    TxSelReg       = 0x16
    RxSelReg       = 0x17
    RxThresholdReg = 0x18
    DemodReg       = 0x19
    MifareReg      = 0x1C
    SerialSpeedReg = 0x1F

    # Page 2: CFG
    CRCResultRegM     = 0x21
    CRCResultRegL     = 0x22
    ModWidthReg       = 0x24
    RFCfgReg          = 0x26
    GsNReg            = 0x27
    CWGsPReg          = 0x28
    ModGsPReg         = 0x29
    TModeReg          = 0x2A
    TPrescalerReg     = 0x2B
    TReloadRegH       = 0x2C
    TReloadRegL       = 0x2D
    TCounterValueRegH = 0x2E
    TCounterValueRegL = 0x2F

    # Page 3: TestRegister
    TestSel1Reg     = 0x31
    TestSel2Reg     = 0x32
    TestPinEnReg    = 0x33
    TestPinValueReg = 0x34
    TestBusReg      = 0x35
    AutoTestReg     = 0x36
    VersionReg      = 0x37
    AnalogTestReg   = 0x38
    TestDAC1Reg     = 0x39
    TestDAC2Reg     = 0x3A
    TestADCReg      = 0x3B

    def __init__(self, bus: int = 0, dev: int = 0, spd: int = 1000000) -> None:
        """
        Initializes the MFRC522 reader.

        :param bus: SPI bus number (default=0).
        :param dev: SPI device number (default=0).
        :param spd: SPI speed in Hz (default=1,000,000).
        """
        self.spi = spidev.SpiDev()
        self.spi.open(bus=bus, device=dev)
        self.spi.max_speed_hz = spd
        self.init()

    # --- Core SPI Communication Methods ---

    def _write_reg(self, addr: int, val: int) -> None:
        """
        Writes a single byte value to a specified register.
        
        :param addr: The register address.
        :param val: The value to write.
        """
        self.spi.writebytes([((addr << 1) & 0x7E), val])

    def _read_reg(self, addr: int) -> int:
        """
        Reads a single byte value from a specified register.
        
        :param addr: The register address.
        :return: The byte value read from the register.
        """
        val = self.spi.xfer2([((addr << 1) & 0x7E) | 0x80, 0])
        return val[1]

    def _set_bit_mask(self, reg: int, mask: int) -> None:
        """
        Sets specific bits (defined by the mask) in a register to 1.
        
        :param reg: The register address.
        :param mask: The bitmask to set.
        """
        current_val = self._read_reg(reg)
        self._write_reg(reg, current_val | mask)

    def _clear_bit_mask(self, reg: int, mask: int) -> None:
        """
        Clears specific bits (defined by the mask) in a register to 0.
        
        :param reg: The register address.
        :param mask: The bitmask to clear.
        """
        current_val = self._read_reg(reg)
        self._write_reg(reg, current_val & (~mask))

    # --- Antenna Control ---

    def antenna_on(self) -> None:
        """
        Turns the antenna on. The antenna is used to communicate with the RFID tag.
        """
        temp = self._read_reg(self.TxControlReg)
        if not (temp & 0x03):
            self._set_bit_mask(self.TxControlReg, 0x03)

    def antenna_off(self) -> None:
        """
        Turns the antenna off.
        """
        self._clear_bit_mask(self.TxControlReg, 0x03)

    # --- Main Communication Logic ---

    def _to_card(self, command: int, send_data: List[int]) -> Tuple[int, List[int], int]:
        """
        The primary method for communicating with the RFID card.
        It sends a command and data, and waits for a response.
        
        :param command: The command to send (e.g., PCD_AUTHENT, PCD_TRANSCEIVE).
        :param send_data: A list of bytes to send to the card.
        :return: A tuple of (status, back_data, back_len).
                 - status: The status of the operation (MI_OK, MI_ERR).
                 - back_data: The data received from the card.
                 - back_len: The number of bits in the received data.
        """
        back_data = []
        back_len = 0
        status = self.MI_ERR
        irq_en = 0x00
        wait_irq = 0x00
        
        if command == self.PCD_AUTHENT:
            irq_en = 0x12
            wait_irq = 0x10
        elif command == self.PCD_TRANSCEIVE:
            irq_en = 0x77
            wait_irq = 0x30

        self._write_reg(self.CommIEnReg, irq_en | 0x80)
        self._clear_bit_mask(self.CommIrqReg, 0x80)
        self._set_bit_mask(self.FIFOLevelReg, 0x80)
        self._write_reg(self.CommandReg, self.PCD_IDLE)

        for byte in send_data:
            self._write_reg(self.FIFODataReg, byte)

        self._write_reg(self.CommandReg, command)

        if command == self.PCD_TRANSCEIVE:
            self._set_bit_mask(self.BitFramingReg, 0x80)

        # Wait for the command to complete
        i = 2000
        while True:
            n = self._read_reg(self.CommIrqReg)
            i -= 1
            if not (i != 0 and not (n & 0x01) and not (n & wait_irq)):
                break
        
        self._clear_bit_mask(self.BitFramingReg, 0x80)

        if i != 0:
            if (self._read_reg(self.ErrorReg) & 0x1B) == 0x00:
                status = self.MI_OK
                if n & irq_en & 0x01:
                    status = self.MI_NOTAGERR
                
                if command == self.PCD_TRANSCEIVE:
                    n = self._read_reg(self.FIFOLevelReg)
                    last_bits = self._read_reg(self.ControlReg) & 0x07
                    if last_bits != 0:
                        back_len = (n - 1) * 8 + last_bits
                    else:
                        back_len = n * 8
                    
                    if n == 0: n = 1
                    if n > self.MAX_LEN: n = self.MAX_LEN

                    for _ in range(n):
                        back_data.append(self._read_reg(self.FIFODataReg))
            else:
                status = self.MI_ERR
        
        return (status, back_data, back_len)

    def request(self, req_mode: int) -> Tuple[int, Optional[int]]:
        """
        Scans for nearby RFID tags.
        
        :param req_mode: The request mode (PICC_REQIDL for idle cards, PICC_REQALL for all cards).
        :return: A tuple of (status, back_bits).
                 - status: MI_OK if a card is found.
                 - back_bits: The card's type information.
        """
        self._write_reg(self.BitFramingReg, 0x07)
        (status, _, back_bits) = self._to_card(self.PCD_TRANSCEIVE, [req_mode])

        if status != self.MI_OK or back_bits != 0x10:
            status = self.MI_ERR

        return (status, back_bits)

    def _anticoll(self, anticoll_level: int) -> Tuple[int, List[int]]:
        """
        Performs an anti-collision loop to get the card's UID.
        
        :param anticoll_level: The anti-collision level (e.g., PICC_ANTICOLL1).
        :return: A tuple of (status, uid_data).
        """
        ser_num_check = 0
        ser_num = [anticoll_level, 0x20]

        self._write_reg(self.BitFramingReg, 0x00)
        (status, back_data, _) = self._to_card(self.PCD_TRANSCEIVE, ser_num)

        if status == self.MI_OK:
            if len(back_data) == 5:
                for i in range(4):
                    ser_num_check ^= back_data[i]
                if ser_num_check != back_data[4]:
                    status = self.MI_ERR
            else:
                status = self.MI_ERR
        
        return (status, back_data)

    def _calculate_crc(self, data: List[int]) -> List[int]:
        """
        Calculates the CRC (Cyclic Redundancy Check) for data.
        
        :param data: A list of bytes to calculate the CRC for.
        :return: A list containing the two CRC bytes.
        """
        self._clear_bit_mask(self.DivIrqReg, 0x04)
        self._set_bit_mask(self.FIFOLevelReg, 0x80)
        
        for byte in data:
            self._write_reg(self.FIFODataReg, byte)
            
        self._write_reg(self.CommandReg, self.PCD_CALCCRC)
        
        i = 0xFF
        while True:
            n = self._read_reg(self.DivIrqReg)
            i -= 1
            if not (i != 0 and not (n & 0x04)):
                break
                
        crc_result = [self._read_reg(self.CRCResultRegL), self._read_reg(self.CRCResultRegM)]
        return crc_result

    def select_tag_sn(self) -> Tuple[int, List[int]]:
        """
        Performs the complete anti-collision and selection process to get a card's UID.
        
        :return: A tuple of (status, uid).
                 - status: MI_OK on success.
                 - uid: A list of bytes representing the card's UID.
        """
        (status, uid_part1) = self._anticoll(self.PICC_ANTICOLL1)
        if status != self.MI_OK:
            return self.MI_ERR, []

        if self._pcd_select(uid_part1, self.PICC_ANTICOLL1) == 0:
            return self.MI_ERR, []

        # Some cards have longer UIDs and require multiple anti-collision steps
        if uid_part1[0] == 0x88:
            (status, uid_part2) = self._anticoll(self.PICC_ANTICOLL2)
            if status != self.MI_OK:
                return self.MI_ERR, []
            if self._pcd_select(uid_part2, self.PICC_ANTICOLL2) == 0:
                return self.MI_ERR, []
            
            # Cascade level 3
            if uid_part2[0] == 0x88:
                (status, uid_part3) = self._anticoll(self.PICC_ANTICOLL3)
                if status != self.MI_OK:
                    return self.MI_ERR, []
                if self._pcd_select(uid_part3, self.PICC_ANTICOLL3) == 0:
                    return self.MI_ERR, []
                # Combine all parts of the UID
                return self.MI_OK, uid_part1[1:4] + uid_part2[1:4] + uid_part3[0:4]
            else:
                # Combine two parts of the UID
                return self.MI_OK, uid_part1[1:4] + uid_part2[0:4]
        
        return self.MI_OK, uid_part1[0:4]

    def _pcd_select(self, ser_num: List[int], anticoll_level: int) -> int:
        """
        Selects a specific tag based on its serial number.
        
        :param ser_num: The serial number (UID) of the tag to select.
        :param anticoll_level: The anti-collision level used.
        :return: 1 if selection was successful, 0 otherwise.
        """
        buf = [anticoll_level, 0x70] + ser_num
        crc = self._calculate_crc(buf)
        buf += crc

        (status, back_data, back_len) = self._to_card(self.PCD_TRANSCEIVE, buf)
        
        return 1 if (status == self.MI_OK) and (back_len == 0x18) else 0

    def auth(self, auth_mode: int, block_addr: int, key: List[int], ser_num: List[int]) -> int:
        """
        Authenticates a block on the card. This is required before reading or writing.
        
        :param auth_mode: The authentication mode (PICC_AUTHENT1A or PICC_AUTHENT1B).
        :param block_addr: The block address to authenticate.
        :param key: The authentication key (a list of 6 bytes).
        :param ser_num: The card's serial number (UID).
        :return: The status of the authentication (MI_OK on success).
        """
        buff = [auth_mode, block_addr] + key + ser_num[:4]
        (status, _, _) = self._to_card(self.PCD_AUTHENT, buff)
        return status

    def stop_crypto1(self) -> None:
        """
        Stops the CRYPTO1 encryption. This should be called after an authenticated operation.
        """
        self._clear_bit_mask(self.Status2Reg, 0x08)

    def read(self, block_addr: int) -> Tuple[int, Optional[List[int]]]:
        """
        Reads 16 bytes from a specified block on the card.
        
        :param block_addr: The block number to read from.
        :return: A tuple of (status, data).
                 - status: MI_OK on success.
                 - data: A list of 16 bytes read from the block, or None on failure.
        """
        recv_data = [self.PICC_READ, block_addr]
        crc = self._calculate_crc(recv_data)
        recv_data += crc

        (status, back_data, _) = self._to_card(self.PCD_TRANSCEIVE, recv_data)
        
        if status != self.MI_OK:
            return status, None
        
        return (status, back_data) if len(back_data) == 16 else (self.MI_ERR, None)

    def write(self, block_addr: int, write_data: List[int]) -> int:
        """
        Writes 16 bytes to a specified block on the card.
        
        :param block_addr: The block number to write to.
        :param write_data: A list of 16 bytes to write to the block.
        :return: The status of the write operation (MI_OK on success).
        """
        buff = [self.PICC_WRITE, block_addr]
        crc = self._calculate_crc(buff)
        buff += crc

        (status, back_data, back_len) = self._to_card(self.PCD_TRANSCEIVE, buff)
        if not (status == self.MI_OK and back_len == 4 and (back_data[0] & 0x0F) == 0x0A):
            status = self.MI_ERR

        if status == self.MI_OK:
            buf_data = write_data
            crc = self._calculate_crc(buf_data)
            buf_data += crc
            (status, back_data, back_len) = self._to_card(self.PCD_TRANSCEIVE, buf_data)
            if not (status == self.MI_OK and back_len == 4 and (back_data[0] & 0x0F) == 0x0A):
                status = self.MI_ERR
        
        return status

    def init(self) -> None:
        """
        Initializes the MFRC522 chip with default settings.
        """
        self.reset()
        self._write_reg(self.TModeReg, 0x8D)
        self._write_reg(self.TPrescalerReg, 0x3E)
        self._write_reg(self.TReloadRegL, 30)
        self._write_reg(self.TReloadRegH, 0)
        self._write_reg(self.TxAutoReg, 0x40)
        self._write_reg(self.ModeReg, 0x3D)
        self.antenna_on()
        
    def reset(self) -> None:
        """
        Resets the MFRC522 chip by sending the soft reset command.
        """
        self._write_reg(self.CommandReg, self.PCD_RESETPHASE)

    # --- Backward Compatibility Aliases ---
    # These methods are kept for compatibility with older scripts but are deprecated.
    # It is recommended to use the new snake_case method names.

    def MFRC522_Init(self) -> None:
        """DEPRECATED: Use init() instead."""
        self.init()

    def MFRC522_Reset(self) -> None:
        """DEPRECATED: Use reset() instead."""
        self.reset()

    def Write_MFRC522(self, addr: int, val: int) -> None:
        """DEPRECATED: Use _write_reg() instead."""
        self._write_reg(addr, val)

    def Read_MFRC522(self, addr: int) -> int:
        """DEPRECATED: Use _read_reg() instead."""
        return self._read_reg(addr)

    def SetBitMask(self, reg: int, mask: int) -> None:
        """DEPRECATED: Use _set_bit_mask() instead."""
        self._set_bit_mask(reg, mask)

    def ClearBitMask(self, reg: int, mask: int) -> None:
        """DEPRECATED: Use _clear_bit_mask() instead."""
        self._clear_bit_mask(reg, mask)

    def AntennaOn(self) -> None:
        """DEPRECATED: Use antenna_on() instead."""
        self.antenna_on()

    def AntennaOff(self) -> None:
        """DEPRECATED: Use antenna_off() instead."""
        self.antenna_off()

    def MFRC522_ToCard(self, command: int, send_data: List[int]) -> Tuple[int, List[int], int]:
        """DEPRECATED: Use _to_card() instead."""
        return self._to_card(command, send_data)

    def MFRC522_Request(self, req_mode: int) -> Tuple[int, Optional[int]]:
        """DEPRECATED: Use request() instead."""
        return self.request(req_mode)

    def MFRC522_Anticoll(self, anticoll_level: int) -> Tuple[int, List[int]]:
        """DEPRECATED: Use _anticoll() instead."""
        return self._anticoll(anticoll_level)

    def CalculateCRC(self, data: List[int]) -> List[int]:
        """DEPRECATED: Use _calculate_crc() instead."""
        return self._calculate_crc(data)

    def MFRC522_SelectTagSN(self) -> Tuple[int, List[int]]:
        """DEPRECATED: Use select_tag_sn() instead."""
        return self.select_tag_sn()
        
    def MFRC522_Auth(self, auth_mode: int, block_addr: int, key: List[int], ser_num: List[int]) -> int:
        """DEPRECATED: Use auth() instead."""
        return self.auth(auth_mode, block_addr, key, ser_num)

    def MFRC522_StopCrypto1(self) -> None:
        """DEPRECATED: Use stop_crypto1() instead."""
        self.stop_crypto1()

    def MFRC522_Read(self, block_addr: int) -> Tuple[int, Optional[List[int]]]:
        """DEPRECATED: Use read() instead."""
        return self.read(block_addr)

    def MFRC522_Write(self, block_addr: int, write_data: List[int]) -> int:
        """DEPRECATED: Use write() instead."""
        return self.write(block_addr, write_data)
