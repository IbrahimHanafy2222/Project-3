import math

def lz78_encode(text):
    # Scan text to determine unique characters
    unique_chars = sorted(list(set(text)), reverse=True)

    alphabet_map = {char: i for i, char in enumerate(unique_chars)}
    num_unique = len(unique_chars)  # Count of unique characters
    
    # This is for the y part in the mx+y max function
    if num_unique > 1:
        char_bits = math.ceil(math.log2(num_unique))
    else:
        char_bits = 1 
        
    dictionary = {"": 0} #Initialize dictionary
    current_phrase = "" 
    output_tuples = []
    
    
    for char in text:
        combined = current_phrase + char #checks if the current phrase plus the new character is in the dictionary
        if combined in dictionary:
            current_phrase = combined #if it is, continue building the phrase
        else:
            idx = dictionary[current_phrase] #get the index of the current phrase
            output_tuples.append((idx, char)) #append the new tuple
            dictionary[combined] = len(dictionary) #add the new phrase to the dictionary to get its index
            current_phrase = ""#reset current phrase
            
    if current_phrase: #if there's any remaining phrase at the end, output it with an empty character
        idx = dictionary[current_phrase]
        output_tuples.append((idx, ""))

    # Binary Generation Phase
    binary_output = ""
    current_dict_size = 1 
    
    for i, (idx, char) in enumerate(output_tuples):
# calculates the m in the mx + y max function
        if current_dict_size > 1:
            index_bits = math.ceil(math.log2(current_dict_size))
        else:
            index_bits = 0
            
        if index_bits > 0:
            # CHECK: Is this the last token and does it have no character?
            if i == len(output_tuples) - 1 and char == "":
                # OPTIMIZATION: Output minimal bits for the final index
                # '1' -> '1', '3' -> '11'. No leading zeros.
                idx_bin = format(idx, 'b') 
            else:
                # Standard Case: Pad with zeros to fit dictionary width
                idx_bin = format(idx, f'0{index_bits}b')
                
            binary_output += idx_bin
        
        # Write Character
        if char:
            char_code = alphabet_map[char] #get character code from alphabet map
            char_bin = format(char_code, f'0{char_bits}b') #convert character code to binary with padding
            binary_output += char_bin #append character bits
            current_dict_size += 1 #increment dictionary size
        else:
            pass

    # Return alphabet string joined (Decoder needs to reconstruct map)
    alphabet_str = "".join(unique_chars)
    return binary_output, alphabet_str

def lz78_decode(binary_data, alphabet):
    # This is for the y part in the mx+y max function
    num_unique = len(alphabet)
    if num_unique > 1:
        char_bits = math.ceil(math.log2(num_unique))
    else:
        char_bits = 1
        
    dictionary = [""]
    output = []
    
    current_dict_size = 1
    i = 0
    
    while i < len(binary_data):
# calculates the m in the mx + y max function
        if current_dict_size > 1:
            index_bits = math.ceil(math.log2(current_dict_size))
        else:
            index_bits = 0
            
        if index_bits > 0:
            if i + index_bits > len(binary_data): #checks for final index-only case if it goes out of bounds
                idx_part = binary_data[i:] # Read whatever is left
                if idx_part:        
                    idx = int(idx_part, 2)  # Convert to integer
                    if idx < len(dictionary): #
                        output.append(dictionary[idx])
                break  # Exit loop after processing final index-only token
                
            idx_part = binary_data[i : i + index_bits] #if availabke ,read the full index bits
            idx = int(idx_part, 2)# Convert to integer
            i += index_bits # Move index forward by the number of bits read
        else:
            idx = 0     # If no index bits, index is always 0
            
        if i + char_bits <= len(binary_data): # checks if there are enough bits left for a character
            char_part = binary_data[i : i + char_bits] # Read character bits
            char_code = int(char_part, 2)# Convert to integer
            
            if char_code < len(alphabet): #checks if character code is valid
                char = alphabet[char_code] # Get character from alphabet
            else:
                char = "?" # Fallback for invalid character codes
                
            if idx < len(dictionary):
                phrase = dictionary[idx] + char
            else:
                phrase = ""
                
            output.append(phrase)
            dictionary.append(phrase)
            current_dict_size += 1
            i += char_bits
        else:
            if idx < len(dictionary): # Final case: index with no character
                phrase = dictionary[idx] #append phrase
            else:
                phrase = ""# Fallback for invalid index
            output.append(phrase)
            break
        
    return "".join(output)