import math
from decimal import Decimal # This is the library used for long decimals

class AdaptiveModelGeneral: # This is the model and the class that keeps track of the CDF and the counts to update them
    def __init__(self, unique_symbols): #The unique symbols of the input is a parameter
        self.symbols = sorted(list(unique_symbols))
        self.counts = {sym: 1 for sym in self.symbols} # Creates the dictionary for character mapping to counts
        self.total_count = len(self.symbols)

    def get_symbol_range(self, symbol): # this is responsible for getting the range of a symbol and the cummulative counts
        current_cumulative_count = 0
        for s in self.symbols:
            if s == symbol: #loops untill it finds the symbol in order
                return (Decimal(current_cumulative_count) / Decimal(self.total_count), 
                        Decimal(current_cumulative_count + self.counts[s]) / Decimal(self.total_count)) #Returns the upper and lower bounds as Decimals
            current_cumulative_count += self.counts[s]
        raise ValueError("Symbol not in alphabet")

    def get_symbol_from_probability(self, prob_value): # Given a probability value, find the corresponding symbol, this is used in decoding.
        current_cumulative_count = 0
        for s in self.symbols:
            low_prob = Decimal(current_cumulative_count) / Decimal(self.total_count)
            high_prob = Decimal(current_cumulative_count + self.counts[s]) / Decimal(self.total_count)
            if low_prob <= prob_value < high_prob: # if the prob is in this range for this character then decide in favor of this character
                return s, low_prob, high_prob
            current_cumulative_count += self.counts[s]
        return self.symbols[-1], low_prob, Decimal(1) # Fallback to the last symbol, should not normally reach here.

    def update(self, symbol):  # Updates the counts after each symbol is processed either for encoding or decoding
        self.counts[symbol] += 1
        self.total_count += 1

class ArithmeticEncoder: # the main encoder class 
    def __init__(self):
        self.low = Decimal(0) # Initialize low and high as Decimals for precision
        self.high = Decimal(1)
        
    def encode(self, sequence, model):
        for char in sequence: # For each character in the input sequence
            current_range = self.high - self.low # Calculate the current range
            sym_low, sym_high = model.get_symbol_range(char) # Get the symbol CDF from the model that we explored earlier
            self.high = self.low + (current_range * sym_high) # Update high and low based on the symbol CDF
            self.low = self.low + (current_range * sym_low)
            model.update(char)
        return self.low, self.high

class ArithmeticDecoder: # The main decoder class
    def __init__(self, encoded_decimal_value, message_length):
        self.value = encoded_decimal_value # The decimal value to decode
        self.low = Decimal(0)
        self.high = Decimal(1)
        self.message_length = message_length # Length of the original message to decode just to know when to stop.
        self.decoded_sequence = []  # Store decoded symbols here

    def decode(self, model):
        for _ in range(self.message_length): #this is simply the reverse of the encoding process but it stops when the message length is reached
            current_range = self.high - self.low
            scaled_value = (self.value - self.low) / current_range
            symbol, sym_low, sym_high = model.get_symbol_from_probability(scaled_value) # Get the symbol corresponding to the scaled value for be the decoded symbol
            self.decoded_sequence.append(symbol)
            self.high = self.low + (current_range * sym_high)
            self.low = self.low + (current_range * sym_low)
            model.update(symbol) # Update the model after decoding each symbol
        return "".join(self.decoded_sequence)

def finish_encoding(low, high): # This function converts the final low and high into a binary string
    width = high - low #this width corresponds to the probability of the sequence
    if width == 0: return ""
    bits_needed = math.ceil(- (width.ln() / Decimal(2).ln())) + 1 # ceil(-log2(width)) + 1
    midpoint = (low + high) / Decimal(2)
    
    binary_output = []
    value = midpoint
    for _ in range(bits_needed):  # this is just converting the decimal value to binary even with a simple algorithm as we learned
        value *= 2
        if value >= 1:
            binary_output.append("1")
            value -= 1
        else:
            binary_output.append("0")
    return "".join(binary_output)

def binary_to_decimal(binary_string): #binary string to decimal conversion for the decoder
    value = Decimal(0)
    power = Decimal(1)/Decimal(2)
    for bit in binary_string:
        if bit == '1': value += power
        power /= 2
    return value