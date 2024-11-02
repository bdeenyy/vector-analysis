class VectorData:
    def __init__(self, name="", length1=0.0, length2=0.0, length3=0.0):
        """
        Initialize a VectorData object

        Args:
            name (str): Name or identifier of the vector
            length1 (float): Length of first vector
            length2 (float): Length of second vector
            length3 (float): Length of third vector
        """
        self.name = name
        self.length1 = length1
        self.length2 = length2
        self.length3 = length3

    def __str__(self):
        """String representation of the vector data"""
        return f"Vector {self.name}: ({self.length1}, {self.length2}, {self.length3})"

    def as_list(self):
        """Return vector lengths as list"""
        return [self.length1, self.length2, self.length3]

    def from_dict(self, data_dict):
        """
        Update vector data from dictionary

        Args:
            data_dict (dict): Dictionary with keys 'name', 'length1', 'length2', 'length3'
        """
        self.name = data_dict.get('name', '')
        self.length1 = float(data_dict.get('length1', 0))
        self.length2 = float(data_dict.get('length2', 0))
        self.length3 = float(data_dict.get('length3', 0))