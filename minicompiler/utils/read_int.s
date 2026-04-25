# This reads from a file as though it were standard in.
# Each call to read_int will read the next int from the given file.
# The file format must be one decimal integer per line.
# If an error is encountered the program exits (does not return).

.import berkeley_utils.s
.globl read_int     # make this visible to other files

.data
    error_string1: .string "read_int.s should not be run directly\n"
    error_string2: .string "incorrect number of bytes read\n"
    error_string3: .string "max bytes read with no newline\n"
    error_string4: .string "error closing file\n"
    read_int_seek: .word 0

.text
# Exits if you run this file
main:
    la a0 error_string1
    jal print_str
    li a0 1
    jal exit
# End main

read_int:
    # read_int(filepath_ptr) int:
    # args 
    #   a0 = pointer to filepath
    # return
    #   a0 = integer read
    #   a1 = error code (0: no error, 1: error)
     
   # Prologue
    addi sp sp -64
    sw ra 60(sp)
    sw s0 56(sp)    # s0 will hold num bytes read
    sw s1 52(sp)    # s1 will hold curr loc in buffer
    sw s2 48(sp)    # s2 will hold file descriptor
    sw s3 44(sp)    # s3 will hold integer to return

    addi s0 zero 0    # num bytes read so far
    mv s1 sp          # current loc in buffer
    addi a1 zero 0    # set file permission to read
    jal fopen
    mv s2 a0          # save file descriptor

    # Seek to the first unread byte by
    # (re)reading already-read bytes, putting them on the 
    # heap and immediately discarding heap space. 
    lw a0 read_int_seek     # num bytes read
    beq a0 zero start_loop  # no need to seek
    jal malloc
    sw s4 40(sp)
    mv s4 a0                # save malloc ptr
    mv a0 s2                # fd
    mv a1 s4                # buffer
    lw a2 read_int_seek     # number of bytes    
    jal fread
    mv a0 s4                # buffer
    jal free
    lw s4 40(sp)

start_loop:
    mv a0 s2
    mv a1 s1
    addi a2 zero 1
    jal fread         # read 1 byte

    addi t0 zero 1
    bne a0 t0 rd_err2       # check that requested bytes were read
    li t0 '\n'              
    lb a0 0(s1)
    beq a0 t0 post_loop     # check for newline

    addi s0 s0 1
    addi s1 s1 1
    addi t0 zero 11         # read at most 11 bytes
    beq s0 t0 of_err3       
    jal zero start_loop     

post_loop:

    mv a0 s2
    jal fclose
    bne a0 zero cl_err4
    li t0 0x00
    sw t0 0(s1)    # overwrite the newline with \0
    mv a0 sp       # translate buffer of ascii bytes to int
    jal atoi
    mv s3 a0

    # update read_int_seek
    lw t0 read_int_seek
    add t0 t0 s0
    addi t0 t0 1    # account for newline
    la t1 read_int_seek
    sw t0 0(t1)

    # Epilogue
    mv a0 s3        # integer to return
    addi a1 zero 0    # exit code 0

    lw ra 60(sp)
    lw s0 56(sp)    
    lw s1 52(sp)    
    lw s2 48(sp)    
    lw s3 44(sp)    
    addi sp sp 64

    jr ra
    #ret             # pseudo instruction for 'jalr zero ra 0'

rd_err2:
    la a0 error_string2
    jal print_str
    li a0 1
    jal exit

of_err3:
    la a0 error_string3
    jal print_str
    li a0 1
    jal exit

cl_err4:
    la a0 error_string4
    jal print_str
    li a0 1
    jal exit
