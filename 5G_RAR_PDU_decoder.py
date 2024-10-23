MAX_PREAMBLE_ID = 64

# Initialize g_si_configured_rapid similar to the C code
g_si_configured_rapid = [64] * MAX_PREAMBLE_ID

def rapid_only(rapid):
    """
    Check if the given RAPID is configured for SI (System Information) acknowledgment.
    Returns True if it is, otherwise False.
    """
    return rapid in g_si_configured_rapid

def decode_rar(rar_buf):
    """
    Decodes the Random Access Response (RAR) buffer in a 5G scenario.
    """
    offset = 0
    while True:
        # Find E-bit to check if there are more MAC subheaders
        e_bit = rar_buf[offset] & 0x80

        # Find T-bit to differentiate between BI and RAPID
        t_bit = rar_buf[offset] & 0x40

        if t_bit:
            # This is a RAPID subheader
            rapid = rar_buf[offset] & 0x3F
            offset += 1
        else:
            # This is a BI subheader
            bi = rar_buf[offset] & 0x0F
            print(f"\nBackoff indicator is included; BI value is: {bi}")
            offset += 1
            if e_bit:
                continue
            else:
                break

        # Check if the RAPID is only subheader (no corresponding MAC RAR)
        if rapid_only(rapid):
            print(f"\nThis subheader is a RAPID ONLY subheader, No corresponding MAC RAR exists for RAPID: {rapid}")
            if e_bit:
                continue
            else:
                break

        # If we reach this point, it is a RAPID with a MAC RAR
        timing_advance = 0
        for _ in range(2):
            timing_advance = (timing_advance << 8) | rar_buf[offset]
            offset += 1
        timing_advance &= 0x7FF8

        ul_grant = 0
        for _ in range(4):
            ul_grant = (ul_grant << 8) | rar_buf[offset]
            offset += 1
        ul_grant &= 0x07FFFFFF  # Not decoding UL grant further

        tc_rnti = 0
        for _ in range(2):
            tc_rnti = (tc_rnti << 8) | rar_buf[offset]
            offset += 1

        # Print the decoded information
        print("\n===========================================================================")
        print(f"MAC RAR decoded for RAPID: {rapid}")
        print(f"TIMING Advance: {timing_advance}")
        print(f"UL grant: {ul_grant}")
        print(f"TC-RNTI: {tc_rnti}")
        print("===========================================================================")

        # Reset values for next potential loop iteration
        timing_advance = 0
        ul_grant = 0
        tc_rnti = 0

        # If E-bit is set, continue to decode more subheaders
        if e_bit:
            continue
        else:
            break

def main():
    """
    Main function to handle initialization and RAR decoding.
    """
    # Example RAR buffer in a 5G scenario
    rar_buf = [0x4f, 0x00, 0x01, 0xf5, 0x1c, 0xff, 0x00, 0xf2, 0x00]
    
    # Start the decoding process
    decode_rar(rar_buf)

# Entry point of the Python program
if __name__ == "__main__":
    main()
    input("Press Enter to exit....")
