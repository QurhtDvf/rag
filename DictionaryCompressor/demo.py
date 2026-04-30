
from compressor import DictionaryCompressor

# Example usage 1
text_to_compress_1 = "abracadabraabracadabra"
K_value_1 = 5 # Number of rules to create

print("--- First Example ---")
compressor_1 = DictionaryCompressor()
compressed_grammar_1, start_symbol_1 = compressor_1.compress(text_to_compress_1, K_value_1)

print(f"Original text: {text_to_compress_1}")
print(f"Target grammar size (K): {K_value_1}")
print("\nCompressed Grammar:")
for nt, rhs in compressed_grammar_1.items():
    print(f"  {nt} -> {''.join(rhs)}")

decompressed_text_1 = compressor_1.decompress(compressed_grammar_1, start_symbol_1)
print(f"\nDecompressed text: {decompressed_text_1}")

if text_to_compress_1 == decompressed_text_1:
    print("\nCompression and decompression successful!")
else:
    print("\nError: Decompressed text does not match original!")

# Example usage 2
text_to_compress_2 = "banana"
K_value_2 = 2

print("\n--- Second Example ---")
compressor_2 = DictionaryCompressor()
compressed_grammar_2, start_symbol_2 = compressor_2.compress(text_to_compress_2, K_value_2)

print(f"Original text: {text_to_compress_2}")
print(f"Target grammar size (K): {K_value_2}")
print("\nCompressed Grammar:")
for nt, rhs in compressed_grammar_2.items():
    print(f"  {nt} -> {''.join(rhs)}")

decompressed_text_2 = compressor_2.decompress(compressed_grammar_2, start_symbol_2)
print(f"\nDecompressed text: {decompressed_text_2}")

if text_to_compress_2 == decompressed_text_2:
    print("\nCompression and decompression successful for second example!")
else:
    print("\nError: Decompressed text does not match original for second example!")

# Example usage 3
text_to_compress_3 = "aaaaabbbbbaaaaabbbbb"
K_value_3 = 3

print("\n--- Third Example ---")
compressor_3 = DictionaryCompressor()
compressed_grammar_3, start_symbol_3 = compressor_3.compress(text_to_compress_3, K_value_3)

print(f"Original text: {text_to_compress_3}")
print(f"Target grammar size (K): {K_value_3}")
print("\nCompressed Grammar:")
for nt, rhs in compressed_grammar_3.items():
    print(f"  {nt} -> {''.join(rhs)}")

decompressed_text_3 = compressor_3.decompress(compressed_grammar_3, start_symbol_3)
print(f"\nDecompressed text: {decompressed_text_3}")

if text_to_compress_3 == decompressed_text_3:
    print("\nCompression and decompression successful for third example!")
else:
    print("\nError: Decompressed text does not match original for third example!")
