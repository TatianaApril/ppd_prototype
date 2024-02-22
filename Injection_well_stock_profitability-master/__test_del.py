import numpy as np

M = [[1, 1, 1, 1, 1, 1],
     [1, 1, 1, 1, 1, 1],
     [1, 1, 1, 1, 1, 1],
     [1, 1, 1, 1, 1, 1],
     [1, 1, 1, 1, 1, 1],
     [1, 1, 1, 1, 1, 1]]

def counter(M):
    n = len(M) - 1
    j = n
    i = 0
    sum = 0
    iterator = 0
    while i <= n:
        while j >= 0:
            iterator += 1
            if M[i][j] == 1:
                sum += M[i][j]
                j = j - 1
            else:
                break
        i = i + 1
        j = n

    print(sum, iterator)

#counter(M)


class Box:
  def __init__(self, cat=None):
    self.cat = cat
    self.nextcat = None

class LinkedList:
    def __init__(self):
        self.head = None


    def del_doubles(self,):
        box = self.head

        while box.nextcat:
            next_box = box.nextcat
            if box.cat == next_box.cat:
                self.removeBox(next_box.cat)
                next_box = box.nextcat
            while next_box.nextcat:
                next_box = next_box.nextcat
                if box.cat == next_box.cat:
                    self.removeBox(next_box.cat)
                    next_box = box.nextcat
                else:
                    next_box = next_box.nextcat
        if not box.nextcat:
            return

    def removeBox(self, rmcat):
        headcat = self.head

        if headcat is not None:
            if headcat.cat == rmcat:
                self.head = headcat.nextcat
                headcat = None
                return
        while headcat is not None:
            if headcat.cat == rmcat:
                break
            lastcat = headcat
            headcat = headcat.nextcat
        if headcat == None:
            return
        lastcat.nextcat = headcat.nextcat
        headcat = None

    def addToEnd(self, newcat):
        newbox = Box(newcat)
        if self.head is None:
            self.head = newbox
            return
        lastbox = self.head
        while (lastbox.nextcat):
            lastbox = lastbox.nextcat
        lastbox.nextcat = newbox


box1 = Box(cat='grumpy')
box2 = Box(cat='silly')
box3 = Box(cat='happy')

llist = LinkedList()
llist.addToEnd('grumpy')
llist.addToEnd('silly')
llist.addToEnd('happy')

llist.del_doubles()


