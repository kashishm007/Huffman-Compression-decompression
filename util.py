# --------------------------------------------
#   Name: Kashish Mittal
#   ID: 1638174
#   CMPUT 274, Fall 2020
#
#   Assignment 2: Huffman Coding
# --------------------------------------------
import bitio
import huffman
import pickle


def read_tree(tree_stream):
    """Read a description of a Huffman tree from the given compressed
    tree stream, and use the pickle module to construct the tree object.
    Then, return the root node of the tree itself.

    Args:
      tree_stream: The compressed stream to read the tree from.

    Returns:
      A Huffman tree root constructed according to the given description.
    """
    tree = pickle.load(tree_stream)
    return tree


def decode_byte(tree, bitreader):
    """
    Reads bits from the bit reader and traverses the tree from
    the root to a leaf. Once a leaf is reached, bits are no longer read
    and the value of that leaf is returned.

    Args:
      bitreader: An instance of bitio.BitReader to read the tree from.
      tree: A Huffman tree.

    Returns:
      Next byte of the compressed bit stream.
    """
    # Run while loop until the tree becomes of class TreeLeaf
    while not isinstance(tree, huffman.TreeLeaf):
        # read bit by bit from the bitreader using readbit
        bit = bitreader.readbit()
        # if bit is 1 we go to right branch of the tree
        if bit:
            tree = tree.getRight()
        # else we go to left branch of the tree
        else:
            tree = tree.getLeft()
    # Once we reach a tree with no branches i.e. a tree leaf we return the
    # value
    return tree.getValue()


def decompress(compressed, uncompressed):
    """First, read a Huffman tree from the 'compressed' stream using your
    read_tree function. Then use that tree to decode the rest of the
    stream and write the resulting symbols to the 'uncompressed'
    stream.

    Args:
      compressed: A file stream from which compressed input is read.
      uncompressed: A writable file stream to which the uncompressed
          output is written.
    """
    # Read a tree from the given compressed stream
    tree = read_tree(compressed)
    # Read the compressed stream
    bitreader = bitio.BitReader(compressed)
    # To write on the uncompressed stream
    bitwriter = bitio.BitWriter(uncompressed)
    # get the first value from the tree
    tree_value = decode_byte(tree, bitreader)
    # While loop runs until the tree value becomes none i.e. until we reach the
    # end of file
    while tree_value is not None:
        try:
            # writing on the uncompressed file 8 bits at a time
            bitwriter.writebits(tree_value, 8)
            # Getting the next value from the tree
            tree_value = decode_byte(tree, bitreader)
        except EOFError:
            tree_value = None
    # after writing everything on the uncompressed file we call flush to
    # account for any partially written bytes
    bitwriter.flush()


def write_tree(tree, tree_stream):
    """Write the specified Huffman tree to the given tree_stream
    using pickle.

    Args:
      tree: A Huffman tree.
      tree_stream: The binary file to write the tree to.
    """
    pickle.dump(tree, tree_stream)


def compress(tree, uncompressed, compressed):
    """First write the given tree to the stream 'compressed' using the
    write_tree function. Then use the same tree to encode the data
    from the input stream 'uncompressed' and write it to 'compressed'.
    If there are any partially-written bytes remaining at the end,
    write 0 bits to form a complete byte.

    Flush the bitwriter after writing the entire compressed file.

    Args:
      tree: A Huffman tree.
      uncompressed: A file stream from which you can read the input.
      compressed: A file stream that will receive the tree description
          and the coded input data.
    """
    # writing the tree on the compressed file
    write_tree(tree, compressed)
    # read the uncompressed stream
    bitreader = bitio.BitReader(uncompressed)
    # to write on the compressed stream
    bitwriter = bitio.BitWriter(compressed)
    # making encoding table from the given tree
    encoding_table = huffman.make_encoding_table(tree)
    # reading byte by byte(8 bits at a time)
    byte = bitreader.readbits(8)
    # runs the loop until byte is None
    while byte is not None:
        # using try and except to account for end of file error
        try:
            # get the corresponding value of the key = byte from the
            # dictionary encoding table
            value = encoding_table[byte]
            # then we use a for loop to get each bit from the tuple 'value'
            # and then use writebit to write that bit on the compressed stream
            for i in value:
                bitwriter.writebit(i)
            # reading in the next byte
            byte = bitreader.readbits(8)
        # when we get an end of file error we set the byte to None to get
        # out of the while loop
        except EOFError:
            byte = None
    # then we get the value for the key = byte where byte is None from
    # the dictionary encoding_table
    EOF = encoding_table[byte]
    for i in EOF:
        bitwriter.writebit(i)
    # after writing everything on the compressed file we call flush to account
    # for any partially written bytes
    bitwriter.flush()
