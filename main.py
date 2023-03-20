import os
import struct

#cubos OLAP = molap / rolap
#cubos OLTP

class DiskNode:
    def __init__(self, key, value, height, left_address, right_address):
        self.key = key
        self.value = value
        self.height = height
        self.left_address = left_address
        self.right_address = right_address

class DiskBasedAVLTree:
    def __init__(self, file_name):
        self.file_name = file_name
        self.node_struct = struct.Struct("i i i q q")  # key, value_length, height, left_address, right_address
        self.node_size = self.node_struct.size

        if not os.path.exists(file_name):
            with open(file_name, "wb") as f:
                f.write(struct.pack("q", -1))  # Write the root address as -1 (empty tree)

        with open(file_name, "rb") as f:
            self.root_address, = struct.unpack("q", f.read(8))
          
    def search(self, key):
        return self._search(self.root_address, key)
    
    def _search(self, node_address, key):
        if node_address == -1:
            return None

        node = self._read_node(node_address)
        print(f"Current node key: {node.key}, address: {node_address}")  # Add this line for debugging

        if key < node.key:
            return self._search(node.left_address, key)
        elif key > node.key:
            return self._search(node.right_address, key)
        else:
            return node

    def insert(self, key, value):
        self.root_address = self._insert(self.root_address, key, value)
        with open(self.file_name, "r+b") as f:
            f.seek(0)
            f.write(struct.pack("q", self.root_address))
      
    def _insert(self, node_address, key, value):
        if node_address == -1:
            new_node = DiskNode(key, value, 1, -1, -1)
            return self._allocate_node(new_node)
    
        node = self._read_node(node_address)
    
        if key < node.key:
            node.left_address = self._insert(node.left_address, key, value)
        elif key > node.key:
            node.right_address = self._insert(node.right_address, key, value)
        else:
            node.value = value  # Update the value if the key already exists
    
        node.height = 1 + max(self._height(node.left_address), self._height(node.right_address))
    
        balance_factor = self._balance_factor(node)
    
        if balance_factor > 1:
            if key < self._read_node(node.left_address).key:
                node_address = self._rotate_right(node_address)
            else:
                node.left_address = self._rotate_left(node.left_address)
                node_address = self._rotate_right(node_address)
    
        if balance_factor < -1:
            if key > self._read_node(node.right_address).key:
                node_address = self._rotate_left(node_address)
            else:
                node.right_address = self._rotate_right(node.right_address)
                node_address = self._rotate_left(node_address)
    
        # Update the node's left and right addresses after rotations
        node.left_address = self._read_node(node_address).left_address
        node.right_address = self._read_node(node_address).right_address
    
        self._write_node(node, node_address)
        return node_address
      
    def _read_node(self, address):
        with open(self.file_name, "rb") as f:
            f.seek(address)
            key, value_length, height, left_address, right_address = self.node_struct.unpack(f.read(self.node_size))
            value = f.read(value_length).decode()
            return DiskNode(key, value, height, left_address, right_address)

    def _write_node(self, node, address):
        with open(self.file_name, "r+b") as f:
            f.seek(address)
            value_encoded = node.value.encode()
            value_length = len(value_encoded)
            f.write(self.node_struct.pack(node.key, value_length, node.height, node.left_address, node.right_address))
            f.write(value_encoded)

    def _allocate_node(self, node):
        with open(self.file_name, "ab") as f:
            address = f.tell()
            value_encoded = node.value.encode()
            value_length = len(value_encoded)
            f.write(self.node_struct.pack(node.key, value_length, node.height, node.left_address, node.right_address))
            f.write(value_encoded)
            return address

    def _height(self, node_address):
        if node_address == -1:
            return 0
        return self._read_node(node_address).height

    def _balance_factor(self, node):
        return self._height(node.left_address) - self._height(node.right_address)

    def _rotate_left(self, node_address):
        node = self._read_node(node_address)
        new_root_address = node.right_address
        new_root = self._read_node(new_root_address)

        node.right_address = new_root.left_address
        new_root.left_address = node_address

        node.height = 1 + max(self._height(node.left_address), self._height(node.right_address))
        new_root.height = 1 + max(self._height(new_root.left_address), self._height(new_root.right_address))

        self._write_node(node, node_address)
        self._write_node(new_root, new_root_address)

        return new_root_address

    def _rotate_right(self, node_address):
        node = self._read_node(node_address)
        new_root_address = node.left_address
        new_root = self._read_node(new_root_address)

        node.left_address = new_root.right_address
        new_root.right_address = node_address

        node.height = 1 + max(self._height(node.left_address), self._height(node.right_address))
        new_root.height = 1 + max(self._height(new_root.left_address), self._height(new_root.right_address))

        self._write_node(node, node_address)
        self._write_node(new_root, new_root_address)

        return new_root_address

# Create an instance of DiskBasedAVLTree with a specified file name
tree = DiskBasedAVLTree("avl_tree_data.bin")

# Insert the tree
tree.insert(1, "3")
tree.insert(2, "2")
tree.insert(3, "4")

value = tree.search(0)

# PRINT
print("-----1")
for campo in dir(value):
    if not campo.startswith("__"):
        print(f"{campo}: {getattr(value, campo)}")

value = tree.search(1)

# PRINT
print("-----2")
for campo in dir(value):
    if not campo.startswith("__"):
        print(f"{campo}: {getattr(value, campo)}")
