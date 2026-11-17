import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as Controls

RowLayout {
    id: root

    signal backClicked
    signal nextClicked

    Controls.Button {
        text: qsTr("Back")
        onClicked: root.backClicked()
    }
    Controls.Button {
        text: qsTr("Next")
        onClicked: root.nextClicked()
    }
}
