import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as Controls
import org.kde.kirigami as Kirigami

Kirigami.AbstractCard {
  contentItem: Item {
    implicitWidth: delegateLayout.implicitWidth
    implicitHeight: delegateLayout.implicitHeight

    GridLayout {
      id: delegateLayout
      anchors {
        left: parent.left
        top: parent.top
        right: parent.right
      }

      columns: 2

      Kirigami.Heading {
        level: 2
        text: qsTr(title)
      }

      Controls.Button {
        Layout.alignment: Qt.AlignRight
        icon.name: "user-trash-symbolic"
        text: qsTr("Uninstall")
      }
    }
  }
}

