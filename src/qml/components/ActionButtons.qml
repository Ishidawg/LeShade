import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as Controls

RowLayout {
    id: root

    signal backClicked
    signal nextClicked

    property alias nextButton: nextBtn
    property alias backButton: backBtn

    Controls.Button {
        id: backBtn
        text: qsTr("Back")
        onClicked: root.backClicked()
    }
    Controls.Button {
        id: nextBtn
        text: qsTr("Next")
        onClicked: root.nextClicked()
    }
}
