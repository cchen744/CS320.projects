class Node():
    def __init__(self, key):
        self.key = key
        self.values = []
        self.left = None
        self.right = None
        
    def __len__(self):
        size = len(self.values)
        if self.left != None:
            size += self.left.__len__()
        if self.right != None:
            size += self.right.__len__()
        return size
    
    def lookup(self,key):
        if key==self.key:
            return self.values
        if key < self.key and self.left != None:
            return self.left.lookup(key)
        if key > self.key and self.right != None:
            return self.right.lookup(key)
        return []
    
    def height(self):
        if self.left != None:
            l=self.left.height()
        else:
            l=0
        if self.right != None:
            r=self.right.height()
        else:
            r=0
        return max(l,r)+1
    
    def count_leaf(self):
        
        if self.left == None and self.right == None:
            return 1
        
        count = 0
        if self.left:
            count += self.left.count_leaf()
        if self.right:
            count += self.right.count_leaf()
        
        return count
    
    def top_n_rate(self,n):
        result = []
        
        def reverse_inorder_traversal(node):
            if node==None or len(result) >= n:
                return
            
            reverse_inorder_traversal(node.right)
            
            if len(result) < n:
                result.append(node.key)
                
            reverse_inorder_traversal(node.left)
            
        reverse_inorder_traversal(self)
        return result
                
            
            

class BST():
    def __init__(self):
        self.root = None

    def add(self, key, val):
        if self.root == None:
            self.root = Node(key) #self.root belongs to class Node().

        curr = self.root
        while True:
            if key < curr.key:
                # go left
                if curr.left == None:
                    curr.left = Node(key)
                curr = curr.left
            elif key > curr.key:
                 # go right
                if curr.right == None:
                    curr.right = Node(key)
                curr = curr.right
            else:
                # found it!
                assert curr.key == key
                break

        curr.values.append(val)
        
    def __dump(self, node):
        if node == None:
            return
        self.__dump(node.right)            # 1
        print(node.key, ":", node.values)  # 2
        self.__dump(node.left)             # 3

    
    def dump(self):
        self.__dump(self.root)
        
    def __getitem__(self, key):
        if self.root is None:
            return []
        return self.root.lookup(key)
    
    def height(self):
        return self.root.height()-1
    
    def count_leaf(self):
        return self.root.count_leaf()
    
    def nth_largest_rate(self,n):
        return self.root.top_n_rate(n)[-1]
        