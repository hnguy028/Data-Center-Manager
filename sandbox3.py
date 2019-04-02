##
#   Tree Widget Demo - with check boxes
##

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sys


def main():
    app     = QApplication (sys.argv)
    tree    = QTreeWidget ()
    headerItem  = QTreeWidgetItem()
    item    = QTreeWidgetItem()

    for i in range(3):
        parent = QTreeWidgetItem(tree)
        parent.setText(0, "Parent {}".format(i))
        parent.setFlags(parent.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
        for x in range(5):
            child = QTreeWidgetItem(parent)
            child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
            child.setText(0, "Child {}".format(x))
            child.setCheckState(0, Qt.Unchecked)
    tree.show()

    root = tree.invisibleRootItem()
    print(root.childCount())

    iterator = QTreeWidgetItemIterator(tree)

    while iterator.value():
        item = iterator.value()
        print(item.text(1))
        # if item.text() == "someText"  # check value here
        #     item.setText(column, "text")  # set text here
        iterator += 1

    sys.exit(app.exec_())


def test(n):
    print("Checked:" + n)


if __name__ == '__main__':
    main()